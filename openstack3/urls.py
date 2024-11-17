from django.urls import path
from openstack3.views.project_users import AdminUser, ProjectUserCreate, ProjectUserList, ProjectUserDelete, \
    CheckCacheView
from openstack3.views.projects import Create_Project, List_Project
from openstack3.views.network import CreateNetworkRequest, ManageNetworkRequest, PendingNetwork, UpdateNetwork, \
    DeleteNetwork
from openstack3.views.keypair import CreateKeyPair
from openstack3.views.flavor import CreateFlavor
from openstack3.views.image import CreateImage
from openstack3.views.instance import CreateInstance
from openstack3.views.users import UserRegistrationView, ApproveUserView, PendingApprovalUsersView, UserLoginView, \
    UserDetailView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # user
    path('register/', UserRegistrationView.as_view(), name='user_request'),
    path('approve/<uuid:user_id>/', ApproveUserView.as_view(), name='user_approval'),
    path('pending-approval-users/', PendingApprovalUsersView.as_view(), name='pending-approval-users'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('user/token/', TokenObtainPairView.as_view(), name='user-token'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='user-token-refresh'),
    path('user/detail/', UserDetailView.as_view(), name='user-detail'),

    # Projects
    path('project/create/', Create_Project.as_view(), name='project-create'),
    path('project/list/', List_Project.as_view(), name='project-list'),
    path('project/user/create/', ProjectUserCreate.as_view(), name='Project-user-create'),
    path('project/user/list/', ProjectUserList.as_view(), name='user-list'),
    path('project/user/delete/', ProjectUserDelete.as_view(), name='user-delete'),
    path('admin/user/', AdminUser.as_view(), name='admin-user'),

    # resources

    # network
    path('resources/network/request/', CreateNetworkRequest.as_view(), name='network-create'),
    path('resources/network/manage/', ManageNetworkRequest.as_view(), name='network-manage'),
    path('resources/network/pending/', PendingNetwork.as_view(), name='network-pending-users'),
    path('resources/network/update/', UpdateNetwork.as_view(), name='network-update'),
    path('resources/network/delete/', DeleteNetwork.as_view(), name='network-delete'),
    # keypair
    path('resources/keypair/', CreateKeyPair.as_view(), name='create-keypair'),
    # image
    path('resources/image/', CreateImage.as_view(), name='create-image'),
    # instance
    path('resources/instance/', CreateInstance.as_view(), name='create-instance'),
    # flavor
    path('resources/flavor/', CreateFlavor.as_view(), name='create-flavor'),

    # util
    path('cache/', CheckCacheView.as_view, name='check-cache'),
]
