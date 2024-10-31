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