# Generated by Django 5.0.1 on 2024-02-17 20:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0008_coupon_user_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_auth.coupon'),
        ),
    ]
