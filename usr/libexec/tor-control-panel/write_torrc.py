#!/usr/bin/python3 -I
import sys

path = '/etc/tor/torrc'
content = sys.stdin.read()

with open(path, 'w') as f:
    f.write(content)

