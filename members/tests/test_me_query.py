from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.testcases import JSONWebTokenTestCase
from members.tests.factories import PersonFactory
from members.schema import schema
import json


class MeQueryValidTest(JSONWebTokenTestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.client.authenticate(self.person.user)

    def test_get_user(self):
        response = self.client.execute(
            """
            query {
                me {
                    name
                    email
                }
            }
        """
        )
        data = response.to_dict()["data"]["me"]
        self.assertEqual(data["name"], self.person.name)
        self.assertEqual(data["email"], self.person.email)


class MeInvalidTestt(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def test_me_not_logged_in(self):
        response = self.query(
            """
                query {
                    me {
                        name
                        email
                    }
                }
            """
        )

        self.assertResponseHasErrors(response)
        self.assertEqual(
            json.loads(response.content)["errors"][0]["message"],
            "You do not have permission to perform this action",
        )
