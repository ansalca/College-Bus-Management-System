from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Student, User


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'contact_number', 'address', 'date_of_birth', 'profile_image']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['department', 'boarding_point', 'batch', 'bus_fare_amount', 'payment_status']