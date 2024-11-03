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
class CreateNetwork(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'network': openapi.Schema(type=openapi.TYPE_STRING, description='Network'),
                'subnet': openapi.Schema(type=openapi.TYPE_STRING, description='Subnet'),
                'CIDR': openapi.Schema(type=openapi.TYPE_STRING, description='CIDR (형식: x.x.x.x/x)'),
                'gateway': openapi.Schema(type=openapi.TYPE_STRING, description='gateway_ip (형식: x.x.x.x)'),
            },
            required=['network', 'subnet', 'CIDR', 'gateway'],
        ),
        responses={
            201: 'ResourcesSerializer',  # 성공 시 ResourcesSerializer 형식으로 응답
            400: 'Bad Request',
        }
    )
    def post(self, request):
        conn = openstack_connection()
        network_name = request.data.get('network')
        subnet_name = request.data.get('subnet')
        gateway_ip = request.data.get('gateway')
        cidr = request.data.get('CIDR')

        # CIDR 및 Gateway IP 형식 검증
        cidr_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$"
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

        if not network_name or not subnet_name or not cidr or not gateway_ip:
            return Response({"error": "네트워크, 서브넷, CIDR, Gateway 입력을 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(cidr_pattern, cidr):
            return Response({"error": "CIDR 형식이 올바르지 않습니다. 형식: x.x.x.x/x"}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(ip_pattern, gateway_ip):
            return Response({"error": "Gateway IP 형식이 올바르지 않습니다. 형식: x.x.x.x"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 네트워크 생성
            network = conn.network.create_network(name=network_name)
            # 서브넷 생성
            subnet = conn.network.create_subnet(
                name=subnet_name,
                network_id=network.id,
                ip_version='4',
                cidr=cidr,
                gateway_ip=gateway_ip
            )

            return Response({
                "network_id": network.id,
                "network_name": network.name,
                "subnet_id": subnet.id,
                "subnet_name": subnet.name
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateKeyPair(APIView):
    def post(self, request):
        conn = openstack_connection()
        key_name = request.data.get('key_name')

        if not key_name:
            return Response({"error": "키 이름 오류입니다."}, status=status.HTTP_400_BAD_REQUEST)

        keypair = conn.compute.create_keypair(name=key_name)
        return Response({"keypair": keypair.to_dict()}, status=status.HTTP_201_CREATED)


class CreateImage(APIView):
    def post(self, request):
        conn = openstack_connection()
        image_name = request.data.get('image_name')
        filename = request.data.get('filename')

        if not all([image_name, filename]):
            return Response({"error": "이미지명과 파일명을 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        image = conn.image.create_image(name=image_name, filename=filename)
        return Response({"image": image.to_dict()}, status=status.HTTP_201_CREATED)

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

