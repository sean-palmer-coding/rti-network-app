from django.db import models
from django.utils import timezone

# Create your models here.

#location model for location of network diagnostic nodes
class Locations(models.Model):
    location = models.CharField(max_length=200)
    lat = models.CharField(max_length=100)
    lon = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(null=True)
    color = models.CharField(max_length=200, default="rgb(255,255,255)")

    def __str__(self):
        return self.location

class TestResult(models.Model):
    alias = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()
    download = models.DecimalField(max_digits=7, decimal_places=2)
    upload = models.DecimalField(max_digits=7, decimal_places=2)
    server_ip = models.GenericIPAddressField()
    ping = models.DecimalField(max_digits=4, decimal_places=2)
    test_datetime = models.DateTimeField(timezone.now)

    def __str__(self):
        return self.alias
