from tkinter.font import names

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openstack import connection
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.cache import cache
import re
from openstack3.models.resources import Resources
from openstack3.serializers.resourceSerializer import ResourcesSerializer


def openstack_connection():
    conn = connection.from_config(cloud_name='default')
    return conn


class CreateNetworkRequest(APIView):  # 사용자가 네트워크 요청
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="사용자가 사용하고자 하는 네트워크를 관리자에게 요청합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'network': openapi.Schema(type=openapi.TYPE_STRING, description='Network'),
                'subnet': openapi.Schema(type=openapi.TYPE_STRING, description='Subnet'),
                'CIDR': openapi.Schema(type=openapi.TYPE_STRING, description='CIDR (형식: x.x.x.x/x)'),
                'gateway': openapi.Schema(type=openapi.TYPE_STRING, description='Gateway IP (형식: x.x.x.x)'),
                'requested_by': openapi.Schema(type=openapi.TYPE_STRING, description='Requested by user'),
            },
            required=['network', 'subnet', 'CIDR', 'gateway', 'requested_by'],
        ),
        responses={201: 'Request submitted successfully', 400: 'Bad Request'}
    )
    def post(self, request):
        # 요청 데이터 가져오기
        network_name = request.data.get('network')
        subnet_name = request.data.get('subnet')
        cidr = request.data.get('CIDR')
        gateway_ip = request.data.get('gateway')
        requested_by = request.data.get('requested_by')
        # CIDR 및 Gateway IP 형식 검증
        cidr_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$"
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

        if not all([network_name, subnet_name, cidr, gateway_ip, requested_by]):
            return Response({"error": "Please check the input."}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(cidr_pattern, cidr):
            return Response({"error": "The CIDR format is invalid. format: x.x.x.x/x"}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(ip_pattern, gateway_ip):
            return Response({"error": "The gatewayIP format is invalid. format: x.x.x.x"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Resources 모델에 요청 저장
            resource = Resources.objects.create(
                network=network_name,
                subnet=subnet_name,
                CIDR=cidr,
                gateway=gateway_ip,
                requested_by=requested_by,
                status='pending'  # 요청 상태는 기본값으로 'pending'

            )
            return Response({"message": "The request has been successfully submitted.", "request_id": resource.id},
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ManageNetworkRequest(APIView):  # 관리자가 네트워크 요청을 수락or거절 /default는 대기
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="관리자가 네트워크 요청을 수락하거나 거절합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'request_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='요청 ID'
                ),
                'action': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="요청 작업 ('approve' 또는 'reject')"
                ),
            },
            required=['request_id', 'action'],
            example={
                "request_id": 1,
                "action": "approve"
            },
        ),
        responses={
            200: openapi.Response(
                description="요청 처리 성공",
                examples={
                    "application/json": {
                        "message": "네트워크 요청이 승인되었습니다.",
                        "network_id": "1234abcd",
                        "subnet_id": "5678efgh"
                    }
                },
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={
                    "application/json": {
                        "error": "Request ID and action are required."
                    }
                },
            ),
            404: openapi.Response(
                description="요청을 찾을 수 없음",
                examples={
                    "application/json": {
                        "error": "Request not found."
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
    )
    def post(self, request):
        request_id = request.data.get('request_id')
        action = request.data.get('action')

        if not all([request_id, action]):
            return Response({"error": "Request ID and action are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Resources 모델에서 요청 데이터 가져오기
            network_request = Resources.objects.get(id=request_id)

            if action == 'approve':
                # OpenStack 네트워크 생성 로직
                conn = openstack_connection()
                network = conn.network.create_network(name=network_request.network)
                subnet = conn.network.create_subnet(
                    name=network_request.subnet,
                    network_id=network.id,
                    ip_version='4',
                    cidr=network_request.CIDR,
                    gateway_ip=network_request.gateway
                )
                network_request.status = 'approved'
                network_request.save()

                return Response({
                    "message": "네트워크 요청이 승인되었습니다.",
                    "network_id": network.id,
                    "subnet_id": subnet.id
                }, status=status.HTTP_200_OK)

            elif action == 'reject':
                # 요청 상태 거절
                network_request.status = 'rejected'
                network_request.save()
                return Response({"message": "네트워크 요청이 거절되었습니다."}, status=status.HTTP_200_OK)

            else:
                return Response({"error": "Invalid action. Use 'approve' or 'reject'."},
                                status=status.HTTP_400_BAD_REQUEST)

        except Resources.DoesNotExist:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteNetwork(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="네트워크를 삭제합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'network_id': openapi.Schema(type=openapi.TYPE_STRING, description='삭제할 네트워크 아이디')},
            required=['network_id'],
            example={
                "network_id": "1234abcd"
            },
        ),
        responses={200: '네트워크 삭제 성공', 400: 'Bad Request'}
    )
    def delete(self, request):
        conn = openstack_connection()
        network_id = request.data.get('network_id')

        if not network_id:
            return Response({"error": "Network ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # OpenStack 네트워크 삭제
            deleted = conn.network.delete_network(network_id, ignore_missing=True)

            if deleted:
                # Resources 모델에서 데이터 삭제
                Resources.objects.filter(network_id=network_id).delete()

                return Response({"message": f"'{network_id}' Network deleted successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateNetwork(APIView):
    permission_classes = [IsAdminUser]
    @swagger_auto_schema(
        operation_description="관리자가 네트워크를 최신화 합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'network_id': openapi.Schema(type=openapi.TYPE_STRING, description='최신화할 네트워크 ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='New network name (optional)'),
                'admin_state_up': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Admin state (optional)'),
            },  # admin_state_up: True는 네트워크 리소스가 활성화 상태
               # False는 비활성화 상태
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
            return Response({"error": "Network ID를 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # OpenStack 네트워크 업데이트
            network = conn.network.find_network(network_id, ignore_missing=True)
            if not network:
                return Response({"error": "해당 네트워크를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # 네트워크 업데이트
            updated_network = conn.network.update_network(
                network,
                name=name,
                admin_state_up=admin_state_up
            )

            return Response({
                "network_id": updated_network.id,
                "network_name": updated_network.name,
                "admin_state_up": updated_network.admin_state_up
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PendingNetwork(APIView):  # 관리자가 network요청을 확인하는 api
    permission_classes = [IsAdminUser]
    @swagger_auto_schema(
        operation_description="Pending 상태의 네트워크 요청을 확인합니다.",
        responses={
            200: openapi.Response(
                description="성공적으로 요청 목록을 반환합니다.",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "network": "default-network",
                            "subnet": "default-subnet",
                            "CIDR": "192.168.1.0/24",
                            "gateway": "192.168.1.1",
                            "status": "pending",
                            "created_at": "2023-01-01T12:00:00Z",
                            "requested_by": "admin"
                        },
                        {
                            "id": 2,
                            "network": "custom-network",
                            "subnet": "custom-subnet",
                            "CIDR": "10.0.0.0/24",
                            "gateway": "10.0.0.1",
                            "status": "pending",
                            "created_at": "2023-01-02T14:30:00Z",
                            "requested_by": "user1"
                        }
                    ]
                },
            ),
            403: openapi.Response(
                description="권한 없음",
                examples={
                    "application/json": {
                        "error": "You do not have permission to perform this action."
                    }
                },
            ),
        },
    )
    def get(self, request):
        # Pending 상태의 요청 가져오기
        pending_requests = Resources.objects.filter(status='pending', deleted_at__isnull=True)

        # 요청 데이터 직렬화
        serializer = ResourcesSerializer(pending_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
