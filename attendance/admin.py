from django.contrib import admin
from .models import Department, Guard, Location, AdminProfile,Attendance


admin.site.register(Department)
admin.site.register(Guard)
admin.site.register(Attendance)
admin.site.register(Location)
admin.site.register(AdminProfile)