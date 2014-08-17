# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class Address(models.Model):
	road_name = models.CharField('Vejnavn', max_length = 256)
	house_number = models.IntegerField('Husnummer')
	floor = models.IntegerField('Etage', blank = True, null = True)
	door = models.CharField('Dør', max_length = 64, blank = True, null = True)
	postal_code = models.IntegerField('postnummer')
	city = models.CharField('By', max_length = 256)
	verified_dtm = models.DateField('Sidste gang adressen blev bekræftet', blank = True, null = True)

class Phonenumber(models.Model):
	country_prefix = models.IntegerField('Landekode')
	number = models.IntegerField('Telefon nummer')
	message_capable = models.BooleanField("Kan modtage SMS'er")
	verified_dtm = models.DateField('Sidste gang nummeret blev bekræftet', blank = True, null = True)
	last_message_dtm = models.DateTimeField('Tidspunkt seneste SMS blev sendt til nummeret', blank = True, null = True)

class EmailAdress(models.Model):
	email_address = models.CharField('Email adresse', primary_key = True, max_length = 256)
	verified_dtm = models.DateField('Sidste gang adressen blev bekræftet', blank=True, null = True)
	last_message_dtm = models.DateTimeField('Tidspunkt deneste E-mail blev sendt til adressen', blank=True, null = True)

class Person(models.Model):
	STUDENT = 'STUDENT'
	PARENT = 'PARENT'
	TEACHER = 'TEACHER'
	PERSON_TYPE = (
		(STUDENT, 'Studerende'),
		(PARENT, 'Forælder / Værge'),
		(TEACHER, 'Underviser / Frivillig')
		)
	member_type = models.CharField('Type', max_length = 32, choices = PERSON_TYPE, default = STUDENT)

	name = models.CharField('Fornavn', max_length = 256)
	last_name = models.CharField('Efternavn', max_length = 256)
	address = models.ForeignKey(Address)
	email = models.ForeignKey(EmailAdress, blank=True, null = True)
	phone = models.ForeignKey(Phonenumber, blank=True, null = True)
	mobile_phone = models.ForeignKey(Phonenumber, related_name = 'mobile_phonenumber', blank=True, null = True)
	born = models.DateField('Født', blank=True, null = True)
	age = models.IntegerField('Alder (ved indmeldelses tidspunkt)', blank=True, null = True)
	forum_id = models.CharField('Forum navn', max_length = 256, blank=True, null = True)
	criminal_record_checked_dtm = models.DateField('Børneattest modtaget', blank=True, null = True)
	signed_up_dtm = models.DateTimeField('Tilmedings tidspunkt for ancienitet (venteliste)')
	signed_out_dtm = models.DateTimeField('Udmeldelses tidspunkt', blank=True, null = True)
	special_cares = models.TextField('Særlige hensyn', blank=True, null = True) 	
	experiences = models.TextField('Erfaringer', blank=True, null = True)
	wishes = models.TextField('Ønsker til undervisningen', blank=True, null = True)
	internal_comments = models.TextField('Interne kommentater', blank=True, null = True)

class Foto(models.Model):
	picture = models.CharField('Billede', max_length = 64)
	uploaded_dtm = models.DateField('Upload tidspunkt')
	person = models.ForeignKey(Person)

class Department(models.Model):
	name = models.CharField('Afdelingsnavn', max_length = 128)
	description = models.TextField('Beskrivelse', blank=True, null = True)
	planned_start_dtm = models.DateField('Planglagt åbningsdag')
	start_dtm = models.DateField('Åbningsdag', blank=True, null = True)
	ceased_dtm = models.DateField('Nedluknings dato', blank=True, null = True)
	responsible = models.ForeignKey(Person)
	address = models.ForeignKey(Address)
	phonenumber = models.ForeignKey(Phonenumber)
	email = models.ForeignKey(EmailAdress)

class Activity(models.Model):
	name = models.CharField('Navn / Titel', max_length = 128)
	description = models.TextField('Beskrivelse', blank=True, null = True)
	department = models.ForeignKey(Department, blank=True, null = True)
	price = models.DecimalField('Pris (kr)', max_digits = 5, decimal_places=2)
	seats = models.IntegerField('Pladser på holdet i alt')
	signup_open_dtm = models.DateField("Åben for opskrivning dato", blank=True, null = True) 
	signup_closed_dtm = models.DateField("Lukkedato for opskrivning", blank=True, null = True) 

class ActivityDate(models.Model):
	activity = models.ForeignKey(Activity)
	date = models.DateTimeField('Tidspunkt')
	description = models.TextField('Beskrivelse', blank=True, null = True)

class ActivitySignup(models.Model):
	person = models.ForeignKey(Person)
	activity = models.ForeignKey(Activity)
	requested_dtm = models.DateTimeField('Har bedt om indskrivning tidspunkt', blank=True, null = True)
	invited_dtm = models.DateTimeField('Er blevet inviteret tidspunkt', blank=True, null = True)
	accepted_dtm = models.DateTimeField('Optaget tidspunkt', blank=True, null = True)

class ActivityMeet(models.Model):
	person = models.ForeignKey(Person)
	activity = models.ForeignKey(Activity)
	date = 	models.ForeignKey(ActivityDate)
	was_present_dtm = models.DateTimeField("Mødte op", blank=True, null = True) 
	prevented_dtm = models.DateTimeField("Forhindret", blank=True, null = True)
	prevented_message =  models.TextField('Forhindret grund', blank=True, null = True)

class Payment(models.Model):
	person = models.ForeignKey(Person, blank=True, null = True)
	activity = models.ForeignKey(Activity, blank=True, null = True)
	amount = models.DecimalField('Betalt (kr)', max_digits = 5, decimal_places=2)
	date = models.DateTimeField('Tidspunkt')
	bank_message =  models.TextField('Bank besked')
