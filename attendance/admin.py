from django.contrib import admin
from .models import Department, Guard, Location, Shift, AdminProfile,Attendance


admin.site.register(Department)
admin.site.register(Guard)
admin.site.register(Attendance)
admin.site.register(Location)
admin.site.register(Shift)
admin.site.register(AdminProfile)