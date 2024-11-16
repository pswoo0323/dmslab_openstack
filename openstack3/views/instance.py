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

class CreateInstance(APIView):
    def post(self, request):
        conn = openstack_connection()
        server_name = request.data.get('server_name')
        flavor_id = request.data.get('flavor_id')
        image_id = request.data.get('image_id')
        network_name = request.data.get('network_name')

        if not all([server_name, flavor_id, image_id, network_name]):
            return Response({"error": "server_name, flaver_id, network_name을 다시 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        server = conn.compute.create_server(
            name=server_name,
            flavor_id=flavor_id,
            image_id=image_id,
            networks=[{"uuid": network_name}]
        )
        server = conn.compute.wait_for_server(server)
        return Response({"server": server.to_dict()}, status=status.HTTP_201_CREATED)

