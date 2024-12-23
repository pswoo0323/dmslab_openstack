# Generated by Django 5.1.2 on 2024-11-17 06:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openstack3', '0004_alter_projectuser_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectuser',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 17, 15, 26, 20, 220389), verbose_name='생성된 시간'),
        ),
        migrations.AlterField(
            model_name='resources',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 17, 15, 26, 20, 220389), verbose_name='생성된 시간'),
        ),
        migrations.AlterField(
            model_name='resources',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=50, verbose_name='Request Status'),
        ),
    ]
