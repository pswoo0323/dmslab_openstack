from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openstack import connection
from openstack3.models.project_users import User
from openstack3.serializer import UserSerializer, ProjectUserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.cache import cache

def openstack_connection():
    conn = connection.from_config(cloud_name='default')
    return conn

from django.core.cache import cache

class ProjectUserCreate(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email'),
            },
            required=['username', 'password', 'email'],
        ),
        responses={
            201: ProjectUserSerializer,
            400: 'Bad Request',
        }
    )
    def post(self, request):
        conn = openstack_connection()
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password:
            return Response({"error": "username, password error"}, status=status.HTTP_400_BAD_REQUEST)

        # OpenStack에 사용자 생성
        user = conn.identity.create_user(
            name=username,
            password=password,
            email=email
        )

        # 데이터베이스에 사용자 저장
        db_user = User(username=username, password=password, email=email)
        db_user.save()

        # 필요한 데이터만 캐시에 저장 (예: 사용자 ID나 이메일 등 직렬화 가능한 데이터)
        cache_data = {
            "user_id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
        }
        cache.set('openstack_data_key', cache_data, timeout=3600) # 1시간 캐시유지

        # 캐시 데이터가 제대로 저장되었는지 확인하는 로그
        if cache.get('openstack_data_key'):
            print("캐시에 데이터가 저장되었습니다.")
        else:
            print("캐시 저장에 실패했습니다.")

        response_data = {
            "user": ProjectUserSerializer(db_user).data,
            "cache_data": cache_data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class ProjectUserList(APIView):
    def get(self, request):
        conn = openstack_connection()
        users = conn.identity.users()
        user_list = [{"user_name": user.username, "user_id": user.id} for user in users]
        return Response(user_list, status=status.HTTP_200_OK)


class ProjectUserDelete(APIView):
    def post(self, request):
        conn = openstack_connection()
        username = request.data.get('user_name')

        try:
            # 사용자 이름으로 ID 조회
            user = conn.identity.find_user(username, ignore_missing=True)

            # 유저가 없을 경우 에러 반환
            if not user:
                return Response({"error": "User not found"},
                                status=status.HTTP_404_NOT_FOUND)

            # 사용자 ID로 삭제 openstack은 사용자name이 아니라 id로 삭제 가능
            conn.identity.delete_user(user.id, ignore_missing=True)
            return Response({"message": "유저 삭제 성공"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

class AdminUser(APIView):
    def post(self, request):
        conn = openstack_connection()
        user_id = request.data.get('user_id')
        project_id = request.data.get('project_id')

        if not user_id or not project_id:
            return Response({"error":"유저와 프로젝트가 존재하지 않습니다."},
                            status = status.HTTP_404_NOT_FOUND)

        admin_role = conn.identity.find_role("admin")

        try:
            conn.identity.assign_project_role_to_user(user_id, project_id, role=admin_role.id)
            return Response({"message": "관리자 권한을 얻었습니다."},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckCacheView(APIView):
    def get(self, request):
        # 캐시에서 데이터 가져오기
        data = cache.get('your_cache_key')
        if data:
            return Response({"message": "캐시에 데이터가 있습니다.", "data": data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "캐시에 데이터가 없습니다.", "data": None}, status=status.HTTP_200_OK)