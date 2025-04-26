from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    license_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_full_name() if self.get_full_name() else self.username
        
    def is_driver(self):
        return bool(self.license_number)
