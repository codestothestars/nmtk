# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-16 18:26
from __future__ import unicode_literals

from django.db import migrations, models


def update_file_name(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    tsf = apps.get_model("NMTK_server", "ToolSampleFile")
    for entry in tsf.objects.all():
        entry.save()


class Migration(migrations.Migration):

    dependencies = [
        ('NMTK_server', '0007_toolsamplefile_file_name'),
    ]

    operations = [
        migrations.RunPython(update_file_name),
    ]