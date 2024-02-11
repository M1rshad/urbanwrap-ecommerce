# Generated by Django 5.0.1 on 2024-02-11 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0005_remove_shippingaddress_address_lines_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='address_line_1',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='address_line_2',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='email',
            field=models.EmailField(max_length=50),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='last_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='phone',
            field=models.CharField(max_length=15),
        ),
    ]
