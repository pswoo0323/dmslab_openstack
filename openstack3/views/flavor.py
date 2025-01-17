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
        operation_description="관리자가 Flavor을 생성합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'flavor_name': openapi.Schema(type=openapi.TYPE_STRING, description='Flavor name'),
                'ram': openapi.Schema(type=openapi.TYPE_INTEGER, description='RAM size in MB'),
                'vcpus': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of vCPUs'),
                'disk': openapi.Schema(type=openapi.TYPE_INTEGER, description='Disk size in GB(Default: 0)'),
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
        disk = request.data.get('disk', 0)  # 디스크 크기 (GB)(기본값 0)

        if not all([flavor_name, ram, vcpus]):
            return Response({"error": "flavor_name, ram, vcpus are required."}, status=status.HTTP_400_BAD_REQUEST)

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


class ListFlavors(APIView):
    """Flavor 조회 API"""
    @swagger_auto_schema(
        operation_description="사용자가 flavor 리스트를 조회합니다.",
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
        responses={200: "flavor deleted successfully.", 404: "flavor not found"},
    )
    def delete(self, request):
        conn = openstack_connection()
        flavor_id = request.data.get('flavor_id')  # 삭제할 Flavor의 ID

        if not flavor_id:
            return Response({"error": "Please check again the Flavor ID."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Flavor 삭제
            flavor = conn.compute.get_flavor(flavor_id)
            if not flavor:
                return Response({"error": "The specified flavor could not be found."}, status=status.HTTP_404_NOT_FOUND)

            conn.compute.delete_flavor(flavor_id)
            return Response({"message": f"'{flavor_id}' Flavor deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
