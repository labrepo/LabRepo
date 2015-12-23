from rest_framework import serializers

from profiles.models import LabUser


class LabUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = LabUser
        fields = ('id', 'first_name', 'last_name', 'full_name')
