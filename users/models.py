from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from datetime import date
class User(AbstractUser):
    phone_number=models.BigIntegerField(blank=True,null=True)
    profile_pic=models.ImageField(upload_to='profiles',default='default.png')
    date_of_birth=models.DateField(blank=True,null=True)