from django.db import models
from drivers.models import Driver

class Truck(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trucks')
    plate_number = models.CharField(max_length=10)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.model} - {self.plate_number}"
