from datetime import datetime

from django.db import models

class Resources(models.Model):

    id = models.BigAutoField(primary_key=True, verbose_name='resource_num')
    network = models.CharField(max_length=100, unique = True, verbose_name='Network Name')
    subnet = models.CharField(max_length=100, null=False, verbose_name='Subnet Name')
    CIDR = models.CharField(max_length=100, null= False, verbose_name='CIDR')
    keypair = models.CharField(max_length=100, null=True, verbose_name='key-pair')
    gateway = models.CharField(max_length=100, null= True, verbose_name='Gateway_ip')
    created_at = models.DateTimeField(default=datetime.now(), verbose_name='생성된 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제된 시간')
    requested_by = models.CharField(max_length=100, verbose_name= 'Requested_by', null=True)# 요청자
    status = models.CharField(
        max_length=50,
        choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')], default='pending',verbose_name='Request Status'
    )

    def __str__(self):
        return f"{self.network} ({self.status})"

    class Meta:
        db_table = 'resources'
        verbose_name_plural ='User Resources'