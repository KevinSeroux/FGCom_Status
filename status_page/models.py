from django.db import models


class ActiveUser(models.Model):

    class Meta:
        db_table = 'active_users'

    id = models.FloatField(primary_key=True)
    point = models.CharField(max_length=4)
    frequency = models.FloatField()
    callsign = models.TextField()
    version = models.TextField()


class Point(models.Model):  # Airports, NDBs

    class Meta:
        db_table = 'points'
        unique_together = ('name', 'latitude', 'longitude')

    name = models.CharField(max_length=4)
    latitude = models.FloatField(null=True)  # WGS84
    longitude = models.FloatField(null=True)  # WGS84


class Frequency(models.Model):

    class Meta:
        db_table = 'frequencies'
        unique_together = ('point', 'frequency')

    point = models.ForeignKey(Point)  # unique for APT, LOC, GS
    frequency = models.FloatField()  # unit: KHz
    description = models.TextField()

    nav = models.BooleanField(default=False)  # NDB, VOR, LOC, GS, DME
    auto_info = models.BooleanField(default=False)
