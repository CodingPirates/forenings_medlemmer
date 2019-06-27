#!/usr/bin/env python
# -*- coding: utf-8 -*-


def format_address(streetname, housenumber, floor=None, door=None):
    address = streetname + " " + housenumber
    if floor != "" and door != "":
        address = address + ", " + floor + ". " + door + "."

    if floor != "" and door == "":
        address = address + ", " + floor + "."

    if floor == "" and door != "":
        address = address + ", " + door + "."

    return address
