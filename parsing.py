import re
import sys
from typing import Any, Literal


def make_a_dictionary() -> dict[str, list[Any]]:
    dic: dict[str, list[Any]] = {}
    check_prefix = 0
    with open("configuration.txt", "r") as file:
        lines = file.readlines()

        for line in lines:
            line = line.split('#')[0].strip()

            if not line:
                continue

            if ":" not in line:
                print("Enter key correctly")
                sys.exit()
            key, value = line.split(":", 1)
            key = key.lower().strip()
            if (
                key != "start_hub"
                and key != "end_hub"
                and key != "hub"
                and key != "connection"
                and key != "nb_drones"
            ):
                print("Enter key correctly")
                check_prefix += 1
                sys.exit()
            if check_prefix > 1:
                print("Enter key correctly")
                sys.exit()
            if key in dic:
                dic[key].append(value)
            else:
                dic[key] = [value]
    dic["prefix_v"] = [check_prefix]
    return dic


def check_connection(
    connection: list[str],
    names: list[str],
) -> dict[str, list[list[str | int]]] | Literal[False]:
    dic: dict[str, list[list[str | int]]] = {}
    dic = {}
    seen_connections = set()
    try:
        for x in connection:
            line = x.strip()
            if not line:
                continue
            if line.count('[') > 1 or line.count(']') > 1:
                raise ValueError("Invalid bracket structure in connection")
            attributes_part = ""

            if "[" in line or "]" in line:
                if not (line.endswith("]") and "[" in line):
                    raise ValueError(
                        "Attributes must be at the end enclosed in [...]")

                connection_part, attributes_part = line.split("[", 1)
                connection_part = connection_part.strip()
                attributes_part = attributes_part.rstrip("]").strip()
            else:
                connection_part = line
            parts = connection_part.split("-")
            if len(parts) != 2:
                raise ValueError("Connection must be in format: name1-name2")

            start, end = parts[0].strip(), parts[1].strip()

            if start not in names or end not in names:
                raise ValueError(
                    f"Unknown hub in connection: {connection_part}")

            if start == end:
                raise ValueError("A connection cannot connect a hub to itself")

            connection_key = tuple(sorted((start, end)))

            if connection_key in seen_connections:
                raise ValueError(f"Duplicate connection: {start}-{end}")

            seen_connections.add(connection_key)

            max_link_capacity = 1

            if attributes_part:
                if "=" not in attributes_part:
                    raise ValueError(
                        f"Invalid connection attribute: [{attributes_part}]")

                pairs = re.findall(r'(\w+)\s*=\s*([\w-]+)', attributes_part)

                if attributes_part.count('=') != len(pairs):
                    raise ValueError("Invalid metadata format in connection")
                clean_attr = re.sub(r'\s*=\s*', '=', attributes_part.strip())
                parsed_text = " ".join(
                    f"{k.strip()}={v.strip()}" for k, v in pairs)
                original_normalized = " ".join(clean_attr.split())

                if parsed_text.lower() != original_normalized.lower():
                    raise ValueError(
                        f"Invalid extra tokens or junk in metadata: "
                        f"[{attributes_part}]")

                for key, val in pairs:
                    key = key.lower().strip()
                    if key != "max_link_capacity":
                        raise ValueError(
                            f"Invalid connection attribute key: {key}")
                    try:
                        max_link_capacity = int(val)
                    except ValueError:
                        raise ValueError(
                            "max_link_capacity must be an integer")

                    if max_link_capacity <= 0:
                        raise ValueError(
                            "max_link_capacity must be greater than 0")

            dic.setdefault(start, []).append([end, max_link_capacity])
            dic.setdefault(end, []).append([start, max_link_capacity])

    except ValueError as e:
        print("Error", e)
        return False

    return dic


def check_start_end(start_hub: str) -> None:
    start_hub = " ".join(
        start_hub.replace("[", " [ ").replace("]", " ] ").split())
    arg = start_hub.split()
    lst_color = ["green", "yellow", "red", "blue", "gray"]
    try:
        if len(arg) < 3:
            raise ValueError("Missing name or coordinates")
        name = arg[0].strip().replace('"', '')
        if not name.replace('_', '').isalnum():
            raise ValueError("please inter name as string :)")
        elif "-" in name:
            raise ValueError("Don't write dashes on the name is forbids :)")
        # start = arg[1].strip().replace('"', '')
        # start = float(start)
        try:
            if arg[3] and "[" not in arg[3]:
                print(arg[3])
                raise ValueError("Don't write after les coordonnées :)")
        except ValueError as e:
            print("Error", e)
            sys.exit()
        # end = arg[2].strip().replace('"', '')
        # end = float(end)
        if (
            ("[" not in start_hub and "]" not in start_hub)
            or start_hub.count("[") > 1
            or start_hub.count("]") > 1
        ):
            raise ValueError("Please enter the form between [ ]")
        check = 0
        temp = ""
        for x in start_hub:
            if x == "[":
                check = 1
            elif x == "]":
                check = 0
            elif check:
                temp += x
        parts = temp.split("=")
        if len(parts) != 2:
            raise ValueError(
                "Please enter the form like that  metadata = value")
        if parts[0].lower().strip() == "color":
            value = parts[1].lower().strip()
            metadata = parts[0].lower().strip()
        else:
            raise ValueError("Please enter the color")
        if not isinstance(value, str) or not isinstance(metadata, str):
            raise ValueError("Enter the color and the value as string")
        if metadata != "color":
            raise ValueError("Please enter the color")

        if value not in lst_color:
            raise ValueError(f"Invalid color: {value}")
        index = start_hub.find(']')
        if index != -1 and start_hub[index+1:].strip():
            raise ValueError("Stop there: invalid trailing text after ']'")

    except ValueError as e:
        print('\033[91m', "Error", e, '\033[0m')
        sys.exit()


def check_hub(
    lines: list[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[list[str | int]]]] | bool:
    dic = make_a_dictionary()
    the_same_name = []
    dic_info = {}
    seen_coordinates = set()
    for key in ["start_hub", "end_hub"]:
        if key in dic:
            for entry in dic[key]:
                the_same_name.append(entry.strip().split()[0])

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            parts = re.findall(r'[^ \[]+|\[[^\]]*\]', line)
            if len(parts) > 4 or (len(parts) == 4 and "[" not in parts[3]):
                raise ValueError("Don't write anything after coordinates")
            if len(parts) < 3:
                raise ValueError(f"Missing information in hub: {line}")
            name = parts[0].strip()
            coordinates = (parts[1], parts[2])

            if coordinates in seen_coordinates:
                raise ValueError("Duplicate coordinates")

            seen_coordinates.add(coordinates)
            if "-" in name:
                raise ValueError("Don't write dashes on the name :)")
            if name in the_same_name:
                raise ValueError("don't use the same name")
            the_same_name.append(name)

            hub_data = {
                "name": name,
                "position": (parts[1], parts[2]),
                "zone": "normal", "color": "none", "max_drones": 1
            }
            if len(parts) > 3 and "[" in parts[3]:
                if parts[3].count("[") > 1 or parts[3].count("]") > 1:
                    raise ValueError("Inter just one like that [ ]")
                meta_content = parts[3].strip("[]")
                if ":" in meta_content:
                    raise ValueError(
                        f"Invalid character ':' in metadata: [{meta_content}]")
                if "=" not in meta_content:
                    raise ValueError(
                        "please write = like that: data = value")

                pairs = re.findall(r'(\w+)\s*=\s*([\w-]+)', meta_content)
                keys = [k.lower() for k, v in pairs]

                if len(keys) != len(set(keys)):
                    raise ValueError("Duplicate metadata key")

                if meta_content.count('=') != len(pairs):
                    raise ValueError(
                        f"Metadata syntax error in:"
                        f" [{meta_content}]. Check your '=' usage.")

                parsed_text = " ".join(f"{k}={v}" for k, v in pairs)
                original = re.sub(r'\s*=\s*', '=', meta_content.strip())

                if parsed_text != original:
                    raise ValueError(
                        "Invalid metadata syntax ... "
                    )
                valid_values = (
                    "priority",
                    "normal",
                    "blocked",
                    "restricted",
                )
                for k, v in pairs:
                    k = k.lower().strip()
                    v = v.lower().strip()
                    if k == "zone":
                        if v not in valid_values:
                            raise ValueError(f"Invalid zone type: {v}")
                        hub_data["zone"] = v
                    elif k == "color":
                        hub_data["color"] = v
                    elif k == "max_drones":
                        v_int = int(v)
                        if v_int <= 0:
                            raise ValueError("max_drones must be > 0")
                        hub_data["max_drones"] = v_int
                    else:
                        raise ValueError(
                            "Please write one of this zone or color ...")
            dic_info[name] = hub_data

        except ValueError as e:
            print("Error", e)
            return False
    connection = check_connection(dic["connection"], the_same_name)
    if connection is not False:
        return dic_info, connection
    else:
        return False


def check_validation() -> int | None:
    dic = make_a_dictionary()
    if dic["prefix_v"][0] > 0:
        print("Error")
        sys.exit()

    nb_drones_list = dic.get("nb_drones")
    start_hub = dic.get("start_hub")
    end_hub = dic.get("end_hub")
    hub = dic.get("hub")
    connection = dic.get("connection")
    try:
        if not nb_drones_list:
            raise ValueError("Missing nb_drones")

        if not start_hub:
            raise ValueError("Missing start_hub")

        if not end_hub:
            raise ValueError("Missing end_hub")

        if not hub:
            raise ValueError("Missing hub")

        if not connection:
            raise ValueError("Missing connection")
        nb_drones = int(''.join(nb_drones_list))
        if nb_drones < 0:
            raise ValueError("Number must of nb_drones be positive")
    except ValueError as e:
        print("Error", e)
        sys.exit()
    if len(dic["start_hub"]) > 1:
        print("You can't write start_hub more than one")
        sys.exit()
    if len(dic["nb_drones"]) > 1:
        print("You can't write nb_drones more than one")
        sys.exit()
    if len(dic["end_hub"]) > 1:
        print("You can't write end_hub more than one")
        sys.exit()

    start_hub = dic["start_hub"][0].strip()
    check_start_end(start_hub)
    end_hub = dic["end_hub"][0].strip()
    check_start_end(end_hub)
    info = check_hub(dic["hub"])
    if not info:
        return None
    return nb_drones
