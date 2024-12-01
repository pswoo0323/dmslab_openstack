from django.urls import path

from openstack3.views.IP import RequestIP, ListIPRequests, ManageIPRequest
from openstack3.views.project_users import AdminUser, ProjectUserCreate, ProjectUserList, ProjectUserDelete, \
    CheckCacheView
from openstack3.views.projects import Create_Project, List_Project
from openstack3.views.network import CreateNetworkRequest, ManageNetworkRequest, PendingNetwork, UpdateNetwork, \
    DeleteNetwork
from openstack3.views.securityGroup import CreateSecurityGroup, ListSecurityGroups, DeleteSecurityGroup
from openstack3.views.keypair import CreateKeyPair
from openstack3.views.flavor import CreateFlavor
from openstack3.views.image import CreateImage, ListImage
from openstack3.views.instance import CreateInstance
from openstack3.views.users import UserRegistrationView, ApproveUserView, PendingApprovalUsersView, UserLoginView, \
    UserDetailView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,

)

urlpatterns = [
    # user
    path('user/register/', UserRegistrationView.as_view(), name='user_request'),
    path('user/approve/<uuid:user_id>/', ApproveUserView.as_view(), name='user_approval'),
    path('user/pending-approval-users/', PendingApprovalUsersView.as_view(), name='pending-approval-users'),
    path('user/login/', UserLoginView.as_view(), name='user-login'),
    path('user/token/', TokenObtainPairView.as_view(), name='user-token'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='user-token-refresh'),
    path('user/detail/', UserDetailView.as_view(), name='user-detail'),

    # admin
    path('admin/network/manage/', ManageNetworkRequest.as_view(), name='network-manage'),
    path('admin/network/pending/', PendingNetwork.as_view(), name='network-pending-users'),
    path('admin/ip/manage/', ManageIPRequest.as_view(), name='ip-manage'),
    path('admin/image/create', CreateImage.as_view(), name='create-image'),
    path('admin/flavor/create', CreateFlavor.as_view(), name='create-flavor'),

    # Projects
    path('project/create/', Create_Project.as_view(), name='project-create'),
    path('project/list/', List_Project.as_view(), name='project-list'),
    path('project/user/create/', ProjectUserCreate.as_view(), name='Project-user-create'),
    path('project/user/list/', ProjectUserList.as_view(), name='user-list'),
    path('project/user/delete/', ProjectUserDelete.as_view(), name='user-delete'),
    path('admin/user/', AdminUser.as_view(), name='admin-user'),

    # resources
    # network
    path('network/request/', CreateNetworkRequest.as_view(), name='network-create'),
    path('network/update/', UpdateNetwork.as_view(), name='network-update'),
    path('network/delete/', DeleteNetwork.as_view(), name='network-delete'),
    # keypair
    path('keypair/create/', CreateKeyPair.as_view(), name='create-keypair'),
    # images
    path('image/list/', ListImage.as_view(), name='image-list'),
    # IP
    path('ip/request/', RequestIP.as_view(), name='request-ip'),
    path('ip/list/', ListIPRequests.as_view(), name='ip-list'),
    # instance
    path('instance/create', CreateInstance.as_view(), name='create-instance'),

    # securityGroup
    path('security/Create/', CreateSecurityGroup.as_view(), name='create-security-group'),
    path('security/List/', ListSecurityGroups.as_view(), name='list-security-groups'),
    path('security/Delete/', DeleteSecurityGroup.as_view(), name='delete-security-group'),

    # util
    path('cache/', CheckCacheView.as_view, name='check-cache'),
]
