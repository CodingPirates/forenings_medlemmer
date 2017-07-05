from django.db import models


class ZipcodeRegion(models.Model):
    REGION_CHOICES = (
        ('DK01', 'Hovedstaden'),
        ('DK02', 'Sjælland'),
        ('DK03', 'Syddanmark'),
        ('DK04', 'Midtjylland'),
        ('DK05', 'Nordjylland')
    )
    region = models.CharField('Region', blank=False, null=False, max_length=4, choices=REGION_CHOICES)
    zipcode = models.CharField('Postnummer', max_length=4)
    city = models.CharField('By', max_length=200)
    municipalcode = models.IntegerField('Kommunekode', blank=False, null=False)
    municipalname = models.TextField('Kommunenavn', null=False, blank=False)
