# Generated by Django 5.0.1 on 2024-02-18 10:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_alter_variation_product'),
        ('orders', '0027_alter_order_order_total_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='products',
        ),
        migrations.AddField(
            model_name='offer',
            name='products',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.product'),
        ),
    ]
