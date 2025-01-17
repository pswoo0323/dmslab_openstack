from rest_framework.permissions import IsAuthenticated
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

class CreateInstance(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="새로운 인스턴스를 생성합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'server_name': openapi.Schema(type=openapi.TYPE_STRING, description='인스턴스 이름'),
                'flavor_id': openapi.Schema(type=openapi.TYPE_STRING, description='Flavor ID'),
                'image_id': openapi.Schema(type=openapi.TYPE_STRING, description='Image ID'),
                'network_name': openapi.Schema(type=openapi.TYPE_STRING, description='Network Name (UUID)'),
            },
            required=['server_name', 'flavor_id', 'image_id', 'network_name'],
        ),
        responses={
            201: openapi.Response(
                description="인스턴스 생성 성공",
                examples={
                    "application/json": {"server": "인스턴스 상세 정보"}
                },
            ),
            400: "잘못된 요청",
            500: "서버 에러",
        }
    )
    def post(self, request):
        conn = openstack_connection()
        server_name = request.data.get('server_name')
        flavor_id = request.data.get('flavor_id')
        image_id = request.data.get('image_id')
        network_name = request.data.get('network_name')

        if not all([server_name, flavor_id, image_id, network_name]):
            return Response({"error": "Please double-check the server name, flavor ID, and network name."}, status=status.HTTP_400_BAD_REQUEST)

        server = conn.compute.create_server(
            name=server_name,
            flavor_id=flavor_id,
            image_id=image_id,
            networks=[{"uuid": network_name}]
        )
        server = conn.compute.wait_for_server(server)
        return Response({"server": server.to_dict()}, status=status.HTTP_201_CREATED)

class ListInstances(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="모든 인스턴스 정보를 조회합니다.",
        responses={
            200: openapi.Response(
                description="인스턴스 조회 성공",
                examples={
                    "application/json": {
                        "instances": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "name": "test-instance-1",
                                "status": "ACTIVE"
                            },
                            {
                                "id": "789e4567-e89b-12d3-a456-426614174001",
                                "name": "test-instance-2",
                                "status": "SHUTOFF"
                            }
                        ]
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
    def get(self, request):
        conn = openstack_connection()

        try:
            # 모든 인스턴스 조회
            servers = conn.compute.servers()
            instance_list = [
                {"id": server.id, "name": server.name, "status": server.status}
                for server in servers
            ]
            return Response({"instances": instance_list}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteInstance(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="특정 인스턴스를 삭제.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'instance_id': openapi.Schema(type=openapi.TYPE_STRING, description='삭제할 인스턴스의 ID'),
            },
            required=['instance_id'],
        ),
        responses={
            200: openapi.Response(
                description="인스턴스 삭제 성공",
                examples={
                    "application/json": {"message": "Instance deleted successfully."}
                },
            ),
            400: "잘못된 요청",
            404: "인스턴스를 찾을 수 없습니다.",
            500: "서버 에러",
        }
    )
    def delete(self, request):
        conn = openstack_connection()
        instance_id = request.data.get('instance_id')

        if not instance_id:
            return Response({"Please check the instance ID you want to delete"},status=status.HTTP_400_BAD_REQUEST)
        try:#인스턴스 존재 확인
            server = conn.compute.server(instance_id)
            if not server:
                return Response({"error":"Instance not found. Please check again"},status = status.HTTP_404_NOT_FOUND)
            conn.compute.delete_server(instance_id)
            return Response({"message":"Instance deleted successfully"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"errpr": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)