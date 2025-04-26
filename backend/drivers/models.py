from django.db import models
from users.models import User

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name()
