import csv

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import LoginForm, StudentForm, UserForm
from .models import Staff, Student, Parent, User


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


def home(request):
    return render(request, 'home.html')


@login_required
def dashboard(request):
    user = request.user
    staff_or_student_roles = ["Staff", "Student", "Parent"]

    if user.role == 'Staff':
        user.get_profile = get_object_or_404(Staff, user=user)
        bus = user.get_profile.bus
        students = Student.objects.filter(bus=bus)
        staff_members = Staff.objects.filter(bus=bus)
        driver = bus.driver if bus else None
    elif user.role in ['Student', 'Parent']:
        if user.role == 'Student':
            user.get_profile = get_object_or_404(Student, user=user)
            bus = user.get_profile.bus
        elif user.role == 'Parent':
            user.get_profile = get_object_or_404(Parent, user=user)
            # Assuming a parent can have only one student
            student = user.get_profile.students.first()
            bus = student.bus if student else None
        students = Student.objects.filter(bus=bus) if bus else None
        staff_members = Staff.objects.filter(bus=bus) if bus else None
        driver = bus.driver if bus else None
    else:
        user.get_profile = None
        bus = None
        students = None
        staff_members = None
        driver = None
    live_location_url = bus.live_location_url if bus else None

    return render(
        request,
        'dashboard.html',
        {
            'user': user,
            'bus': bus,
            'staff_or_student_roles': staff_or_student_roles,
            'students': students,
            'staff_members': staff_members,
            'driver': driver,
            'live_location_url': live_location_url,
        }
    )

@login_required
def add_student(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        date_of_birth = request.POST.get('date_of_birth')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        department = request.POST.get('department')
        boarding_point = request.POST.get('boarding_point')
        batch = request.POST.get('batch')
        bus_fare_amount = request.POST.get('bus_fare_amount')
        payment_status = request.POST.get('payment_status') == 'True'
        parent_email = request.POST.get('parent_email')
        parent_name = request.POST.get('parent_name')
        parent_contact = request.POST.get('parent_contact')
        parent_password = request.POST.get('parent_password')
        profile_image = request.FILES.get('profile_image')
        password = request.POST.get('password')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return redirect('add_student')

        # Get bus number from staff user
        staff_user = request.user
        bus = staff_user.staff.bus

        # Create or get parent user
        parent_user, created = User.objects.get_or_create(
            username=parent_email,
            defaults={'email': parent_email, 'first_name': parent_name.split()[0],
                      'last_name': ' '.join(parent_name.split()[1:]), 'contact_number': parent_contact,
                      'role': 'Parent'}
        )
        if created:
            parent_user.set_password(parent_password)
            parent_user.save()

        # Create or get parent
        parent, created = Parent.objects.get_or_create(user=parent_user)

        # Create user
        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name,
                                        date_of_birth=date_of_birth, address=address, contact_number=contact_number,
                                        role='Student', profile_image=profile_image)
        user.set_password(password)
        user.save()

        # Create student
        student = Student(user=user, department=department, boarding_point=boarding_point, batch=batch, bus=bus,
                          bus_fare_amount=bus_fare_amount, payment_status=payment_status, parent=parent)
        student.save()

        messages.success(request, 'Student added successfully!')
        return redirect('dashboard')
    return render(request, 'dashboard.html')

@login_required
def bulk_upload_students(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            username = row['username']
            first_name = row['first_name']
            last_name = row['last_name']
            date_of_birth = row['date_of_birth']
            email = row['email']
            contact_number = row['contact_number']
            address = row['address']
            department = row['department']
            boarding_point = row['boarding_point']
            batch = row['batch']
            bus_fare_amount = row['bus_fare_amount']
            payment_status = row['payment_status'] == 'True'
            parent_email = row['parent_email']
            parent_name = row['parent_name']
            parent_contact = row['parent_contact']
            parent_password = row['parent_password']
            profile_image = row.get('profile_image', 'default_profile.png')  # Set default image if not provided
            password = row['password']

            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                continue

            # Get bus number from staff user
            staff_user = request.user
            bus = staff_user.staff.bus

            # Create or get parent user
            parent_user, created = User.objects.get_or_create(
                username=parent_email,
                defaults={'email': parent_email, 'first_name': parent_name.split()[0],
                          'last_name': ' '.join(parent_name.split()[1:]), 'contact_number': parent_contact,
                          'role': 'Parent'}
            )
            if created:
                parent_user.set_password(parent_password)
                parent_user.save()

            # Create or get parent
            parent, created = Parent.objects.get_or_create(user=parent_user)

            # Create user
            user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name,
                                            date_of_birth=date_of_birth, address=address, contact_number=contact_number,
                                            role='Student', profile_image=profile_image)
            user.set_password(password)
            user.save()

            # Create student
            student = Student(user=user, department=department, boarding_point=boarding_point, batch=batch, bus=bus,
                              bus_fare_amount=bus_fare_amount, payment_status=payment_status, parent=parent)
            student.save()

        messages.success(request, 'Students uploaded successfully!')
        return redirect('dashboard')
    return render(request, 'dashboard.html')

@login_required
def update_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        raise Http404("No Student matches the given query.")

    user = student.user  # Assuming there is a OneToOneField from Student to User
    if request.method == 'POST':
        student_form = StudentForm(request.POST, instance=student)
        user_form = UserForm(request.POST, request.FILES, instance=user)
        if student_form.is_valid() and user_form.is_valid():
            student_form.save()
            user_form.save()
            messages.success(request, 'Student details updated successfully!')
            return redirect('dashboard')
    else:
        student_form = StudentForm(instance=student)
        user_form = UserForm(instance=user)
    return render(request, 'accounts/edit_student.html', {'student_form': student_form, 'user_form': user_form})


@login_required
def delete_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        raise Http404("No Student matches the given query.")

    user = student.user
    student.delete()
    user.delete()
    messages.success(request, 'Student deleted successfully!')
    return redirect('dashboard')

