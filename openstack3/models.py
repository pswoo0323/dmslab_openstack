from datetime import datetime
from tabnanny import verbose

from django.db import models

# Create your models here.
class User(models.Model):

    id = models.BigAutoField(primary_key=True, verbose_name='user_num')
    username = models.CharField(max_length=150, unique = True, verbose_name='Openstack username')
    created_at = models.DateTimeField(default=datetime.now(), verbose_name='생성된 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제된 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='업데이트 날짜')
    password = models.CharField(null=False, max_length=150, verbose_name='오픈스택 패스워드')
    email = models.EmailField(null=False, max_length=300, verbose_name='이메일')


    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'DMSLAB Openstack'