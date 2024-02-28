# Generated by Django 5.0.1 on 2024-02-28 14:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_alter_variation_variation_value'),
        ('orders', '0033_alter_offer_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='products',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product', to='home.product'),
        ),
    ]
