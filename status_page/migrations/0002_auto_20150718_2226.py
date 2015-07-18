# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_page', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='point',
            old_name='id',
            new_name='icao',
        ),
        migrations.RemoveField(
            model_name='activeuser',
            name='airport',
        ),
        migrations.AddField(
            model_name='activeuser',
            name='point',
            field=models.ForeignKey(to='status_page.Point', default='KSFO'),
            preserve_default=False,
        ),
    ]
