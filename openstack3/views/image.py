from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openstack import connection
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import re
from openstack3.serializers.resourceSerializer import ResourcesSerializer

def openstack_connection():
    conn = connection.from_config(cloud_name='default')

    return conn

class CreateImage(APIView):
    def post(self, request):
        conn = openstack_connection()
        image_name = request.data.get('image_name')
        filename = request.data.get('filename')

        if not all([image_name, filename]):
            return Response({"error": "이미지명과 파일명을 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        image = conn.image.create_image(name=image_name, filename=filename)
        return Response({"image": image.to_dict()}, status=status.HTTP_201_CREATED)
