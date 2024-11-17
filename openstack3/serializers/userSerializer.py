from openstack3.models.project_users import *
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from openstack3.models.resources import Resources
from rest_framework import serializers
from openstack3.models.users import CustomUser
from openstack3.utils.token import get_cached_openstack_token

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    userPW = serializers.CharField(write_only=True)  # 비밀번호는 write-only

    class Meta:
        model = CustomUser
        fields = ['userID', 'userPW', 'userName', 'userEmail', 'userRole', 'userDetail']

    def create(self, validated_data):
        password = validated_data.pop('userPW')
        user = CustomUser(**validated_data)
        user.set_password(password)  # 비밀번호 암호화 후 저장
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    userID = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['userID'], password=data['password'])
        # 사용자 인증 실패 시
        if not user:
            raise serializers.ValidationError("올바른 자격 증명이 아닙니다.")
        # 승인되지 않은 사용자일 경우
        if not user.approve:
            raise serializers.ValidationError("관리자 승인이 필요합니다.")
        # OpenStack 인증 토큰 캐시 확인 및 발급
        try:
            token = get_cached_openstack_token(data['userID'])
        except Exception as e:
            raise serializers.ValidationError(f"OpenStack 인증에 실패했습니다: {str(e)}")
        return {
            "user": user,
            "openstack_token": token
        }

class UserPendingApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['uuid', 'userID', 'userName', 'userEmail', 'userRole']  # 필요한 정보만 선택