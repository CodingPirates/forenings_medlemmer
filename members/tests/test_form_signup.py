from django.test import TestCase

from members.forms.signup_form import signupForm


class TestSignupForm(TestCase):
    def get_valid_form_data(self):
        return {
            "form_id": "signup",
            "next": "",
            "parent_gender": "MA",
            "parent_name": "Anders Afprøvning",
            "parent_birthday": "1980-03-05",
            "parent_email": "parent@example.com",
            "parent_phone": "12345678",
            "password1": "securepassword123-securepassword123",
            "password2": "securepassword123-securepassword123",
            "streetname": "Kochsgade",
            "housenumber": "31D",
            "floor": "",
            "door": "",
            "zipcode": "5000",
            "city": "Odense C",
            "placename": "",
            "dawa_id": "test-dawa-id",
            "search_address": "",
            "manual_entry": "",
            "consent": "on",
        }

    def test_child_fields_are_optional_when_no_child_name(self):
        form = signupForm(data=self.get_valid_form_data())

        self.assertTrue(form.is_valid(), form.errors)

    def test_child_gender_and_birthday_are_required_when_child_name_is_set(self):
        data = self.get_valid_form_data()
        data.update(
            {
                "child_name": "Torben Test",
                "child_gender": "",
                "child_birthday": "",
                "child_email": "",
                "child_phone": "",
            }
        )

        form = signupForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("child_gender", form.errors)
        self.assertIn("child_birthday", form.errors)
        self.assertNotIn("child_email", form.errors)
        self.assertNotIn("child_phone", form.errors)

    def test_child_email_and_phone_remain_optional_when_child_is_created(self):
        data = self.get_valid_form_data()
        data.update(
            {
                "child_name": "Torben Test",
                "child_gender": "MA",
                "child_birthday": "2010-03-05",
                "child_email": "",
                "child_phone": "",
            }
        )

        form = signupForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)
