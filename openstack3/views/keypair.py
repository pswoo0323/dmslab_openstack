from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openstack import connection
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import re
from openstack3.serializer import ResourcesSerializer

def openstack_connection():
    conn = connection.from_config(cloud_name='default')

    return conn


class CreateKeyPair(APIView):

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
        key_name = request.data.get('key_name')
        public_key = request.data.get('public_key')

        if not key_name:
            return Response({"error": "키 이름 오류입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 키페어 생성 (public_key는 선택적)
        keypair = conn.compute.create_keypair(name=key_name, public_key=public_key)

        return Response({"keypair": keypair.to_dict()}, status=status.HTTP_201_CREATED)
