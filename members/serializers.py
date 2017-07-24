from rest_framework import serializers
from members.models.person import Person

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id','membertype','name','zipcode','city','streetname','housenumber', \
            'floor','door','dawa_id','placename','email','phone','gender', \
            'birthday','has_certificate','family','notes','added','deleted_dtm')

    def create(self, validated_data):
        """
        Create and return a new `Person` instance, given the validated data.
        """
        return Person.objects.create(**validated_data)
