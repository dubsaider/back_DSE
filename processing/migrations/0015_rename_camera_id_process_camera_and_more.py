# Generated by Django 4.2.4 on 2024-02-12 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0014_actiontype_description_eventtype_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='process',
            old_name='camera_id',
            new_name='camera',
        ),
        migrations.RenameField(
            model_name='process',
            old_name='cv_module_id',
            new_name='cv_module',
        ),
    ]