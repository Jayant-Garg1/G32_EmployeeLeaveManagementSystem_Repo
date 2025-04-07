from django.shortcuts import render

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

def signup(request):
    return render(request, "signup.html")

def terms_and_conditions(request):
    return render(request, "terms_and_conditions.html")