# Generated by Django 5.0.1 on 2024-02-18 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0026_delete_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_total',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='product_price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]