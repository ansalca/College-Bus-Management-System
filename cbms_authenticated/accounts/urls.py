from django.urls import path, include

from .views import user_login, user_logout, home, dashboard, add_student, bulk_upload_students, update_student, \
    delete_student

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', home, name='home'),
    path('add_student/', add_student, name='add_student'),
    path('bulk_upload_students/', bulk_upload_students, name='bulk_upload_students'),
    path('student/update/<int:student_id>/', update_student, name='update_student'),
    path('student/delete/<int:student_id>/', delete_student, name='delete_student'),
    # Include default auth URLs
    path('', include('django.contrib.auth.urls')),
]
