# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveUser',
            fields=[
                ('id', models.FloatField(primary_key=True, serialize=False)),
                ('airport', models.CharField(max_length=4)),
                ('frequency', models.FloatField()),
                ('callsign', models.TextField()),
                ('version', models.TextField()),
            ],
            options={
                'db_table': 'active_users',
            },
        ),
        migrations.CreateModel(
            name='Frequency',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('frequency', models.FloatField()),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'frequencies',
            },
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.CharField(primary_key=True, max_length=4, serialize=False)),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
            ],
            options={
                'db_table': 'points',
            },
        ),
        migrations.AddField(
            model_name='frequency',
            name='point',
            field=models.ForeignKey(to='status_page.Point'),
        ),
    ]
