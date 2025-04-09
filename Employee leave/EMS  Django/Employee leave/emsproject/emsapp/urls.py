from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('about-us/', views.about_us, name='about_us'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('employee-portal/', views.employee_portal, name='employee_portal'),
    path('login/', views.login, name='login'),
    path('login1/', views.login1, name='login1'),
    path('privacy-and-policy/', views.privacy_and_policy, name='privacy_and_policy'),
    path('profile/', views.profile, name='profile'),
    # path('signup/', views.signup, name='signup'),
    path('register/', views.register, name='register'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
]