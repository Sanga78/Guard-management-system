from django.utils import timezone
from datetime import date, datetime
from django.shortcuts import get_object_or_404, redirect, render
from .models import Attendance,Guard,Location,Shift,Department
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Count 
from django.contrib.auth import authenticate, login
from attendance.decorators import login_required_superuser_required
from django.contrib.auth.decorators import login_required
from django.contrib import auth 
from django.contrib.auth.hashers import check_password, make_password
# Create your views here.

def index(request):
    next = request.GET.get('next') or None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
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
    shift_guard_counts = Guard.objects.values('shift__id', 'shift__start', 'shift__end').annotate(guard_count=Count('id'))
    context = {
        'attendances_count': Attendance.objects.count(),
        'guards_count': Guard.objects.count(),
        'departments_count': Department.objects.count(),
        'locations_count': Location.objects.count(),
        'shifts_count': Shift.objects.count(),
        'department_guard_counts': department_guard_counts,
        'shift_guard_counts': shift_guard_counts,
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
        shift_id = request.POST.get("shift")
        image = request.FILES['profile_pic']

        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_url = fs.url(filename)
        else:
            image_url = ''
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
        shift = Shift.objects.get(pk=shift_id)


        # Create the Guard without a User
        guard = Guard.objects.create(
            name=name,
            email=email,
            profile_pic=image_url,
            gender=gender,
            hire_date=hire_date,
            birth_date=dob,
            department=department,
            shift=shift,
        )

        messages.success(request, "Guard added successfully! User account will be created upon activation.")
        return redirect("add_guard")

    departments = Department.objects.all()
    shifts = Shift.objects.all()
    return render(request, "admin/add_guard.html", {"departments": departments, "shifts": shifts})

@login_required_superuser_required
def edit_guard(request):
    guardId =None
    if 'guardid' in request.GET:
        guardId = request.GET.get('guardid')
    guard = get_object_or_404(Guard, id=guardId)

    if request.method == 'POST':
        name = request.POST.get("guard_name")
        gender = request.POST.get("gender")
        dob = request.POST.get("birth_date")
        hire_date = request.POST.get("hire_date")
        department_id = request.POST.get("department")
        shift_id = request.POST.get("department")
        profile_pic = request.FILES['profile_pic']
        fs = FileSystemStorage()
        filename = fs.save(profile_pic.name,profile_pic)
        profile_pic_url = fs.url(filename)

        guard.gender = gender
        guard.birth_date = dob
        guard.image=profile_pic_url,
        guard.name = name
        guard.department = get_object_or_404(Department, id=department_id)
        guard.shift = get_object_or_404(Shift, id=shift_id)
        guard.hire_date= hire_date
        guard.save()

        messages.success(request, "Updated successfully ")
        return redirect('edit_guard')
    
    departments = Department.objects.all()
    shifts = Shift.objects.all()
    
    return render(request, 'admin/edit_guard.html', {"guard":guard, "departments":departments,"shifts":shifts})

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
def shifts(request):
    if 'del' in request.GET:
        shift_id = request.GET['del']
        shift = get_object_or_404(Shift, pk=shift_id)
        shift.delete()
        messages.success(request, "The selected shift has been deleted.")
        return redirect('shifts')
    shifts = Shift.objects.all()
    context = {
        'shifts': shifts
    }
    return render(request,"admin/shifts.html",context)

@login_required_superuser_required
def add_shift(request):
    if request.method == 'POST':
        shift_start = request.POST.get("s_start")
        shift_end = request.POST.get("s_end")
        if shift_start and shift_end:
            try:
                Shift.objects.create(
                    start=shift_start,
                    end=shift_end
                )
                messages.success(request, "Shift Created Successfully")
                return redirect("shifts")
            except Exception as e:
                messages.error(request, f"Something went wrong: {e}")
        else:
            messages.error(request, "All fields are required.")
    context = {
        'title': 'Add New Shift',
    }
    return render(request, 'admin/add_shift.html', context)

@login_required_superuser_required
def edit_shift(request):
    shift_id = request.GET.get('shiftid')
    shift = get_object_or_404(Shift, id=shift_id)

    if request.method == 'POST':
        shift_start = request.POST.get("s_start")
        shift_end = request.POST.get("s_end")
        shift.start = shift_start
        shift.end = shift_end
        shift.save()
        messages.success(request, "Shift updated successfully!")
        return redirect(f'/edit_shift?shiftid={shift_id}')
    return render(request, 'admin/edit_shift.html', {'shift': shift})  

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
        dept_code = request.POST.get('deptcode')
        if Department.objects.filter(code=dept_code).exists() and dept_code != department.code:
            messages.error(request, "Department Code already exists.")
            return redirect("edit_department")
        department.name = dept_name
        department.code = dept_code
        department.save()
        messages.success(request, "Department updated successfully!")
        return redirect(f'/edit_department?deptid={dept_id}')

    return render(request, 'admin/edit_department.html', {'department': department})

@login_required_superuser_required
def list_users(request):
    if 'del' in request.GET:
        user_id = request.GET['del']
        user = get_object_or_404(User, pk=user_id)
        user.delete()
        messages.success(request, f"{user.username} Has beed deleted!")
        return redirect('list_users')
    guards = Guard.objects.all().select_related('user', 'department', 'shift')
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
    attendance = None
    start = None
    end = None
    dept_code = None

    if request.method == 'GET':
        start = request.GET.get('start')
        end = request.GET.get('end')
        dept_code = request.GET.get('dept')

        if start and end and dept_code:
            # Convert start and end dates to timestamps
            start_timestamp = int(timezone.datetime.strptime(start, "%Y-%m-%d").timestamp())
            end_timestamp = int(timezone.datetime.strptime(end, "%Y-%m-%d").timestamp())

            # Fetch attendance records based on the filters
            attendance = Attendance.objects.filter(
                in_time__range=(start_timestamp, end_timestamp),  # Use in_time for filtering
                department_id=dept_code
            ).select_related('guard', 'department', 'shift')

            # Convert timestamps to datetime objects
            for atd in attendance:
                atd.date = datetime.fromtimestamp(atd.in_time)  # Add a `date` attribute
                atd.check_in_time = datetime.fromtimestamp(atd.in_time)  # Add a `check_in_time` attribute
                if atd.out_time != 0:
                    atd.check_out_time = datetime.fromtimestamp(atd.out_time)  # Add a `check_out_time` attribute
                else:
                    atd.check_out_time = None

    context = {
        'title': title,
        'departments': departments,
        'attendance': attendance,
        'start': start,
        'end': end,
        'dept_code': dept_code,
    }
    return render(request, 'admin/attendance_report.html', context)


@login_required_superuser_required
def generate_report(request, start, end, dept_code):
    start_timestamp = int(timezone.datetime.strptime(start, "%Y-%m-%d").timestamp())
    end_timestamp = int(timezone.datetime.strptime(end, "%Y-%m-%d").timestamp())

    attendance = Attendance.objects.filter(
        in_time__range=(start_timestamp, end_timestamp), 
        department_id=dept_code
    ).select_related('guard', 'department', 'shift')

    for atd in attendance:
        atd.date = datetime.fromtimestamp(atd.in_time) 
        atd.check_in_time = datetime.fromtimestamp(atd.in_time)
        if atd.out_time != 0:
            atd.check_out_time = datetime.fromtimestamp(atd.out_time)
        else:
            atd.check_out_time = None

    context = {
        'dept_code': dept_code,
        'start': start,
        'end': end,
        'attendance': attendance,
    }
    return render(request, 'admin/print_report.html', context)

@login_required
def guard_attendance(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'guard'):
        return redirect('login')

    guard = request.user.guard

    today = datetime.today()
    weekends = today.weekday() >= 5  # 5 = Saturday, 6 = Sunday

    in_attendance = Attendance.objects.filter(guard=guard, out_time__isnull=True).exists()

    locations = Location.objects.all()

    context = {
        'guard': guard,
        'weekends': weekends,
        'g_in': in_attendance,
        'locations': locations,
        'disable': False,  # Set this based on your logic (e.g., disable check-out after a certain time)
    }

    return render(request, 'employee/employee_attendance.html', context)

@login_required
def check_in(request):
    if request.method == 'POST':
        guard = get_object_or_404(Guard, user=request.user)
        location_id = request.POST.get('location')
        notes = request.POST.get('notes')
        image = request.FILES.get('image')

        # Save the image to the media directory
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_url = fs.url(filename)
        else:
            image_url = ''

        # Create the attendance record
        Attendance.objects.create(
            guard=guard,
            department=guard.department,
            shift=guard.shift,
            location_id=location_id,
            in_time=int(timezone.now().timestamp()),  # Save timestamp
            notes=notes,
            image=image_url,
            in_status='Present',  # Default status
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
