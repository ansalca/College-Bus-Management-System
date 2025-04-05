from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Staff, Student, Parent, Bus, Driver


# Custom User admin
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'profile_image', 'first_name', 'last_name', 'email', 'contact_number', 'address', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'contact_number', 'address',
                'date_of_birth', 'role'),
        }),
    )
    list_display = ('username', 'role', 'first_name', 'last_name', 'is_staff', 'contact_number')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'role',)
    ordering = ('username', 'role')


# Custom Staff admin
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'boarding_point', 'bus')
    search_fields = ('user__username', 'department', 'bus__plate_number')
    list_filter = ('department',)


# Custom Student admin
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'batch', 'bus_fare_amount', 'payment_status', 'parent', 'bus')
    search_fields = ('user__username', 'department', 'parent__user__username', 'bus__plate_number')
    list_filter = ('department', 'batch', 'payment_status')


# Custom Parent admin
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)


# Custom Bus admin
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_id', 'plate_number', 'capacity', 'driver')
    search_fields = ('bus_id', 'plate_number', 'driver__user__username')
    list_filter = ('capacity',)


# Custom Driver admin
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', )
    search_fields = ('user__username',)


# Register all models with their custom admin configurations
admin.site.register(User, UserAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(Bus, BusAdmin)
admin.site.register(Driver, DriverAdmin)
