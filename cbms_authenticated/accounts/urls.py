from django.urls import path, include

from .views import user_login, user_logout, home, dashboard

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', home, name='home'),
    # Include default auth URLs
    path('', include('django.contrib.auth.urls')),
]
