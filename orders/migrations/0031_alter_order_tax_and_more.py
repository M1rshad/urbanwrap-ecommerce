# Generated by Django 5.0.1 on 2024-02-20 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0030_alter_offer_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tax',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='updated_balance',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
