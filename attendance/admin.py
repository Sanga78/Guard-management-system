from django.contrib import admin
from .models import Department, Guard, Location, Shift, AdminProfile,Attendance


admin.register(Department)
admin.register(Guard)
admin.register(Attendance)
admin.register(Location)
admin.register(Shift)
admin.register(AdminProfile)