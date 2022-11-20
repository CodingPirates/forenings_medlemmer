#!/usr/bin/env python
# -*- coding: utf-8 -*-


# TODO remove this once everything is moved to address model
def format_address(streetname, housenumber, floor=None, door=None):
    address = streetname + " " + housenumber
    if floor != "" and door != "":
        address = address + ", " + floor + ". " + door + "."

    if floor != "" and door == "":
        address = address + ", " + floor + "."

    if floor == "" and door != "":
        address = address + ", " + door + "."

    return address
