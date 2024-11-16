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


class DeleteNetwork(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'network_id': openapi.Schema(type=openapi.TYPE_STRING, description='삭제할 네트워크 아이디')},
            required=['network_id'],
        ),
        responses={200: '네트워크 삭제 성공', 400: 'Bad Request'}
    )
    def delete(self, request):
        conn = openstack_connection()
        network_id = request.data.get('network_id')

        if not network_id:
            return Response({"error": "Network ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conn.network.delete_network(network_id, ignore_missing=True)
            return Response({"message": "네트워크 삭제에 성공하였습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateNetwork(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'network_id': openapi.Schema(type=openapi.TYPE_STRING, description='최신화할 네트워크 ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='New network name (optional)'),
                'admin_state_up': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Admin state (optional)'),
            },  #admin_state_up: True는 네트워크 리소스가 활성화 되어 있어 사용할 수 있는 상태
                #                False는 비활성화 되어 있어 사용할 수 없는 상태
            required=['network_id'],
        ),
        responses={200: 'Network updated successfully', 400: 'Bad Request'}
    )
    def patch(self, request):
        conn = openstack_connection()
        network_id = request.data.get('network_id')
        name = request.data.get('name')
        admin_state_up = request.data.get('admin_state_up')

        if not network_id:
            return Response({"error": "Network ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            network = conn.network.update_network(network_id, name=name, admin_state_up=admin_state_up)
            return Response({"network_id": network.id, "network_name": network.name, "admin_state_up": network.admin_state_up}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
