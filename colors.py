COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "gray": "\033[90m",
    "orange": "\033[38;5;208m",
}

RESET = "\033[0m"


def color_node(
    node_name: str,
    info: dict[str, dict[str, str]],
) -> str:
    color = info.get(node_name, {}).get("color")

    if color in COLORS:
        return f"{COLORS[color]}{node_name}{RESET}"

    return node_name
