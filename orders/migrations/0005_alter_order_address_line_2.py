# Generated by Django 5.0.1 on 2024-01-23 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_address_line_2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address_line_2',
            field=models.CharField(max_length=50),
        ),
    ]