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
        operation_description="Keypair를 생성합니다.",
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
            return Response({"error": "Check the keypair name again"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 체크
            existing_keypair = conn.compute.find_keypair(keypair_name)
            if existing_keypair:
                return Response({"error": "The keypair aleady exists."}, status=status.HTTP_400_BAD_REQUEST)

            # 키페어 생성
            if public_key:
                keypair = conn.compute.create_keypair(name=keypair_name, public_key=public_key)
            else:
                keypair = conn.compute.create_keypair(name=keypair_name)

            if not public_key:
                private_key_path = os.path.join(os.getcwd(),
                                                f"{keypair_name}.pem")  # public_key없으면 현재 작업 경로에 priviate_key 생성
                with open(private_key_path,
                          "w") as key_file:  # 현재 작업 경로에 .pem 파일을 작성 모드 (w)로 열고, 파일 객체를 key_file 변수로 가져온다.
                    key_file.write(keypair.private_key)  # OpenStack에서 생성한 개인 키(keypair.private_key)를 .pem 파일에 기록.
                os.chmod(private_key_path, 0o600)  # .pem 파일의 권한을 변경하여 읽기 및 쓰기 권한을 현재 사용자에게만 부여
                # 6: 파일 소유자에게 읽기(4)와 쓰기(2) 권한을 부여.
                # 0: 그룹과 다른 사용자에게는 권한 없음.

            response_data = {
                "message": "Keypair created successfully.",
                "keypair_name": keypair.name,
                "public_key": keypair.public_key,
            }

            if not public_key:
                response_data["private_key_saved_at"] = private_key_path

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteKeyPair(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="키페어를 삭제합니다."
        , request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"keypair_name": openapi.Schema(type=openapi.TYPE_STRING, description="삭제할 키페어 이름")},
            required=['keypair_name'],),
                         responses={200:'키페어 삭제 성공',400: 'Bad Request'})
    def delete(self, request):
        conn = openstack_connection()
        keypair_name = request.data.get('keypair_name')

        if not keypair_name:
            return Response({"Check the keypair name again."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            existing_keypair = conn.compute.find_keypair(keypair_name)
            if not existing_keypair:
                return Response({"Not found keypair. check again you want to delete"},
                                status=status.HTTP_404_NOT_FOUND)

            conn.compute.delete_keypair(keypair_name)
            return Response({"message": f"'{keypair_name}' Keypair deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListKeyPair(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="모든 키페어 정보를 조회합니다.",
        responses={
            200: openapi.Response(
                description="키페어 조회 성공",
                examples={
                    "application/json": {
                        "keypairs": [
                            {
                                "name": "example-keypair",
                                "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAr...",
                            },
                            {
                                "name": "another-keypair",
                                "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEBr...",
                            }
                        ]
                    }
                },
            ),
            500: openapi.Response(
                description="서버 에러",
                examples={
                    "application/json": {
                        "error": "Internal server error message"
                    }
                },
            ),
        },
        tags=["KeyPairs"]
    )
    def get(self, request):
        conn = openstack_connection()
        try:
            keypairs = conn.compute.keypairs()
            keypair_list = [{
                "name": keypair.name,
                "public_key": keypair.public_key,
            }
                for keypair in keypairs
            ]
            return Response({"keypairs": keypair_list}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
