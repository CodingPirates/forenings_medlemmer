import json

from graphene_django.utils.testing import GraphQLTestCase
from members.schema import schema
from members.tests.factories import PersonFactory

from members.models import Person, Family


class PersonMutationsTest(GraphQLTestCase):
    def setUp(self):
        self.person = PersonFactory.build()
        self.input = {
            "password": "Password8!",
            "email": self.person.email,
            "gender": self.person.gender,
            "name": self.person.name,
            "housenumber": self.person.housenumber,
            "streetname": self.person.streetname,
            "phone": self.person.phone,
            "zipcode": self.person.zipcode,
            "birthday": str(self.person.birthday),
            "city": self.person.city,
        }

    GRAPHQL_SCHEMA = schema

    def test_valid_create_adult(self):
        persons_before_mutation = len(Person.objects.filter(email=self.person.email))
        response = self.query(
            """
            mutation createAdult($input: CreateAdultInput!) {
                createAdult(input: $input) {
		              name
                      email
                }
            }
            """,
            op_name="createAdult",
            input_data=self.input,
        )
        person_after_muation = Person.objects.filter(email=self.person.email)
        self.assertEqual(len(person_after_muation), 1)
        person_after_muation = person_after_muation[0]
        print(response.content)
        self.assertResponseNoErrors(response)
        data = json.loads(response.content)["data"]["createAdult"]
        self.assertEqual(data["name"], self.person.name)
        self.assertEqual(data["email"], self.person.email)
        self.assertEqual(persons_before_mutation, 0)
        self.assertEqual(person_after_muation.name, self.person.name)
        self.assertEqual(person_after_muation.email, self.person.email)

    def test_create_adult_invalid(self):
        self.input["password"] = "invalid password"
        persons_before_mutation = Person.objects.filter(email=self.person.email)
        response = self.query(
            """
            mutation createAdult($input: CreateAdultInput!) {
                createAdult(input: $input) {
		              name
                      email
                }
            }
            """,
            op_name="createAdult",
            input_data=self.input,
        )
        print(response.content)
        self.assertResponseHasErrors(response)
        person_after_muation = Person.objects.filter(email=self.person.email)
        self.assertEqual(len(persons_before_mutation), len(person_after_muation))
