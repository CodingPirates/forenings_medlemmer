import json

from graphene_django.utils.testing import GraphQLTestCase
from members.schema import schema
from members.tests.factories import PersonFactory

from members.models import Person, Family


class GraphQLTokenTest(GraphQLTestCase):
    def setUp(self):
        self.person = PersonFactory.build()
        self.password = "adfe9v93"
        self.person.user.set_password(self.password)
        self.person.user.save()

    GRAPHQL_SCHEMA = schema

    def test_valid_get_token(self):
        # Check that we gan get a token
        response = self.query(
            f"""
            mutation {{
                tokenAuth(username: "{self.person.email}", password: "{self.password}"){{
                    token
                }}
            }}
            """,
            op_name="tokenAuth",
        )
        self.assertResponseNoErrors(response)

        # Check that token can be verified
        token = json.loads(response.content)["data"]["tokenAuth"]["token"]
        response = self.query(
            f"""
            mutation {{
                verifyToken(token: "{token}") {{
                    payload
                }}
            }}
            """,
            op_name="verifyToken",
        )
        self.assertResponseNoErrors(response)
        personToken = json.loads(response.content)["data"]["verifyToken"]["payload"][
            "username"
        ]
        self.assertEqual(personToken, self.person.user.username)

        # Can verify changed tokean
        response = self.query(
            f"""
            mutation {{
                verifyToken(token: "{token + "a"}") {{
                    payload
                }}
            }}
            """,
            op_name="verifyToken",
        )
        self.assertResponseHasErrors(response)

        # Fails on wrong password
        response = self.query(
            f"""
            mutation {{
                tokenAuth(username: "{self.person.email}", password: "{self.password + '1'}"){{
                    token
                }}
            }}
            """,
            op_name="tokenAuth",
        )
        self.assertResponseHasErrors(response)

        # Can refresh token
        response = self.query(
            f"""
            mutation {{
                refreshToken(token: "{token}"){{
                    token
                    payload
                }}
            }}
            """,
            op_name="refreshToken",
        )
        self.assertResponseNoErrors(response)
