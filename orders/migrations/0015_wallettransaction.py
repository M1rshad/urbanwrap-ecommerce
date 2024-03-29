# Generated by Django 5.0.1 on 2024-02-15 15:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_offer'),
    ]

    operations = [
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('transaction_type', models.CharField(choices=[('debit', 'Debit'), ('credit', 'Credit')], max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('order_reference', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.order')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.wallet')),
            ],
        ),
    ]
