from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='login'),
        path('logout/', views.logout, name='logout'),
        path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
        path('admin_change_password/', views.admin_change_password, name='admin_change_password'),
        path('guards', views.guards, name='guards'),
        path('add_guard', views.add_guard, name='add_guard'),
        path('edit_guard', views.edit_guard, name='edit_guard'),
        path('edit_user', views.edit_user, name='edit_user'),
        path('list_users', views.list_users, name='list_users'),
        path('add_user', views.add_user, name='add_user'),
        path('locations', views.locations, name='locations'),
        path('add_location', views.add_location, name='add_location'),
        path('edit_location', views.edit_location, name='edit_location'),
        path('departments', views.department, name='departments'),
        path('add_department', views.add_department, name='add_department'),
        path('edit_department', views.edit_department, name='edit_department'),
        path('attendance-report', views.attendance_report, name='attendance_report'),
        path('generate-report/<str:location>/<int:dept_code>/', views.generate_report, name='generate_report'),


        #GUARD URLS
        path('guard_attendance', views.guard_attendance, name='guard_attendance'),
        path('guard_profile', views.guard_profile, name='guard_profile'),
        path('change_password/', views.change_password, name='change_password'),
        path('check-in/', views.check_in, name='check_in'),
        path('check-out/', views.check_out, name='check_out'),

]