#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError


class Membership(models.Model):
    class Meta:
        verbose_name = "Foreningsmedlemskab"
        verbose_name_plural = "Foreningsmedlemskaber"
        ordering = ["union"]

    union = models.ForeignKey("Union", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    sign_up_date = models.DateField("Opskrivningsdato")

    def clean(self):
        old_memberships = [
            membership.sign_up_date.year
            for membership in Membership.objects.filter(
                person=self.person, union=self.union
            ).exclude(id=self.id)
        ]
        if self.sign_up_date.year in old_memberships:
            raise ValidationError(
                f"{self.person} is already a member of {self.union} for the \
                year {self.sign_up_date.year}"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super(Membership, self).save(*args, **kwargs)

    def __str__(self):
        return f"Medlemskab: {self.person} af {self.union}"
