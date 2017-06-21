from django.db import models


class Notification(models.Model):
    family = models.ForeignKey('Family')
    email = models.ForeignKey('EmailItem')
    update_info_dtm = models.DateTimeField('Bedt om opdatering af info', blank=True, null=True)
    warned_deletion_info_dtm = models.DateTimeField('Advaret om sletning fra liste', blank=True, null=True)
    anounced_department = models.ForeignKey('Department', null=True)
    anounced_activity = models.ForeignKey('Activity', null=True)
    anounced_activity_participant = models.ForeignKey('ActivityParticipant', null=True)
