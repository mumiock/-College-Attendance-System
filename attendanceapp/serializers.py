from rest_framework import serializers

from info.models import *


class logSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'


