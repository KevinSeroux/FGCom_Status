from django.db import models


class Point(models.Model):  # Airports, NDBs

    class Meta:
        db_table = 'points'

    icao = models.CharField(primary_key=True, max_length=4)  # ICAO
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)


class ActiveUser(models.Model):

    class Meta:
        db_table = 'active_users'

    id = models.FloatField(primary_key=True)
    point = models.ForeignKey(Point)
    frequency = models.FloatField()
    callsign = models.TextField()
    version = models.TextField()


class Frequency(models.Model):

    class Meta:
        db_table = 'frequencies'

    point = models.ForeignKey(Point)
    frequency = models.FloatField()
    description = models.TextField()
