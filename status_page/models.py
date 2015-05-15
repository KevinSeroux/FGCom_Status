from django.db import models


# Create your models here.
class ActiveUser(models.Model):

    class Meta:
        db_table = 'active_users'

    id = models.FloatField(primary_key=True)
    airport = models.CharField(max_length=4)
    frequency = models.FloatField()
    callsign = models.TextField()
    version = models.TextField()
