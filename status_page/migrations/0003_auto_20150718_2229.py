# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_page', '0002_auto_20150718_2226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='point',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='point',
            name='longitude',
            field=models.FloatField(null=True),
        ),
    ]
