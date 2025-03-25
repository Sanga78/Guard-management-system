from django.utils import timezone
from datetime import date, datetime
from django.shortcuts import get_object_or_404, redirect, render
from .models import Attendance,Guard,Location,Department
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Count 
from django.contrib.auth import authenticate, login
from attendance.decorators import login_required_superuser_required
from django.contrib.auth.decorators import login_required
from django.contrib import auth 
from django.contrib.auth.hashers import check_password, make_password
from django.utils.timezone import now
# Create your views here.

def index(request):
    next = request.GET.get('next') or None
    if request.method == "POST":
        identifier = request.POST.get("username")
        password = request.POST.get("password")
        user = None

        try:
            user_obj = User.objects.get(email=identifier)
            user = authenticate(request,username=user_obj.username,password=password)
        except User.DoesNotExist:
            user = authenticate(request, username=identifier, password=password)
        
        if user is not None:
            login(request, user)

            if user.is_superuser:
                if next:
                    return redirect(next)
                return redirect('admin_dashboard') 
            else:
                if next:
                        return redirect(next)
                return redirect('guard_profile') 
        else:
            messages.error(request, "Invalid login credentials!")
    return render(request, 'index.html', {"message": None})

@login_required_superuser_required
def admin_dashboard(request):
    active_guard_counts = Guard.objects.filter(user__isnull=False).count()
    department_guard_counts = Guard.objects.values('department__code', 'department__name').annotate(guard_count=Count('id'))
    location_guard_counts = Guard.objects.values('location__id','location__name').annotate(guard_count=Count('id'))
    context = {
        'attendances_count': Attendance.objects.count(),
        'guards_count': Guard.objects.count(),
        'departments_count': Department.objects.count(),
        'locations_count': Location.objects.count(),
        'department_guard_counts': department_guard_counts,
        'location_guard_counts': location_guard_counts,
        'active_user_counts': active_guard_counts,
    }
    return render(request, "admin/admin_dashboard.html", context)

@login_required_superuser_required
def guards(request):
    if 'del' in request.GET:
        guard_id = request.GET['del']
        guard = get_object_or_404(Guard, pk=guard_id)
        guard.delete()
        messages.success(request, f"{guard.user.name} Has beed deleted!")
        return redirect('guards')
    guards = Guard.objects.all()
    context={
        "guards": guards,
    }
    return render(request,"admin/guards.html",context)

@login_required_superuser_required
def add_guard(request):
    if request.method == "POST":
        name = request.POST.get("guard_name")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        hire_date = request.POST.get("hire_date")
        department_id = request.POST.get("d_id")
        location_id = request.POST.get("location")
        image = request.FILES.get('profile_pic') 

        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

            if age < 18:
                messages.error(request, 'Guard must be at least 18 years old.')
                return redirect('add_guard')
        except ValueError:
            messages.error(request, 'Invalid date of birth.')
            return redirect('add_guard')
        if Guard.objects.filter(name=name).exists():
            messages.error(request, "Guard name already exists.")
            return redirect("add_guard")

        if Guard.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("add_guard")

        department = Department.objects.get(pk=department_id)
        location = Location.objects.get(pk=location_id)

        guard = Guard.objects.create(
            name=name,
            email=email,
            profile_pic=image,  # If image is None, the model's default will be used
            gender=gender,
            hire_date=hire_date,
            birth_date=dob,
            department=department,
            location=location,
        )

        messages.success(request, "Guard added successfully! User account will be created upon activation.")
        return redirect("add_guard")

    departments = Department.objects.all()
    locations = Location.objects.all()
    return render(request, "admin/add_guard.html", {"departments": departments, "locations": locations})

@login_required_superuser_required
def edit_guard(request):
    guardId = None
    if 'guardid' in request.GET:
        guardId = request.GET.get('guardid')
    guard = get_object_or_404(Guard, id=guardId)

    if request.method == 'POST':
        name = request.POST.get("guard_name")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        hire_date = request.POST.get("hire_date")
        department_id = request.POST.get("department")
        location_id = request.POST.get("location")
        profile_pic = request.FILES.get('profile_pic')
        if profile_pic:
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
        else:
            profile_pic_url = guard.profile_pic

        guard.name = name
        guard.gender = gender
        guard.birth_date = dob
        guard.hire_date = hire_date 
        guard.department = get_object_or_404(Department, id=department_id)
        guard.location = get_object_or_404(Location, id=location_id)
        guard.profile_pic = profile_pic_url
        guard.save()
        messages.success(request, "Updated successfully")
        return redirect('guards')
    
    departments = Department.objects.all()
    locations = Location.objects.all()
    
    return render(request, 'admin/edit_guard.html', {"guard": guard, "departments": departments, "locations": locations})

@login_required_superuser_required
def locations(request):
    if 'del' in request.GET:
        loc_id = request.GET['del']
        location = get_object_or_404(Location, pk=loc_id)
        location.delete()
        messages.success(request, f"{location.name} Has beed deleted!")
        return redirect('locations')
    locations = Location.objects.all()
    context = {
        'locations': locations
    }
    return render(request,"admin/locations.html",context)

@login_required_superuser_required
def add_location(request):
    if request.method == 'POST':
        location_name = request.POST.get("l_name")
        if Location.objects.filter(name=location_name).exists():
            messages.error(request, "Location name already exists.")
            return redirect("add_location")
        if location_name:
            try:
                Location.objects.create(
                    name=location_name,
                )
                messages.success(request, "Location Added Successfully")
                return redirect("locations")
            except Exception as e:
                messages.error(request, f"Something went wrong: {e}")
        else:
            messages.error(request, "All fields are required.")
    context = {
        'title': 'Add New Location',
    }
    return render(request, 'admin/add_location.html', context)

@login_required_superuser_required
def edit_location(request):
    location_id = request.GET.get('locid')
    location = get_object_or_404(Location, id=location_id)

    if request.method == "POST":
        location_name = request.POST.get('l_name')
        location.name = location_name
        location.save()
        messages.success(request, "Location updated successfully!")
        return redirect(f'/edit_location?locid={location_id}')
    context = {
        'title': 'Edit Location',
        'location': location
    }
    return render(request, 'admin/edit_location.html', context)

@login_required_superuser_required
def admin_change_password(request):
    user = request.user
    if request.method == "POST":
        current_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("c_password")

        if not check_password(current_password, user.password):
            messages.error(request, "Your current password is incorrect.")
            return redirect("admin_change_password")

        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect("admin_change_password")

        user.password = make_password(new_password)
        user.save()
        messages.success(request, "Your password has been updated successfully.")
        return redirect("login")

    return render(request, "admin/change_password.html")

@login_required_superuser_required
def department(request):
    if 'del' in request.GET:
        department_id = request.GET['del']
        department = get_object_or_404(Department, pk=department_id)
        department.delete()
        messages.success(request, "The selected department has been deleted.")
        return redirect('departments')
    departments = Department.objects.all()
    context = {
        'departments': departments
    }
    return render(request,"admin/departments.html",context)

@login_required_superuser_required
def attendance(request):
    attendance = Attendance.objects.all()
    context = {
        'attendance': attendance
    }
    return render(request,"admin/attendance_report.html",context)

@login_required_superuser_required
def add_department(request):
    if request.method == 'POST':
        deptname = request.POST.get('deptname')
        deptcode = request.POST.get('deptcode')
        if Department.objects.filter(code=deptcode).exists():
            messages.error(request, "Department Code already exists.")
            return redirect("add_department")

        if deptname and deptcode:
            try:
                Department.objects.create(
                    name=deptname,
                    code=deptcode
                )
                messages.success(request, "Department Created Successfully")
                return redirect("departments")
            except Exception as e:
                messages.error(request, f"Something went wrong: {e}")
        else:
            messages.error(request, "All fields are required.")
    return render(request, 'admin/add_department.html')

@login_required_superuser_required
def edit_department(request):
    dept_id = request.GET.get('deptid')
    department = get_object_or_404(Department, id=dept_id)

    if request.method == "POST":
        dept_name = request.POST.get('deptname')
        department.name = dept_name
        department.save()
        messages.success(request, "Department updated successfully!")
        return redirect('departments')

    return render(request, 'admin/edit_department.html', {'department': department})

@login_required_superuser_required
def list_users(request):
    if 'del' in request.GET:
        user_id = request.GET['del']
        user = get_object_or_404(User, pk=user_id)
        user.delete()
        messages.success(request, f"{user.username} Has beed deleted!")
        return redirect('list_users')
    guards = Guard.objects.all().select_related('user', 'department', 'location')
    context = {
        'title': 'Users',
        'guards':guards
    }
    return render(request, 'admin/users.html', context)

@login_required_superuser_required
def add_user(request):
    guard_id =None
    if 'guard_id' in request.GET:
        guard_id = request.GET.get('guard_id')
    
    guard = get_object_or_404(Guard, id=guard_id)
    
    if request.method == 'POST':
        username = request.POST.get('u_username')
        password = request.POST.get('password')
        
        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        else:
            email = guard.email
            user = User.objects.create_user(username=username,email=email, password=password)
            guard.user = user 
            guard.save()
            messages.success(request, 'User account created and activated successfully!')
            return redirect('list_users')
    
    context = {
        'guard_id': guard_id,
        'username': f"{guard.name}_{guard.id}",
    }
    return render(request, 'admin/add_users.html', context)

@login_required_superuser_required
def edit_user(request):
    userId =None
    if 'us_id' in request.GET:
        userId = request.GET.get('us_id')
    user = get_object_or_404(User, id=userId)
    
    if request.method == 'POST':
        username = request.POST.get('u_username')
        password = request.POST.get('password')        
        
        user.username = username
        user.set_password(password)
        messages.success(request, 'User Details Updated successfully!')
        return redirect('list_users')
    
    return render(request, 'admin/edit_users.html',{"user":user})

@login_required_superuser_required
def attendance_report(request):
    title = "Attendance Report"
    departments = Department.objects.all()
    locations = Location.objects.all()
    attendance = None
    dept_code = None

    if request.method == 'GET':
        location = request.GET.get('location')
        dept_code = request.GET.get('dept')

        try:
            location = int(location) if location else None
            dept_code = int(dept_code) if dept_code else None
        except ValueError:
            location = None
            dept_code = None

        if location is not None and dept_code is not None:
            attendance = Attendance.objects.filter(
                location_id=location,
                department_id=dept_code 
            ).select_related('guard', 'department', 'location')

            for atd in attendance:
                atd.date = datetime.fromtimestamp(atd.in_time)
                atd.check_in_time = datetime.fromtimestamp(atd.in_time)
                atd.check_out_time = (
                    datetime.fromtimestamp(atd.out_time) if atd.out_time else None
                )

    if request.method == "POST":
        attendance_id = request.POST.get("attendance_id") 
        status = request.POST.get("status")
        description = request.POST.get("description")

        if not attendance_id:
            messages.error(request, "Invalid attendance ID.")
            return redirect("attendance_report")

        attendance_record = get_object_or_404(Attendance, id=attendance_id)

        if status and description:
            attendance_record.status = int(status)
            attendance_record.admin_remark = description
            attendance_record.admin_remark_date = now()
            attendance_record.save()
            messages.success(request, "Attendance status updated successfully.")
        else:
            messages.error(request, "Please provide all required fields.")

        return redirect("attendance_report")

    context = {
        "title": title,
        "departments": departments,
        "attendance": attendance,
        "locations": locations,
        "dept_code": dept_code,
    }
    return render(request, "admin/attendance_report.html", context)

@login_required_superuser_required
def generate_report(request, location, dept_code):

    attendance = Attendance.objects.filter(
        location=location, 
        department_id=dept_code
    ).select_related('guard', 'department', 'location')

    for atd in attendance:
        atd.date = datetime.fromtimestamp(atd.in_time) 
        atd.check_in_time = datetime.fromtimestamp(atd.in_time)
        if atd.out_time != 0:
            atd.check_out_time = datetime.fromtimestamp(atd.out_time)
        else:
            atd.check_out_time = None

    context = {
        'dept_code': dept_code,
        'location': location,
        'attendance': attendance,
    }
    return render(request, 'admin/print_report.html', context)

@login_required
def guard_attendance(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'guard'):
        return redirect('login')

    guard = request.user.guard

    today = datetime.today()
    weekends = today.weekday() >= 5

    in_attendance = Attendance.objects.filter(guard=guard, out_time__isnull=True).exists()

    locations = Location.objects.all()

    context = {
        'guard': guard,
        'weekends': weekends,
        'g_in': in_attendance,
        'locations': locations,
        'disable': False,
    }

    return render(request, 'employee/employee_attendance.html', context)

@login_required
def check_in(request):
    if request.method == 'POST':
        guard = get_object_or_404(Guard, user=request.user)
        notes = request.POST.get('notes')
        image = request.FILES.get('image')
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_url = fs.url(filename)
        else:
            image_url = ''

        Attendance.objects.create(
            guard=guard,
            department=guard.department,
            location_id=guard.location.id,
            in_time=int(timezone.now().timestamp()),
            notes=notes,
            image=image_url,
            in_status='Present',
            status=0,
        )

        messages.success(request, 'You have successfully checked in!')
        return redirect('guard_attendance')

    return redirect('guard_attendance')
@login_required
def check_out(request):
    if request.method == 'POST':
        guard = get_object_or_404(Guard, user=request.user)
        attendance = Attendance.objects.filter(guard=guard, out_time__isnull=True).first()

        if attendance:
            attendance.out_time = int(timezone.now().timestamp())
            attendance.out_status = 'Checked Out'
            attendance.save()
            messages.success(request, 'You have successfully checked out!')
        else:
            messages.error(request, 'No active check-in record found!')

    return redirect('guard_attendance')


@login_required
def guard_profile(request):
    user = request.user
    guard = get_object_or_404(Guard, user=user)
    return render(request, 'employee/employee_profile.html',{"guard":guard})

@login_required
def change_password(request):
    user = request.user
    guard = get_object_or_404(Guard, user=user)
    if request.method == "POST":
        current_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("c_password")

        if not check_password(current_password, user.password):
            messages.error(request, "Your current password is incorrect.")
            return redirect("change_password")

        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect("change_password")

        user.password = make_password(new_password)
        user.save()
        messages.success(request, "Your password has been updated successfully.")
        return redirect("login")

    return render(request, "employee/change_password.html",{"guard":guard})

def logout(request):
    auth.logout(request)
    return redirect('login')
