# Generated by Django 3.1.7 on 2021-07-14 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20210714_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='shipped_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
