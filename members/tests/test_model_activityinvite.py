# from django.test import TestCase
# from members.models.activity import Activity
# from members.models.activityinvite import ActivityInvite
# from members.models.person import Person
# from members.models.family import Family
# from members.models.department import Department
# from members.models.union import Union
# from members.models.emailtemplate import EmailTemplate
# from members.models.waitinglist import WaitingList
# from django.core import mail
# from datetime import timedelta, datetime
# from members.jobs import EmailSendCronJob
# from django.core.exceptions import ValidationError
#
#
# class TestModelActivityInvite(TestCase):
#     fixtures = ['templates']
#
#     def setUp(self):
#         self.union = Union()
#         self.union.save()
#
#         self.department = Department(
#             union=self.union
#         )
#         self.department.save()
#
#         self.activity = Activity(
#             start_date=datetime.now(),
#             end_date=datetime.now() + timedelta(days=365),  # Has to be long enough to be a season
#             department=self.department
#         )
#         self.activity.save()
#         self.assertTrue(self.activity.is_season())  # If this fail increase the end_date
#
#         self.family = Family(
#             email='family@example.com'
#         )
#         self.family.save()
#
#         self.person = Person(
#             family=self.family
#         )
#         self.person.save()
#
#         waitinglist = WaitingList(
#             person=self.person,
#             department=self.department,
#             on_waiting_list_since=datetime.now() - timedelta(days=1)
#         )
#         waitinglist.save()
#         self.waitinglist_id = waitinglist.id
#
#         self.emailtemplate = EmailTemplate(
#             idname='ACT_INVITE',
#             from_address='from@example.com'
#         )
#         self.emailtemplate.save()
#
#     def test_own_email(self):
#         self.person.email = 'person@example.com'
#         self.person.save()
#         self.invite = ActivityInvite(
#             activity=self.activity,
#             person=self.person
#         )
#         self.invite.save()
#         EmailSendCronJob().do()
#         self.assertEqual(len(mail.outbox), 2)
#         self.assertEqual(len(list(filter(lambda email: email.to == ['person@example.com'], mail.outbox))), 1, msg="No email was send to the persons email address")
#         self.assertEqual(len(list(filter(lambda email: email.to == ['family@example.com'], mail.outbox))), 1, msg="No email wes send to the families email address")
#
#     def test_family_email(self):
#         self.person.email = ''
#         self.person.save()
#         self.invite = ActivityInvite(
#             activity=self.activity,
#             person=self.person
#         )
#         self.invite.save()
#         EmailSendCronJob().do()
#         self.assertEqual(len(mail.outbox), 1)
#         self.assertEqual(mail.outbox[0].to, ['family@example.com'])
#
#     def test_email_only_once(self):
#         self.invite = ActivityInvite(
#             activity=self.activity,
#             person=self.person
#         )
#         self.invite.save()
#         EmailSendCronJob().do()
#         mail.outbox.clear()
#         self.invite.save()
#         EmailSendCronJob().do()
#         self.assertEqual(len(mail.outbox), 0)
#
#     def test_waiting_list(self):
#         self.invite = ActivityInvite(
#             activity=self.activity,
#             person=self.person
#         )
#         self.invite.save()
#         self.assertFalse(WaitingList.objects.filter(pk=self.waitinglist_id).exists())
#
#     def test_clean_age_limit_min(self):
#         self.person.birthday = datetime.now() - timedelta(days=365 * 2)
#         self.activity.min_age = 4
#         self.activity.max_age = 8
#         self.invite = ActivityInvite(
#             activity=self.activity,
#             person=self.person
#         )
#         with self.assertRaises(ValidationError):
#             self.invite.clean()
#
#     def test_clean_age_limit_max(self):
#         self.person.birthday = datetime.now() - timedelta(days=365 * 10)
#         self.activity.min_age = 4
#         self.activity.max_age = 6
#         self.invite = ActivityInvite(
#             activity=self.activity,
#             person=self.person
#         )
#         with self.assertRaises(ValidationError):
#             self.invite.clean()
#
#     def test_clean_age_limit_inbounds(self):
#         self.person.birthday = datetime.now() - timedelta(days=365 * 6)
#         self.activity.min_age = 4
#         self.activity.max_age = 8
#         self.invite = ActivityInvite(
#             activity=self.activity,
#             person=self.person
#         )
#         self.invite.clean()
