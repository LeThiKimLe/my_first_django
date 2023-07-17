from django.db import models

# Create your models here.
class Subject(models.Model):
    s_name = models.CharField(max_length=100, default=' ', blank=True)
    s_code = models.IntegerField(default=0, blank=False)

