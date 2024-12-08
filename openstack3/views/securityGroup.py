from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from openstack import connection


# OpenStack Connection
def openstack_connection():
    conn = connection.from_config(cloud_name='default')
    return conn


# Create Security Group
class CreateSecurityGroup(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Security_Group 이름'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the Security Group')
            },
            required=['name', 'description'],
        ),
        responses={201: 'Security Group Created', 400: 'Bad Request'}
    )
    def post(self, request):
        conn = openstack_connection()
        name = request.data.get('name')
        description = request.data.get('description')

        if not name or not description:
            return Response({"error": "Name and description are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            security_group = conn.network.create_security_group(name=name, description=description)
            return Response({
                "message": "Security Group Created Successfully",
                "id": security_group.id,
                "name": security_group.name,
                "description": security_group.description
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# List Security Groups
class ListSecurityGroups(APIView):
    def get(self, request):
        conn = openstack_connection()

        try:
            security_groups = conn.network.security_groups()
            security_groups_list = [
                {
                    "id": sg.id,
                    "name": sg.name,
                    "description": sg.description
                }
                for sg in security_groups
            ]
            return Response(security_groups_list, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Delete Security Group
class DeleteSecurityGroup(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'security_group_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the Security Group to delete')
            },
            required=['security_group_id'],
        ),
        responses={200: 'Security Group Deleted', 400: 'Bad Request'}
    )
    def delete(self, request):
        conn = openstack_connection()
        security_group_id = request.data.get('security_group_id')

        if not security_group_id:
            return Response({"error": "Security Group ID를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conn.network.delete_security_group(security_group_id, ignore_missing=True)
            return Response({"message": "Security Group 삭제가 완료되었습니다."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
