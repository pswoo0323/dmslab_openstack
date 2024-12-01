import os
from turtledemo.sorting_animate import start_ssort

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openstack import connection

from config.settings import SWAGGER_SETTINGS


def openstack_connection():
    conn = connection.from_config(cloud_name='default')

    return conn


class CreateImage(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser]  # 파일 업로드를 처리하기 위한 파서 지정
    @swagger_auto_schema(
        operation_description="관리자가 파일을 업로드하여 이미지를 생성합니다.",
        manual_parameters=[
            openapi.Parameter(
                'image_name',
                openapi.IN_FORM,
                description="생성할 이미지의 이름",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                description="이미지 파일",
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ])
    def post(self, request):
        conn = openstack_connection()
        image_name = request.data.get('image_name')
        uploaded_file = request.FILES.get('file')  # 업로드된 파일 가져오기

        if not all([image_name, uploaded_file]):
            return Response({"error": "이미지명과 파일을 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 파일을 로컬 디스크에 임시 저장
            file_path = os.path.join('/tmp', uploaded_file.name)
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # OpenStack에 이미지 생성
            image = conn.image.create_image(
                name=image_name,
                data=open(file_path, 'rb'),  # 저장된 파일을 읽어서 전달
                disk_format='qcow2',  # 이미지 형식 ( raw, vmdk, vdi, vhd, vhdx 등 필요에 따라 수정 가능)
                #QEMU Copy-On-Write 2 형식, 관리자가 지원하는 디스크 형식을 미리 확인해야 함
                container_format='bare'#ovf, ami가능
            )

            # 업로드한 이미지파일 로컬에서는 삭제(공간 낭비 하니깐)
            os.remove(file_path)

            return Response({"image": image.to_dict()}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListImage(APIView):
    @swagger_auto_schema(operation_description="사용자가 사용할 이미지 조회")
    def get(self, request):
        conn = openstack_connection()

        try:
            # Retrieve all images
            images = conn.image.images()
            images_list = [
                {
                    "name": image.name,
                    "created_at": image.created_at,
                }
                for image in images
            ]
            return Response(images_list, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
