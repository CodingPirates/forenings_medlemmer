#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone


class WaitingList(models.Model):
    class Meta:
        verbose_name = "På venteliste"
        verbose_name_plural = "På ventelister"
        ordering = ["on_waiting_list_since"]

    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    on_waiting_list_since = models.DateTimeField(
        "Venteliste position", blank=False, null=False
    )
    added_dtm = models.DateTimeField(
        "Tilføjet", blank=False, null=False, default=timezone.now
    )

    def number_on_waiting_list(self):
        return (
            WaitingList.objects.filter(
                department=self.department,
                on_waiting_list_since__lt=self.on_waiting_list_since,
            ).count()
            + 1
        )

    number_on_waiting_list.short_description = "Position på venteliste"

    def save(self, *args, **kwargs):
        """ On creation set on_waiting_list """
        if not self.id:
            self.on_waiting_list_since = self.person.added
        return super(WaitingList, self).save(*args, **kwargs)

    @staticmethod
    def get_by_child(child):
        """ Returns a list of (department, waitinglist_tuple) tuples """
        waitlists = [
            (waitinglist.department, waitinglist.number_on_waiting_list())
            for waitinglist in WaitingList.objects.filter(person=child)
        ]
        waitlists.sort(key=lambda tup: tup[1])
        return waitlists
