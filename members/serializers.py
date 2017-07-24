from rest_framework import serializers
from members.models.person import Person
from members.models.family import Family

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id','membertype','name','zipcode','city','streetname','housenumber', \
            'floor','door','dawa_id','placename','email','phone','gender', \
            'birthday','has_certificate','family','notes','added','deleted_dtm')
class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ('id','email','dont_send_mails','updated_dtm','confirmed_dtm','last_visit_dtm','deleted_dtm','unique')
 