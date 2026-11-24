import json
import subprocess


def workspace_windows(node, workspace=None):
    if node["type"] == "workspace":
        workspace = node["id"]
    if workspace is not None and node["window"] is not None:
        yield node, workspace
    for child in node["nodes"] + node["floating_nodes"]:
        yield from workspace_windows(child, workspace)


def get_windows():
    tree = json.loads(subprocess.check_output(["i3-msg", "-t", "get_tree"]))
    return {node["window"]: (node, workspace) for node, workspace in workspace_windows(tree)}


def inherit_layout(window, focused, windows):
    if window not in windows:
        return
    child, workspace = windows[window]
    properties = child["window_properties"]
    parent = properties.get("transient_for")
    source = parent if parent is not None else focused
    if source == window or source not in windows:
        return
    opener, opener_workspace = windows[source]

    # Normal windows (e.g. browser Ctrl+N) don't always identify their opener.
    if parent is None:
        window_class = properties.get("class")
        if not window_class or window_class != opener["window_properties"].get("class"):
            return
        if workspace != opener_workspace:
            return

    floating = opener["floating"].endswith("_on")
    if floating != child["floating"].endswith("_on"):
        mode = "enable" if floating else "disable"
        subprocess.run(["i3-msg", "-q", f'[con_id={child["id"]}] floating {mode}'])


def main():
    with subprocess.Popen(
        ["i3-msg", "-t", "subscribe", "-m", '["window"]'],
        stdout=subprocess.PIPE,
        text=True,
    ) as events:
        focused = next((node["window"] for node, _ in get_windows().values() if node["focused"]), None)
        # i3 reports window::new before window::focus for the new window.
        for line in events.stdout:
            event = json.loads(line)
            window = event["container"]["window"]
            if event["change"] == "new":
                inherit_layout(window, focused, get_windows())
            elif event["change"] == "focus":
                focused = window
            elif event["change"] == "close" and window == focused:
                focused = None


if __name__ == "__main__":
    main()
