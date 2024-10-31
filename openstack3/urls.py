from django.urls import path
from openstack3.views.users import UserList, UserCreate, UserDelete, AssignAdminRole
from openstack3.views.projects import Create_Project, List_Project
from openstack3.views.resources import CreateNetwork


urlpatterns = [
    #Projects
    path('project/create/', Create_Project.as_view(), name='project-create'),
    path('project/list/', List_Project.as_view(), name='project-list'),


    #Users

    path('user/create/',UserCreate.as_view(), name='user-create'),
    path('user/list/', UserList.as_view(), name='user-list'),
    path('user/delete/', UserDelete.as_view(), name='user-delete'),
    path('user/assignadmin/', AssignAdminRole.as_view(), name='user-assignadmin'),

    #resources
    path('resources/network/create/', CreateNetwork.as_view(), name='network-create'),
]
