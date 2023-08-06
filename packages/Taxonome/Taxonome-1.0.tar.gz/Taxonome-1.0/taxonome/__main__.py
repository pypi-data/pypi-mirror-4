#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
sys.path[0] = "." # Ugly hack so we can import ourself.
from taxonome import col

print("Commands: resolve, equivalent, map, quit, help")
while True:
    cmd, dummy, info = input(":").partition(" ")
    cmd = cmd.lower()
    if cmd.startswith("quit") or cmd.startswith("exit"):
        break
    elif cmd.startswith("help"):
        print("Examples:")
        print('  resolve "Dolichos lablab"')
        #print('  equivalent "Dolichos lablab" "Lablab purpureus"')
        #print("  map species_listA.csv species_listB.csv")
        print("  quit")
    if cmd.startswith("resolve"):
        print(col.resolve(info.strip(" \"")))
