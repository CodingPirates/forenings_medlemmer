#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models


class Notification(models.Model):
    family = models.ForeignKey("Family", on_delete=models.CASCADE)
    email = models.ForeignKey("EmailItem", on_delete=models.CASCADE)
    update_info_dtm = models.DateTimeField(
        "Bedt om opdatering af info", blank=True, null=True
    )
    warned_deletion_info_dtm = models.DateTimeField(
        "Advaret om sletning fra liste", blank=True, null=True
    )
    anounced_department = models.ForeignKey(
        "Department", null=True, on_delete=models.CASCADE
    )
    anounced_activity = models.ForeignKey(
        "Activity", null=True, on_delete=models.CASCADE
    )
    anounced_activity_participant = models.ForeignKey(
        "ActivityParticipant", null=True, on_delete=models.CASCADE
    )
