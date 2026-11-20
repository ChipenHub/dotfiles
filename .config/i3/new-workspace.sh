#!/bin/sh
# Switch to the first unused workspace number (a fresh "session").
n=$(i3-msg -t get_workspaces | python3 -c 'import json,sys
ws={w.get("num") for w in json.load(sys.stdin)}
n=1
while n in ws:
    n += 1
print(n)')
i3-msg "workspace number $n"
