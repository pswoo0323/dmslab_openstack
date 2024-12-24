from http.client import responses

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, OutstandingToken, BlacklistedToken
from openstack3.serializers.userSerializer import UserRegistrationSerializer, UserLoginSerializer
from openstack3.models.users import CustomUser
from openstack3.serializers.userSerializer import UserPendingApprovalSerializer
from openstack3.utils.token import get_cached_openstack_token


class UserRegistrationView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'userID': openapi.Schema(type=openapi.TYPE_STRING),
                'userPW': openapi.Schema(type=openapi.TYPE_STRING),
                'userEmail': openapi.Schema(type=openapi.TYPE_STRING),
                'userName': openapi.Schema(type=openapi.TYPE_STRING),
                'userRole': openapi.Schema(type=openapi.TYPE_STRING,
                                           enum=['학생', '석사', '박사', '교수', '기타'],
                                           ),
            },
            required=['userID', 'userPW', 'userEmail', 'userName', 'userRole'],
        ),
        responses={
            201: '회원가입 요청 완료. 관리자 승인 대기.',
            404: '404_Bad Request'
        })
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "회원가입 요청이 완료되었습니다. 관리자의 승인을 기다려주세요."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveUserView(APIView):
    permission_classes = [IsAdminUser]  # 관리자만 접근 가능
    @swagger_auto_schema(
        operation_description="관리자가 사용 신청한 유저를 확인하고 승인합니다.",
        request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'uuid_userID': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['uuid_userID'],
        responses={
            201: '[userID] 사용자가 승인되었습니다.',
            404: '해당 사용자를 찾을 수 없습니다.'
        }
    ))
    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(uuid=user_id)
            user.approve = True
            user.save()
            return Response({"message": f"{user.userID} 사용자가 승인되었습니다."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "해당 사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


class PendingApprovalUsersView(APIView):
    permission_classes = [IsAdminUser]  # 관리자만 접근 가능

    @swagger_auto_schema(
        operation_description="승인 대기 중인 사용자 목록을 조회합니다.",
        responses={200: UserPendingApprovalSerializer(many=True)}
    )
    def get(self, request):
        # 승인되지 않은 사용자만 필터링
        pending_users = CustomUser.objects.filter(approve=False)
        serializer = UserPendingApprovalSerializer(pending_users, many=True)
        return Response(serializer.data)


class UserLoginView(APIView):
    @swagger_auto_schema(
        operation_description="승인된 사용자가 로그인하여 OpenStack 토큰을 발급받습니다.",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="로그인 성공"),
            400: "Bad Request"
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            token = get_cached_openstack_token(user.userID)

            return Response({
                "message": f"{user.userID}님, 로그인에 성공하였습니다.",
                "access_token": access_token,
                "refresh_token": str(refresh),
                "openstack_token": token,
                "userID": user.userID,
                "userEmail": user.userEmail
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]  # jwt인증된 사람만

    def get(self, request):
        user = request.user  # jwt에서 디코딩된 사용자 정보

        return Response({
            "user_id": user.userID,
            "username": user.userName,
            "email": user.userEmail
        })


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="사용자가 로그아웃하여 Refresh Token을 블랙리스트에 추가",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description="사용자의 Refresh Token")
            },
            required=['refresh_token']
        ),
        responses={
            205: "로그아웃 성공. Refresh Token이 블랙리스트에 추가되었습니다.",
            400: "Bad Request. Refresh Token을 확인해주세요.",
            401: "Unauthorized. 인증되지 않은 사용자입니다.",
        }
    )
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error":"Refresh Token이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "로그아웃이 완료되었습니다"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
