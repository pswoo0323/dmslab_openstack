from openstack3.models.project_users import *
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from openstack3.models.resources import Resources
from rest_framework import serializers


class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = '__all__'
