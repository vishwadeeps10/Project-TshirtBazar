# Generated by Django 3.1.2 on 2020-10-23 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='slug',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='color',
            name='slug',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='idealfor',
            name='slug',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='necktype',
            name='slug',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='occasion',
            name='slug',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='sleeve',
            name='slug',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
