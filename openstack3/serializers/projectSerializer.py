from openstack3.models.project_users import *
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from openstack3.models.resources import Resources
from rest_framework import serializers
from openstack3.models.users import CustomUser
from openstack3.utils.token import get_cached_openstack_token

User = get_user_model()

class ProjectUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectUser
        fields = '__all__'