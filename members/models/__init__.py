#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Ensure all models are included - otherwise makemigrations fails to detect models
import members.models.activity
import members.models.activitytype
import members.models.activityinvite
import members.models.activityparticipant

import members.models.consent
import members.models.department
import members.models.emailitem
import members.models.emailtemplate
import members.models.equipment
import members.models.equipmentloan
import members.models.family
import members.models.municipality
import members.models.member
import members.models.notification
from members.models.slackinvitesetup import SlackInvitationSetup
from members.models.slackinvitelog import SlackInviteLog
import members.models.payment
import members.models.person
import members.models.anonymization_candidate
import members.models.quickpaytransaction
import members.models.union
import members.models.volunteer
import members.models.waitinglist
import members.models.zipcoderegion  # noqa  # fine to have all models included


# Export models not files
from .activity import Activity
from .activitytype import ActivityType
from .activityinvite import ActivityInvite
from .activityparticipant import ActivityParticipant
from .address import Address
from .admin_user_information import AdminUserInformation
from .consent import Consent
from .dailystatisticsgeneral import DailyStatisticsGeneral
from .dailystatisticsregion import DailyStatisticsRegion
from .dailystatisticsunion import DailyStatisticsUnion
from .department import Department
from .emailitem import EmailItem
from .emailtemplate import EmailTemplate
from .equipment import Equipment
from .equipmentloan import EquipmentLoan
from .family import Family
from .municipality import Municipality
from .member import Member
from .notification import Notification
from .payment import Payment
from .person import Person
from .anonymization_candidate import AnonymizationCandidate
from .union import Union
from .volunteer import Volunteer
from .waitinglist import WaitingList
from .zipcoderegion import ZipcodeRegion


from .statistics import gatherDayliStatistics

__all__ = [
    Activity,
    ActivityInvite,
    ActivityType,
    ActivityParticipant,
    Address,
    AdminUserInformation,
    AnonymizationCandidate,
    Consent,
    DailyStatisticsGeneral,
    DailyStatisticsRegion,
    DailyStatisticsUnion,
    Department,
    EmailItem,
    EmailTemplate,
    Equipment,
    EquipmentLoan,
    Family,
    gatherDayliStatistics,
    Municipality,
    Member,
    Notification,
    Payment,
    Person,
    Union,
    Volunteer,
    WaitingList,
    ZipcodeRegion,
    SlackInviteLog,
    SlackInvitationSetup,
]
