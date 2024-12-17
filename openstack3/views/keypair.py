import os.path
from http.client import responses

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openstack import connection
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os


def openstack_connection():
    conn = connection.from_config(cloud_name='default')

    return conn


class CreateKeyPair(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'key_name': openapi.Schema(type=openapi.TYPE_STRING, description='Key pair name'),
                'public_key': openapi.Schema(type=openapi.TYPE_STRING, description='Public key (optional)'),
            },
            required=['key_name'],
        ),
        responses={
            201: 'ResourcesSerializer',  # 성공 시 ResourcesSerializer 형식으로 응답
            400: 'Bad Request',
        }
    )
    def post(self, request):
        conn = openstack_connection()
        keypair_name = request.data.get('key_name')
        public_key = request.data.get('public_key')

        if not keypair_name:
            return Response({"error": "키페어 이름을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 체크
            existing_keypair = conn.compute.find_keypair(keypair_name)
            if existing_keypair:
                return Response({"error": "이미 존재하는 키페어 입니다."}, status=status.HTTP_400_BAD_REQUEST)

            # 키페어 생성
            if public_key:
                keypair = conn.compute.create_keypair(name=keypair_name, public_key=public_key)
            else:
                keypair = conn.compute.create_keypair(name=keypair_name)

            if not public_key:
                private_key_path = os.path.join(os.getcwd(), f"{keypair_name}.pem")# public_key없으면 현재 작업 경로에 priviate_key 생성
                with open(private_key_path, "w") as key_file:# 현재 작업 경로에 .pem 파일을 작성 모드 (w)로 열고, 파일 객체를 key_file 변수로 가져온다.
                    key_file.write(keypair.private_key)# OpenStack에서 생성한 개인 키(keypair.private_key)를 .pem 파일에 기록.
                os.chmod(private_key_path, 0o600)# .pem 파일의 권한을 변경하여 읽기 및 쓰기 권한을 현재 사용자에게만 부여
                # 6: 파일 소유자에게 읽기(4)와 쓰기(2) 권한을 부여.
                # 0: 그룹과 다른 사용자에게는 권한 없음.

            response_data = {
                "message": "키페어가 생성되었습니다.",
                "keypair_name": keypair.name,
                "public_key": keypair.public_key,
            }

            if not public_key:
                response_data["private_key_saved_at"] = private_key_path

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
