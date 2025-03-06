from django.shortcuts import redirect, render
from .models import Attendance,Guard,Location,Shift,Department
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
# Create your views here.

def index(request):
    return render(request,"index.html")


def admin_dashboard(request):
    context = {
        'attendances_count': Attendance.objects.count(),
        'guards_count': Guard.objects.count(),
        'departments_count': Department.objects.count(),
        'locations_count': Location.objects.count(),
        'shifts_count': Shift.objects.count(),
    }
    return render(request,"admin/admin_dashboard.html",context)

def guards(request):
    guards = Guard.objects.all()
    context={
        "guards": guards,
    }
    return render(request,"admin/guards.html",context)

def add_guard(request):
    if request.method == "POST":
        name = request.POST.get("guard_name")
        email = request.POST.get("email")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        hire_date = request.POST.get("hire_date")
        department_id = request.POST.get("department")
        shift_id = request.POST.get("shift")

        if Guard.objects.filter(name=name).exists():
            messages.error(request, "Guard name already exists.")
            return redirect("add_guard")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("add-employee")

        user = User.objects.create_user(username=email, email=email, password=password)
        department = Department.objects.get(pk=department_id)
        shift = Shift.objects.get(pk=shift_id)
        profile_pic = request.FILES['profile_pic']
        fs = FileSystemStorage()
        filename = fs.save(profile_pic.name,profile_pic)
        profile_pic_url = fs.url(filename)

        guard = Guard.objects.create(
            user=user,
            name=name,
            email=email,
            image=profile_pic_url,
            gender=gender,
            hire_date=hire_date,
            birth_date=dob,
            department=department,
            shift=shift,
        )

        messages.success(request, "Employee added successfully!")
        return redirect("add-employee")

    departments = Department.objects.all()
    return render(request, "admin/add-employee.html", {"departments": departments})

def locations(request):
    locations = Location.objects.all()
    context = {
        'locations': locations
    }
    return render(request,"admin/locations.html",context)

def shifts(request):
    shifts = Shift.objects.all()
    context = {
        'shifts': shifts
    }
    return render(request,"admin/shifts.html",context)

def departments(request):
    departments = Department.objects.all()
    context = {
        'departments': departments
    }
    return render(request,"admin/departments.html",context)

def attendance(request):
    attendance = Attendance.objects.all()
    context = {
        'attendance': attendance
    }
    return render(request,"admin/attendance_report.html",context)

def add_department(request):
    if request.method == 'POST':
        deptname = request.POST.get('departmentname')
        deptcode = request.POST.get('deptcode')

        if deptname and deptcode:
            try:
                Department.objects.create(
                    name=deptname,
                    code=deptcode
                )
                messages.success(request, "Department Created Successfully")
            except Exception as e:
                messages.error(request, f"Something went wrong: {e}")
        else:
            messages.error(request, "All fields are required.")
    return render(request, 'admin/add_department.html')
