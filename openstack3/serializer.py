from openstack3.domain.models import *
from rest_framework import serializers

from openstack3.domain.resources import Resources


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = '__all__'