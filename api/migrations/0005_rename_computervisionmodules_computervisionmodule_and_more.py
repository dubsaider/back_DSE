# Generated by Django 4.2.4 on 2023-11-20 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_detectedobjecttype_description'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ComputerVisionModules',
            new_name='ComputerVisionModule',
        ),
        migrations.RenameModel(
            old_name='Models',
            new_name='Model',
        ),
    ]
