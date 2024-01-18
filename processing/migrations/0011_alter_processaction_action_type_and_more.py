# Generated by Django 4.2.4 on 2023-12-14 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0010_alter_process_result_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processaction',
            name='action_type',
            field=models.CharField(choices=[('record', 'Record'), ('logging', 'Logging'), ('line_count', 'Line Count'), ('zone_check', 'Zone Check'), ('rtp_stream', 'RTP Stream'), ('box_drawing', 'Box Drawing'), ('buffer_stream', 'Stream Buffer'), ('rtsp_server_stream', 'RTSP Stream Server'), ('FPS_check', 'FPS Check')]),
        ),
        migrations.AlterField(
            model_name='processevent',
            name='event_type',
            field=models.CharField(choices=[('all_frames', 'All frames'), ('check_any_object', 'Check any object'), ('check_any_object_few_minutes', 'Check any object few minutes')]),
        ),
    ]