# Generated by Django 3.1.7 on 2021-07-14 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20210714_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='created_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='orders',
            name='return_order_date',
            field=models.DateTimeField(),
        ),
    ]