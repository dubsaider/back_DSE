# Generated by Django 4.2.4 on 2023-08-21 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('camera_name', models.CharField(max_length=255)),
                ('camera_ip', models.CharField(max_length=15)),
                ('camera_description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ClusterUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_name', models.CharField(max_length=255)),
                ('unit_ip', models.CharField(max_length=15)),
                ('unit_config', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='DetectedObjectTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Locations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Processing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processing_config', models.JSONField()),
                ('result_link', models.URLField(blank=True, null=True)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.camera')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.clusterunit')),
            ],
        ),
        migrations.CreateModel(
            name='ObjectsDetectionLogs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datestamp', models.DateTimeField()),
                ('count', models.IntegerField(default=0)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.locations')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.detectedobjecttypes')),
            ],
        ),
    ]