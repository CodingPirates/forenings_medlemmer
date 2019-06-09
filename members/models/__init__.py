#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ensure all models are included - otherwise makemigrations fails to detect models
import members.models.activity
import members.models.activityinvite
import members.models.activityparticipant
import members.models.dailystatisticsdepartment
import members.models.dailystatisticsgeneral
import members.models.dailystatisticsregion
import members.models.dailystatisticsunion
import members.models.department
import members.models.emailitem
import members.models.emailtemplate
import members.models.equipment
import members.models.equipmentloan
import members.models.family
import members.models.member
import members.models.notification
import members.models.payment
import members.models.person
import members.models.quickpaytransaction
import members.models.union
import members.models.volunteer
import members.models.waitinglist
import members.models.zipcoderegion  # noqa  # fine to hav eall models included


# Export models not files
from .department import Department
from .union import Union
from .person import Person
