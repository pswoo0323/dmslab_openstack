from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from openstack import connection
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def openstack_connection():
    conn = connection.from_config(cloud_name='default')
    return conn


class CreateFlavor(APIView):
    permission_classes = [IsAdminUser]  # 관리자만 접근 가능
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'flavor_name': openapi.Schema(type=openapi.TYPE_STRING, description='Flavor name'),
                'ram': openapi.Schema(type=openapi.TYPE_INTEGER, description='RAM size in MB'),
                'vcpus': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of vCPUs'),
                'disk': openapi.Schema(type=openapi.TYPE_INTEGER, description='Disk size in GB'),
            },
            required=['flavor_name', 'ram', 'vcpus', 'disk'],
        ),
        responses={
            201: 'Flavor created successfully.',
            400: 'Bad Request',
            500: 'Internal Server Error',
        }
    )
    def post(self, request):
        conn = openstack_connection()
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
            return Response({"message": "Flavor created successfully.", "flavor": flavor.to_dict()}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateFlavor(APIView):
    """Flavor 수정 API"""
    permission_classes = [IsAdminUser]  # 관리자만 접근 가능
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'flavor_id': openapi.Schema(type=openapi.TYPE_STRING, description='Flavor ID'),
                'ram': openapi.Schema(type=openapi.TYPE_INTEGER, description='New RAM size in MB'),
                'vcpus': openapi.Schema(type=openapi.TYPE_INTEGER, description='New number of vCPUs'),
                'disk': openapi.Schema(type=openapi.TYPE_INTEGER, description='New disk size in GB'),
            },
            required=['flavor_id'],
        ),
        responses={
            200: 'Flavor updated successfully.',
            400: 'Bad Request',
            404: 'Flavor not found.',
            500: 'Internal Server Error',
        }
    )
    def patch(self, request):
        conn = openstack_connection()
        flavor_id = request.data.get('flavor_id')
        ram = request.data.get('ram')
        vcpus = request.data.get('vcpus')
        disk = request.data.get('disk')

        if not flavor_id:
            return Response({"error": "flavor_id를 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flavor = conn.compute.get_flavor(flavor_id)
            if not flavor:
                return Response({"error": "Flavor를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # Flavor 업데이트는 일반적으로 지원되지 않지만 예를 위해 로직 추가
            flavor = conn.compute.update_flavor(
                flavor,
                ram=ram or flavor.ram,
                vcpus=vcpus or flavor.vcpus,
                disk=disk or flavor.disk,
            )
            return Response({"message": "Flavor가 업데이트 되었습니다.", "flavor": flavor.to_dict()}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListFlavors(APIView):
    """Flavor 조회 API"""
    @swagger_auto_schema(
        responses={
            200: 'Flavor list retrieved successfully.',
            500: 'Internal Server Error',
        }
    )
    def get(self, request):
        conn = openstack_connection()
        try:
            flavors = conn.compute.flavors()
            flavor_list = [
                {
                    "id": flavor.id,
                    "name": flavor.name,
                    "ram": flavor.ram,
                    "vcpus": flavor.vcpus,
                    "disk": flavor.disk,
                }
                for flavor in flavors
            ]
            return Response({"flavors": flavor_list}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteFlavor(APIView):
    """Flavor 삭제 API"""
    permission_classes = [IsAdminUser]  # 관리자만 접근 가능
    @swagger_auto_schema(
        operation_description="관리자가 Flavor를 삭제합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'flavor_id': openapi.Schema(type=openapi.TYPE_STRING, description='Flavor ID to delete'),
            },
            required=['flavor_id'],
        ),
    )
    def delete(self, request):
        conn = openstack_connection()
        flavor_id = request.data.get('flavor_id')  # 삭제할 Flavor의 ID

        if not flavor_id:
            return Response({"error": "Flavor ID를 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Flavor 삭제
            flavor = conn.compute.get_flavor(flavor_id)
            if not flavor:
                return Response({"error": "Flavor를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            conn.compute.delete_flavor(flavor_id)
            return Response({"message": "Flavor가 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
