from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openstack import connection
from openstack3.models import User


def openstack_connection():
    conn = connection.from_config(cloud_name='default')

    return conn

class UserCreate(APIView):
    def post(self, request):
        conn = openstack_connection()
        username = request.data.get('username')
        password= request.data.get('password')
        email = request.data.get('email')

        if not username or not password:
            return Response({"error": "username, password error"})

        user = conn.identity.create_user(
            name = username,
            password= password,
            email= email
        )

        db_user = User(username=username, password=password, email=email)
        db_user.save()

        return Response({"user_ID": user.id, "username": user.name},
                        status= status.HTTP_201_CREATED)

class UserList(APIView):
    def get(self, request):
        conn = openstack_connection()
        users = conn.identity.users()
        user_list = [{"user_name": user.name, "user_id": user.id} for user in users]
        return Response(user_list, status=status.HTTP_200_OK)


class UserDelete(APIView):
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

class AssignAdminRole(APIView):
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