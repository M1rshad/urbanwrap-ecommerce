# Generated by Django 5.0.1 on 2024-02-20 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_alter_variation_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discounted_price',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
