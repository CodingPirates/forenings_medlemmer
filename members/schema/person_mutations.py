import datetime
import django
import graphene
from graphql import GraphQLError
import graphql_jwt
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
from members.models import Person
from members.models import Family


class CreateAdultInput(graphene.InputObjectType):
    gender = graphene.String(required=True)
    name = graphene.String(required=True)
    password = graphene.String(required=True)
    email = graphene.String(required=True)
    birthday = graphene.types.datetime.Date(required=True)
    phone = graphene.String(required=True)
    zipcode = graphene.Int(required=True)
    streetname = graphene.String(required=True)
    housenumber = graphene.String(required=True)
    city = graphene.String(required=True)


class CreateAdultMutation(graphene.Mutation):
    class Arguments:
        input = CreateAdultInput(required=True)

    name = graphene.String(required=True)
    email = graphene.String(required=True)

    def mutate(self, info, input):
        valid_genders = [
            short_name for (short_name, long_name) in Person.MEMBER_GENDER_CHOICES
        ]
        if input["gender"] not in valid_genders:
            raise GraphQLError(f"Køn skal være en af {valid_genders}")

        if len(input["name"]) < 3 or len(input["name"]) > 200:
            raise GraphQLError(f'Ugyldigt navn: {input["name"]}')

        try:
            django.core.validators.validate_email(input["email"])
        except django.core.exceptions.ValidationError:
            raise GraphQLError(f'Ugyldig email: {input["email"]}')

        if (
            len(Person.objects.filter(email=input["email"])) > 0
            or len(Family.objects.filter(email=input["email"])) > 0
            or len(User.objects.filter(username=input["email"])) > 0
        ):
            raise GraphQLError("Email er i brug")

        if input["birthday"] > datetime.date.today() - relativedelta(years=18):
            raise GraphQLError(
                "Du skal være over 18 for at bliver oprettet som\
             frivillig/forældre"
            )
        if (
            len(input["password"]) < 8
            or not any([char.isdigit() for char in input["password"]])
            or not any([char.isalpha() for char in input["password"]])
            or not any([not char.isalpha() for char in input["password"]])
            or not any([char.isupper() for char in input["password"]])
            or not any([char.islower() for char in input["password"]])
        ):
            raise GraphQLError(
                "Ugyldigt kodeord, det skal være mindst 8 tegn, mindst et \
                    tal, et tegn og både store og små bogstaver"
            )
        if len(input["phone"]) < 8:
            raise GraphQLError("Ugyldigt telefon nummer")

        f = Family(email=input["email"])
        f.save()

        user = User.objects.create_user(
            username=input["email"], email=input["email"], password=input["password"]
        )

        user.save()

        person = Person(
            gender=input["gender"],
            name=input["name"],
            email=input["email"],
            birthday=input["birthday"],
            phone=input["phone"],
            family=f,
            membertype="PA",
            zipcode=str(input["zipcode"]),
            city=input["city"],
            streetname=input["streetname"],
            housenumber=input["housenumber"],
            user=user,
        )
        person.save()

        return CreateAdultMutation(name=person.name, email=person.email)
