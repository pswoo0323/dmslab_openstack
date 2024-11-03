from django.urls import path
from openstack3.views.users import UserList, UserDelete, AdminUser, UserRegister
from openstack3.views.projects import Create_Project, List_Project
from openstack3.views.resources import CreateNetwork, CreateKeyPair, CreateImage, CreateInstance, CreateFlavor

urlpatterns = [
    #Projects
    path('project/create/', Create_Project.as_view(), name='project-create'),
    path('project/list/', List_Project.as_view(), name='project-list'),


    #Users
    path('user/register/',UserRegister.as_view(), name='user-register'),
    path('user/list/', UserList.as_view(), name='user-list'),
    path('user/delete/', UserDelete.as_view(), name='user-delete'),
    path('admin/user/', AdminUser.as_view(), name='admin-user'),

    #resources
    path('resources/network/create/', CreateNetwork.as_view(), name='network-create'),
    path('resources/keypair/', CreateKeyPair.as_view(), name='create-keypair'),
    path('resources/image/', CreateImage.as_view(), name = 'create-image'),
    path('resources/instance/', CreateInstance.as_view(), name= 'create-instance'),
    path('resources/flavor/', CreateFlavor.as_view(), name = 'create-flavor'),
]
