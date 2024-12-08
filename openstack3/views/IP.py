from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from openstack3.models.IP import IPRequest


class RequestIP(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'request_type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of IP ('public_ip' or 'vpn_ip')"),
                'server_name': openapi.Schema(type=openapi.TYPE_STRING, description='Associated Server Name'),
                'network_name': openapi.Schema(type=openapi.TYPE_STRING, description='External Network Name'),
                'requested_by': openapi.Schema(type=openapi.TYPE_STRING, description='Requested by User'),
            },
            required=['request_type', 'server_name', 'network_name', 'requested_by'],
        ),
        responses={201: 'IP request submitted successfully', 400: 'Bad Request'}
    )
    def post(self, request):
        request_type = request.data.get('request_type')
        server_name = request.data.get('server_name')
        network_name = request.data.get('network_name')
        requested_by = request.data.get('requested_by')

        if not all([request_type, server_name, network_name, requested_by]):
            return Response({"error": "모든 필드값을 넣어주세요."}, status=status.HTTP_400_BAD_REQUEST)

        if request_type not in ['public_ip', 'vpn_ip']:
            return Response({"error": "유효하지 않은 요청 타입입니다. Use 'public_ip' or 'vpn_ip'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ip_request = IPRequest.objects.create(
                request_type=request_type,
                server_name=server_name,
                network_name=network_name,
                requested_by=requested_by,
                status='pending'
            )
            return Response({"message": "IP request submitted successfully.", "request_id": ip_request.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from openstack import connection

def openstack_connection():
    conn = connection.from_config(cloud_name='default')
    return conn


class ManageIPRequest(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'request_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Request ID'),
                'action': openapi.Schema(type=openapi.TYPE_STRING, description="Action ('approve' or 'reject')"),
            },
            required=['request_id', 'action'],
        ),
        responses={200: 'Request processed successfully', 400: 'Bad Request'}
    )
    def post(self, request):
        request_id = request.data.get('request_id')
        action = request.data.get('action')

        if not all([request_id, action]):
            return Response({"error": "Request ID and action are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ip_request = IPRequest.objects.get(id=request_id)

            if action == 'approve':
                conn = openstack_connection()
                if ip_request.request_type == 'public_ip':
                    # Create and assign Public IP
                    network = conn.network.find_network(ip_request.network_name)
                    if not network:
                        return Response({"error": f"Network '{ip_request.network_name}'를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

                    floating_ip = conn.network.create_ip(floating_network_id=network.id)
                    ip_request.ip_address = floating_ip.floating_ip_address

                elif ip_request.request_type == 'vpn_ip':
                    # Placeholder for VPN IP allocation logic
                    ip_request.ip_address = "192.168.1.1"  # Example IP for demonstration

                ip_request.status = 'approved'
                ip_request.save()
                return Response({"message": "요청이 성공적으로 승인되었습니다.", "ip_address": ip_request.ip_address}, status=status.HTTP_200_OK)

            elif action == 'reject':
                ip_request.status = 'rejected'
                ip_request.save()
                return Response({"message": "요청이 성공적으로 거절되었습니다."}, status=status.HTTP_200_OK)

            else:
                return Response({"error": "'approve' or 'reject'를 선택하여 주세요."}, status=status.HTTP_400_BAD_REQUEST)

        except IPRequest.DoesNotExist:
            return Response({"error": "요청을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListIPRequests(APIView):
    def get(self, request):
        requests = IPRequest.objects.all()
        request_data = [
            {
                "id": req.id,
                "request_type": req.request_type,
                "server_name": req.server_name,
                "network_name": req.network_name,
                "ip_address": req.ip_address,
                "status": req.status,
                "requested_by": req.requested_by,
                "created_at": req.created_at,
            }
            for req in requests
        ]
        return Response(request_data, status=status.HTTP_200_OK)
