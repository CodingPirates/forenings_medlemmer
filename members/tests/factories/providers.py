import random
from faker.providers import BaseProvider


class CodingPiratesProvider(BaseProvider):
    activity_types = [
        "Hackathon",
        "Gamejam",
        "Børne IT-konference",
        "Summercamp",
        "Forårssæson",
        "Efterårssæson",
    ]

    def activity_type(self):
        """Formatter for generating random activity types"""
        return random.choice(self.activity_types)

    def activity(self):
        """Formatter for generating random Coding Pirates activities"""
        pattern = "{{activity_type}} {{year}}"
        return self.generator.parse(pattern)

    payment_types = ["CA", "BA", "CC", "RE", "OT"]

    def payment_type(self):
        return random.choice(self.payment_types)


class DanishProvider(BaseProvider):
    """
    Custom faker provider for Danish addresses.
    """

    floor_formats = [
        "",
        "Stuen",
        "1. sal",
        "1",
        "1.",
        "2.",
        "0",
        "0.",
        "4.",
        "kl",
        "st",
        "kælder",
        "k2",
    ]

    door_formats = ["", "410", "th", "tv", "mf", "v28"]  # , "værelse 17"]

    city_suffixes = ["rød", "havn", "borg", "by", "bjerg", "ssund", "sværk", "ning"]
    street_suffixes = ["Vej", "Gade", "Vangen", "Stræde", "Plads"]

    def floor(self):
        """Formatter for generating floor names in danish"""
        return random.choice(self.floor_formats)

    def door(self):
        """Formatter for generating door names in danish"""
        return random.choice(self.door_formats)

    def zipcode(self):
        """Formatter for generating door names in danish"""
        return str(random.randint(1000, 9999))

    def city_suffix(self):
        """
        :example 'rød'
        """
        return self.random_element(self.city_suffixes)

    def street_suffix(self):
        """
        :example 'vej'
        """
        return self.random_element(self.street_suffixes)

    def city(self):
        """
        :example 'Frederiksværk'
        """
        pattern = "{{first_name}}{{city_suffix}}"
        return self.generator.parse(pattern)

    def municipality(self):
        """Formatter for generating danish municipality names"""
        return self.generator.parse("{{city}} kommune")

    def street_name(self):
        """Formatter for generating danish street names"""
        return self.generator.parse("{{name}}s {{street_suffix}}")
