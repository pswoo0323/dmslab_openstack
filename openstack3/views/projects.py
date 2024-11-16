from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openstack import connection

def openstack_connection():
    conn = connection.from_config(cloud_name='default')

    return conn

class Create_Project(APIView):
    def post(self, request):
        conn = openstack_connection()
        project_name =  request.data.get('project_name')

        if not project_name:
            return Response({"error": "프로젝트 이름을 기재해 주세요."},
                            status=status.HTTP_400_BAD_REQUEST)

        project = conn.identity.create_project(
            name = project_name,
            domain_id='default',
            enabled=True)

        return Response({
            "project_id" : project.id, "project_name": project_name
        }, status=status.HTTP_201_CREATED)

class List_Project(APIView):
    def get(self, request):
        conn = openstack_connection()
        projects = conn.identity.projects()
        project_list = [{"project_name": project.name, "project_id": project.id} for project in projects]
        return Response(project_list, status=status.HTTP_200_OK)