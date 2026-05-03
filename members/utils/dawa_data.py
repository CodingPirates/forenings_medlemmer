#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from django.conf import settings


def get_user_region(person):
    dawa_req = (
        f"{settings.DATAFORSYNINGEN_BASE_URL}/adresser/{person.dawa_id}?format=geojson"
    )
    try:
        dawa_reply = json.loads(requests.get(dawa_req).text)
        user_region = dawa_reply["properties"]["regionsnavn"]
    except Exception:
        user_region = None
        # and we simply skip the region, and sorting will be as default

    return user_region
