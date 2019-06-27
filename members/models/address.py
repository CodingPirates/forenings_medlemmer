#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.conf import settings
from members.utils.address import format_address
from urllib.parse import quote_plus
import requests
import logging
import json


class Address(models.Model):
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresser"
    streetname = models.CharField("Vejnavn", max_length=200, blank=True)
    housenumber = models.CharField("Husnummer", max_length=5, blank=True)
    floor = models.CharField("Etage", max_length=10, blank=True)
    door = models.CharField("Dør", max_length=5, blank=True)
    city = models.CharField("By", max_length=200, blank=True)
    zipcode = models.CharField("Postnummer", max_length=4, blank=True)
    municipality = models.CharField("Kommune", max_length=100, blank=True, null=True)
    placename = models.CharField("Stednavn", max_length=200, blank=True)
    longitude = models.DecimalField(
        "Længdegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    latitude = models.DecimalField(
        "Breddegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    dawa_id = models.CharField("DAWA id", max_length=200, blank=True)
    address_invalid = models.BooleanField("Ugyldig adresse", default=False)

    def __str__(self):
        return format_address(self.streetname, self.housenumber, self.floor, self.door)

    def addressWithZip(self):
        return str(self) + ", " + self.zipcode + " " + self.city

    def update_dawa_data(self):
        if (
            self.dawa_id is None
            or self.latitude is None
            or self.longitude is None
            or self.municipality is None
        ):
            addressID = 0
            dist = 0
            req = "https://dawa.aws.dk/datavask/adresser?betegnelse="
            req += quote_plus(self.addressWithZip())
            try:
                washed = json.loads(requests.get(req).text)
                addressID = washed["resultater"][0]["adresse"]["id"]
                dist = washed["resultater"][0]["vaskeresultat"]["afstand"]
            except Exception as error:
                logger.error("Couldn't find addressID for " + self.name)
                logger.error("Error " + str(error))
            if addressID != 0 and dist < 10:
                try:
                    req = (
                        "https://dawa.aws.dk/adresser/" + addressID + "?format=geojson"
                    )
                    address = json.loads(requests.get(req).text)
                    if address["properties"]["etage"] is None:
                        address["properties"]["etage"] = ""
                    if address["properties"]["dør"] is None:
                        address["properties"]["dør"] = ""
                    if address["properties"]["supplerendebynavn"] is None:
                        address["properties"]["supplerendebynavn"] = ""
                    self.zipcode = address["properties"]["postnr"]
                    self.city = address["properties"]["postnrnavn"]
                    self.streetname = address["properties"]["vejnavn"]
                    self.housenumber = address["properties"]["husnr"]
                    self.floor = address["properties"]["etage"]
                    self.door = address["properties"]["dør"]
                    self.placename = address["properties"]["supplerendebynavn"]
                    self.latitude = address["geometry"]["coordinates"][1]
                    self.longitude = address["geometry"]["coordinates"][0]
                    self.municipality = address["properties"]["kommunenavn"]
                    self.dawa_id = address["properties"]["id"]
                    self.save()
                except Exception as error:
                    logger.error("Couldn't find coordinates for " + self.name)
                    logger.error("Error " + str(error))
                    return None
            else:
                self.address_invalid = True
                self.save()