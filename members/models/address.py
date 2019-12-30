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
    streetname = models.CharField("Vejnavn", max_length=200)
    housenumber = models.CharField("Husnummer", max_length=5)
    floor = models.CharField("Etage", max_length=10, blank=True)
    door = models.CharField("Dør", max_length=5, blank=True)
    city = models.CharField("By", max_length=200)
    zipcode = models.CharField("Postnummer", max_length=4)
    municipality = models.CharField("Kommune", max_length=100, blank=True, null=True)
    placename = models.CharField("Stednavn", max_length=200, blank=True)
    longitude = models.DecimalField(
        "Længdegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    latitude = models.DecimalField(
        "Breddegrad", blank=True, null=True, max_digits=9, decimal_places=6
    )
    dawa_id = models.CharField("DAWA id", max_length=200, blank=True)

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
            try:
                address = self.addressWithZip()
                response = requests.request("GET", "https://dawa.aws.dk/datavask/adresser", data="", params={"betegnelse": address})
                payload = json.loads(response.content)
            except Exception as error:
                logger.error("Couldn't find dawa_id for " + self.name)
                logger.error("Error " + str(error))
                return None
            # A and B means a match
            if payload['kategori'] < 'C':
                match = payload['resultater'][0]['aktueladresse']
                self.zipcode = match["postnr"]
                self.city = match["postnrnavn"]
                self.streetname = match["vejnavn"]
                self.housenumber = match["husnr"]
                self.floor = match["etage"]
                self.door = match["dør"]
                self.dawa_id = match["adgangsadresseid"]
            try:
                req = (
                    "https://dawa.aws.dk/adresser/" + match["adgangsadresseid"] + "?format=geojson"
                )
                addressPayload = json.loads(requests.get(req).text)
            except Exception as error:
                logger.error("Couldn't find coordinates for " + self.name)
                logger.error("Error " + str(error))
            self.placename = addressPayload["properties"]["supplerendebynavn"]
            self.latitude = addressPayload["geometry"]["coordinates"][1]
            self.longitude = addressPayload["geometry"]["coordinates"][0]
            self.municipality = addressPayload["properties"]["kommunenavn"]
            self.save()