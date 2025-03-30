from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


# Custom User Manager for better user creation
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_('The Username field is required'))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, password, **extra_fields)


# Custom User Model with Roles
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Staff', 'Staff'),
        ('Student', 'Student'),
        ('Driver', 'Driver'),
        ('Parent', 'Parent')
    ]

    contact_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='default_profile.png')
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'contact_number', 'address', 'date_of_birth']

    def __str__(self):
        return self.username


# Staff Model
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    boarding_point = models.CharField(max_length=100, blank=True, null=True)
    bus = models.ForeignKey('Bus', on_delete=models.SET_NULL, null=True, blank=True, related_name='staffs')

    def __str__(self):
        return f'{self.user.username} - {self.department}'


# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    boarding_point = models.CharField(max_length=100, blank=True, null=True)
    bus = models.ForeignKey('Bus', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    batch = models.CharField(max_length=20)
    bus_fare_amount = models.FloatField()
    payment_status = models.BooleanField(default=False)
    parent = models.ForeignKey('Parent', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return self.user.username


# Parent Model
class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


# Bus Model
class Bus(models.Model):
    plate_number = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()
    current_location = models.CharField(max_length=200, null=True, blank=True)
    driver = models.OneToOneField('Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='bus')

    def __str__(self):
        return self.plate_number


# Driver Model
class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.user.username


# Signal to delete parent if no other students are associated
@receiver(post_delete, sender=Student)
def delete_parent_if_no_students(sender, instance, **kwargs):
    parent = instance.parent
    if parent and not parent.students.exists():
        parent.user.delete()
        parent.delete()
