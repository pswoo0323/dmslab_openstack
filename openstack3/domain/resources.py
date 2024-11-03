from datetime import datetime
from django.db import models

class Resources(models.Model):

    id = models.BigAutoField(primary_key=True, verbose_name='resource_num')
    network = models.CharField(max_length=100, unique = True, verbose_name='Network Name')
    subnet = models.CharField(max_length=100, verbose_name='Subnet Name')
    CIDR = models.CharField(max_length=100, verbose_name='CIDR')
    gateway = models.CharField(max_length=100, verbose_name='Gateway_ip')
    created_at = models.DateTimeField(default=datetime.now(), verbose_name='생성된 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제된 시간')


    def __str__(self):
        return self.network

    class Meta:
        db_table = 'resources'
        verbose_name_plural ='User Resources'