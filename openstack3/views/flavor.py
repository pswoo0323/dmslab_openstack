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

class CreateFlavor(APIView):
    def post(self, request):
        conn = connection.from_config(cloud_name='default')
        flavor_name = request.data.get('flavor_name')
        ram = request.data.get('ram')  # RAM 크기 (MB)
        vcpus = request.data.get('vcpus')  # 가상 CPU 수
        disk = request.data.get('disk')  # 디스크 크기 (GB)

        if not all([flavor_name, ram, vcpus, disk]):
            return Response({"error": "flavor_name, ram, vcpus, and disk are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flavor = conn.compute.create_flavor(
                name=flavor_name,
                ram=ram,
                vcpus=vcpus,
                disk=disk
            )
            return Response({"flavor": flavor.to_dict()}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
