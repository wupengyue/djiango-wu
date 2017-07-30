from django.db import models
from django.utils import timezone


# Create your models here.
class Node(models.Model):
    hostname = models.CharField(max_length=50)
    ip_addr = models.CharField(max_length=50)
    add_time = models.DateField(default=timezone.now)
    last_update_time = models.DateField(default=timezone.now)
    update_interval = models.IntegerField(default=360)

    def __str__(self):
        return self.hostname
