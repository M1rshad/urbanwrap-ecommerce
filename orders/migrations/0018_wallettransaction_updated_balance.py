# Generated by Django 5.0.1 on 2024-02-15 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_alter_wallettransaction_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallettransaction',
            name='updated_balance',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
