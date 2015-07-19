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

    icao = models.CharField(primary_key=True, max_length=4)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)


class Frequency(models.Model):

    class Meta:
        db_table = 'frequencies'

    point = models.ForeignKey(Point)
    frequency = models.FloatField()
    description = models.TextField()
