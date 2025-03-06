from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='login'),
        path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
        path('guards', views.guards, name='guards'),
        path('locations', views.locations, name='locations'),
        path('shifts', views.shifts, name='shifts'),
        path('departments', views.departments, name='departments'),
        path('attendance', views.attendance, name='attendance'),
        path('add_department', views.add_department, name='add_department'),
]