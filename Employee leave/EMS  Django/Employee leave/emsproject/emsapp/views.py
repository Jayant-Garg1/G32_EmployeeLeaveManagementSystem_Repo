from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.hashers import make_password

def home_page(request):
    return render(request, "home_page.html")

def about_us(request):
    return render(request, "about_us.html")

def admin_portal(request):
    return render(request, "admin_portal.html")

def employee_portal(request):
    return render(request, "employee_portal.html")

def login(request):
    return render(request, "login.html")

def login1(request):
    return render(request, "login1.html")

def privacy_and_policy(request):
    return render(request, "privacy_and_policy.html")

def profile(request):
    return render(request, "profile.html")

# def signup(request):
#     return render(request, "signup.html")

def terms_and_conditions(request):
    return render(request, "terms_and_conditions.html")


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password!=confirm_password:
            messages.error(request,'Password does not match')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request,'Email already exists')
            return redirect('register')

        user = User.objects.create(
            username=username,
            first_name=name,
            email=email,
            password=make_password(password),
            is_staff=False,
        )
        messages.success(request, 'Signup successful! You can now login.')
        return redirect('login')

    return render(request,'register.html')



def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            auth_login(request, user)
            return redirect('employee_portal')
        else:
            messages.error(request, 'Invalid Username or Password')
    return render(request, 'login.html')

