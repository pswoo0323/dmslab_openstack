# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from openstack import connection
#
# def openstack_connection():
#     conn = connection.from_config(cloud_name='default')
#
#     return conn
#
# class Create_Project(APIView):
#     def post(self, request):
#         conn = openstack_connection()
#         project_name =  request.data.get('project_name')
#
#         if not project_name:
#             return Response({"error": "프로젝트 이름을 기재해 주세요."},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         project = conn.identity.create_project(
#             name = project_name,
#             domain_id='default',
#             enabled=True)
#
#         return Response({
#             "project_id" : project.id, "project_name": project_name
#         }, status=status.HTTP_201_CREATED)
#
# class List_Project(APIView):
#     def get(self, request):
#         conn = openstack_connection()
#         projects = conn.identity.projects()
#         project_list = [{"project_name": project.name, "project_id": project.id} for project in projects]
#         return Response(project_list, status=status.HTTP_200_OK)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from openstack import connection
from rest_framework.permissions import IsAdminUser, IsAuthenticated


# OpenStack 연결 함수
def openstack_connection():
    conn = connection.from_config(cloud_name="default")
    return conn


class CreateProject(APIView):

    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="새로운 OpenStack 프로젝트를 생성합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project_name': openapi.Schema(type=openapi.TYPE_STRING, description='프로젝트 이름'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='프로젝트 설명 (선택 사항)', default=''),
                'domain_id': openapi.Schema(type=openapi.TYPE_STRING, description='도메인 ID (선택 사항)', default='default'),
            },
            required=['project_name'],
        ),
        responses={
            201: openapi.Response(
                description="프로젝트 생성 성공",
                examples={
                    "application/json": {
                        "message": "프로젝트가 성공적으로 생성되었습니다.",
                        "project_id": "abc123",
                        "project_name": "example_project"
                    }
                },
            ),
            400: "Bad Request",
            500: "Internal Server Error",
        }
    )
    def post(self, request):
        conn = openstack_connection()
        project_name = request.data.get('project_name')
        description = request.data.get('description', '')
        domain_id = request.data.get('domain_id', 'default')

        if not project_name:
            return Response({"error": "Project name is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 프로젝트 생성
            project = conn.identity.create_project(
                name=project_name,
                description=description,
                domain_id=domain_id,
            )
            return Response(
                {
                    "message": "Project created successfully.",
                    "project_id": project.id,
                    "project_name": project.name,
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteProject(APIView):
    permission_classes = [IsAdminUser]  # 관리자만 접근 가능

    @swagger_auto_schema(
        operation_description="특정 OpenStack 프로젝트를 삭제합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project_id': openapi.Schema(type=openapi.TYPE_STRING, description='삭제할 프로젝트 ID'),
            },
            required=['project_id'],
        ),
        responses={
            200: openapi.Response(
                description="프로젝트 삭제 성공",
                examples={
                    "application/json": {"message": "Project deleted successfully."}
                },
            ),
            400: "Bad Request",
            404: "Project Not Found",
            500: "Internal Server Error",
        }
    )
    def delete(self, request):
        conn = openstack_connection()
        project_id = request.data.get('project_id')

        if not project_id:
            return Response({"error": "project_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # 프로젝트 확인
            project = conn.identity.find_project(project_id)
            if not project:
                return Response({"error": "The specified project cannot be found."}, status=status.HTTP_404_NOT_FOUND)

            # 프로젝트 삭제
            conn.identity.delete_project(project_id, ignore_missing=True)
            return Response({"message": f"'{project_id}' Project deleted successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListProjects(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="OpenStack에서 프로젝트 리스트를 확인합니다.",
        responses={
            200: openapi.Response(
                description="프로젝트 리스트 조회 성공",
                examples={
                    "application/json": [
                        {
                            "id": "1234abcd",
                            "name": "Test Project 1"
                        },
                        {
                            "id": "5678efgh",
                            "name": "Test Project 2"
                        }
                    ]
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
            projects = conn.identity.projects()
            list_projects = [{
                "id": project.id,
                "name": project.name,
            }
                for project in projects
            ]
            return Response(list_projects, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
