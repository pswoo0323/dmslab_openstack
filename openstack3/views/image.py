import os
import tempfile
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
                description="name of the image to create",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                'disk_format',
                openapi.IN_FORM,
                description="디스크 형식 (아래 옵션 중 선택)",
                type=openapi.TYPE_STRING,
                enum=[
                    "ISO - 광학 디스크 이미지 (Optical Disk Image)",
                    "PLOOP - Virtuozzo/Parallels Loopback Disk",
                    "QCOW2 - QEMU 에뮬레이터 (Emulator)",
                    "Raw - 순수 디스크 이미지",
                    "VDI - 가상 디스크 이미지 (Virtual Disk Image)",
                    "VHD - 가상 하드 디스크 (Virtual Hard Disk)",
                    "VMDK - 가상 머신 디스크 (Virtual Machine Disk)",
                    "AKI - Amazon 커널 이미지 (Kernel Image)",
                    "AMI - Amazon 머신 이미지 (Machine Image)",
                    "ARI - Amazon 램디스크 이미지 (Ramdisk Image)"
                ],
                required=True,
            ),
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                description="image file",
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ])
    def post(self, request):
        conn = openstack_connection()  # OpenStack 연결
        image_name = request.data.get('image_name')
        disk_format = request.data.get('disk_format')
        uploaded_file = request.FILES.get('file')  # 업로드된 파일 가져오기

        if not all([image_name, disk_format, uploaded_file]):
            return Response({"error": "Please check the image name, disk format, and file."}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자가 선택한 디스크 형식에서 실제 형식 추출
        allowed_formats = {
            "ISO - 광학 디스크 이미지 (Optical Disk Image)": "iso",
            "PLOOP - Virtuozzo/Parallels Loopback Disk": "ploop",
            "QCOW2 - QEMU 에뮬레이터 (Emulator)": "qcow2",
            "Raw - 순수 디스크 이미지": "raw",
            "VDI - 가상 디스크 이미지 (Virtual Disk Image)": "vdi",
            "VHD - 가상 하드 디스크 (Virtual Hard Disk)": "vhd",
            "VMDK - 가상 머신 디스크 (Virtual Machine Disk)": "vmdk",
            "AKI - Amazon 커널 이미지 (Kernel Image)": "aki",
            "AMI - Amazon 머신 이미지 (Machine Image)": "ami",
            "ARI - Amazon 램디스크 이미지 (Ramdisk Image)": "ari",
        }

        if disk_format not in allowed_formats.keys():
            return Response({"error": "It is an unsupported disk format."}, status=status.HTTP_400_BAD_REQUEST)

        # 실제 형식으로 변환
        disk_format_value = allowed_formats[disk_format]

        try:
            # TemporaryDirectory를 사용하여 임시 디렉터리 생성
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)

                # 업로드된 파일을 임시 디렉터리에 저장
                with open(file_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                # OpenStack에 이미지 생성
                image = conn.image.create_image(
                    name=image_name,
                    data=open(file_path, 'rb'),
                    disk_format=disk_format_value,
                    container_format='bare'  # 기본값 사용
                )

            # TemporaryDirectory는 context manager를 벗어날 때 자동 삭제됨
            return Response({"image": image.to_dict()}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListImage(APIView):
    @swagger_auto_schema(operation_description="사용자가 사용할 이미지 조회",
                         responses={
                             200: openapi.Response(
                                 description="이미지 조회 성공",
                                 examples={
                                     "application/json": [
                                         {
                                             "name": "Ubuntu 20.04",
                                             "created_at": "2023-01-01T12:34:56Z"
                                         },
                                         {
                                             "name": "CentOS 7",
                                             "created_at": "2023-01-02T15:45:30Z"
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
                                 }
                             ),
                         },
                         tags=["Images"]
                         )
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

class DeleteImage(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="이미지 삭제 API. 관리자가 특정 이미지를 삭제할 수 있습니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["image_name"],
            properties={
                "image_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="삭제할 이미지의 이름"
                )
            },
            example={
                "image_name": "Ubuntu 20.04"
            }
        ),
        responses={
            200: openapi.Response(
                description="이미지 삭제 성공",
                examples={
                    "application/json": {
                        "message": "'Ubuntu 20.04' 이미지가 삭제되었습니다."
                    }
                },
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={
                    "application/json": {
                        "error": "삭제하고자 하는 이미지 이름을 확인해주세요."
                    }
                },
            ),
            404: openapi.Response(
                description="이미지를 찾을 수 없음",
                examples={
                    "application/json": {
                        "error": "이미지를 찾을 수 없습니다. 다시 확인해 주세요."
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
    def delete(self, request):
        conn = openstack_connection()
        image_name = request.data.get('image_name')

        if not image_name:
            return Response({"Please check the name of the image you want to delete."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            image = conn.image.find_image(image_name)
            if not image:
                return Response({"Image not found. Please check again."}, status=status.HTTP_404_NOT_FOUND)

            conn.image.delete_image(image_name)
            return Response({"message": f"'{image_name}' image deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
