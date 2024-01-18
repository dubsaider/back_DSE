# Generated by Django 4.2.4 on 2023-12-07 06:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='process',
            name='process_events',
        ),
        migrations.RemoveField(
            model_name='processevent',
            name='actions',
        ),
        migrations.RemoveField(
            model_name='processevent',
            name='event_type',
        ),
        migrations.AddField(
            model_name='process',
            name='all_frames_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='all_frames', to='processing.processevent'),
        ),
        migrations.AddField(
            model_name='process',
            name='any_object_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='any_object', to='processing.processevent'),
        ),
        migrations.AddField(
            model_name='process',
            name='any_object_few_minutes_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='any_object_few_minutes', to='processing.processevent'),
        ),
        migrations.AddField(
            model_name='processevent',
            name='fps',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='processevent',
            name='host_rtp',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='processevent',
            name='line_count',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='processevent',
            name='port_rtp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='processevent',
            name='size_buff',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='processevent',
            name='zone_check',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='ProcessAction',
        ),
    ]