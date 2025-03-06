from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Department(models.Model):
    id = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Shift(models.Model):
    id = models.AutoField(primary_key=True)
    start = models.TimeField()
    end = models.TimeField()

class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Guard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=128)
    gender = models.CharField(max_length=1)
    image = models.CharField(max_length=128, default='default.png')
    birth_date = models.DateField()
    hire_date = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=6)
    guard = models.ForeignKey(Guard, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    in_time = models.IntegerField()
    notes = models.CharField(max_length=120, blank=True)
    image = models.CharField(max_length=50, blank=True)
    lack_of = models.CharField(max_length=11, blank=True)
    in_status = models.CharField(max_length=15)
    out_time = models.IntegerField()
    out_status = models.CharField(max_length=15)

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)
    email = models.EmailField()
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fullname
