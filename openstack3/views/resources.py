from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openstack import connection
from openstack3.models import User

def openstack_connection():
    conn = connection.from_config(cloud_name='default')

    return conn

#network, subnet 생성
class CreateNetwork(APIView):
    def post(self, request):
        conn = openstack_connection()
        network_name = request.data.get('network_name')
        subnet_name = request.data.get('subnet_name')
        cidr = request.data.get('cidr')

        if not network_name or not subnet_name or not cidr:
            return Response({"error": "네트워크, 서브넷, CIDR입력을 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 네트워크 생성
            network = conn.network.create_network(name=network_name)
            # 서브넷 생성
            subnet = conn.network.create_subnet(
                name=subnet_name,
                network_id=network.id,
                ip_version='4',
                cidr=cidr,
                gateway_ip=cidr.split('.')[0] + '.' + cidr.split('.')[1] + '.' + cidr.split('.')[2] + '.1'
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

