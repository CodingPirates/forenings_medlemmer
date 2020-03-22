#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


class Membership(models.Model):
    class Meta:
        verbose_name = "Foreningsmedlemskab"
        verbose_name_plural = "Foreningsmedlemskaber"
        ordering = ["union"]

    union = models.ForeignKey("Union", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    sign_up_date = models.DateField("Opskrivningsdato")

    def clean(self):
        self.sign_up_date = (
            date.today() if self.sign_up_date is None else self.sign_up_date
        )
        self.can_be_member_validator(self.person, self.union, self.sign_up_date.year)

    def save(self, *args, **kwargs):
        self.clean()
        super(Membership, self).save(*args, **kwargs)

    def __str__(self):
        return f"Medlemskab: {self.person} : {self.union}"

    @staticmethod
    def can_be_member_validator(person, union, year=None):
        old_memberships = [
            membership.sign_up_date.year
            for membership in Membership.objects.filter(person=person, union=union)
        ]
        year = date.today().year if year is None else year
        if year in old_memberships:
            raise ValidationError(
                f"{person} er allerede medlem af foreningen {union} i år {year}"
            )
