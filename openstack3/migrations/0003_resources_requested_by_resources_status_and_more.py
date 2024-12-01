# Generated by Django 5.1.2 on 2024-11-17 06:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openstack3', '0002_alter_projectuser_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='resources',
            name='requested_by',
            field=models.CharField(max_length=100, null=True, verbose_name='Requested_by'),
        ),
        migrations.AddField(
            model_name='resources',
            name='status',
            field=models.CharField(choices=[('대기', '대기'), ('승인', '승인'), ('거절', '거절')], default='대기', max_length=50, verbose_name='Request Status'),
        ),
        migrations.AlterField(
            model_name='projectuser',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 17, 15, 5, 37, 867847), verbose_name='생성된 시간'),
        ),
        migrations.AlterField(
            model_name='resources',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 17, 15, 5, 37, 867847), verbose_name='생성된 시간'),
        ),
    ]