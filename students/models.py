from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=100, default='', blank=True)
    mssv = models.CharField(max_length=10, default='', blank=True)

