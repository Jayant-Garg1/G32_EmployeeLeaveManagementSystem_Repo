from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.urls import reverse_lazy
from .models import LeaveRequest, Profile
from .forms import ProfileForm
from django.views.generic import TemplateView, UpdateView
from datetime import datetime
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Feedback
from django.contrib.auth import logout
from django.http import JsonResponse
from django.template.loader import render_to_string
import requests

FLASK_API_BASE_URL = "http://127.0.0.1:5000/api"


def home_page(request):
    return render(request, "home_page.html")

def about_us(request):
    response = requests.get(f"{FLASK_API_BASE_URL}/about_us")
    html_content = response.json().get("html", "")
    return render(request, "about_us.html", {"html_content": html_content})

def privacy_and_policy(request):
    response = requests.get(f"{FLASK_API_BASE_URL}/privacy_and_policy")
    html_content = response.json().get("html", "")
    return render(request, "privacy_and_policy.html", {"html_content": html_content})

def terms_and_conditions(request):
    response = requests.get(f"{FLASK_API_BASE_URL}/terms_and_conditions")
    html_content = response.json().get("html", "")
    return render(request, "terms_and_conditions.html", {"html_content": html_content})


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Password does not match')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')

        user = User.objects.create(
            username=username,
            first_name=name,
            email=email,
            password=make_password(password),
            is_staff=False
        )
        messages.success(request, 'Signup successful! You can now login.')
        return redirect('login')

    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            auth_login(request, user)

            Profile.objects.get_or_create(user=user)

            if user.is_staff:
                return redirect('admin_portal')
            else:
                return redirect('employee_portal')

        else:
            messages.error(request, 'Invalid Username or Password')
    return render(request, 'login.html')


@login_required
def employee_portal(request):
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        profile, created = Profile.objects.get_or_create(user=request.user)

        try:
            start_date_obj = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('employee_portal')

        if start_date_obj < timezone.now().date():
            messages.error(request, 'You cannot apply for leave with a start date in the past.')
        elif end_date_obj < start_date_obj:
            messages.error(request, 'End date cannot be before start date.')
        else:
            leave_duration = (end_date_obj - start_date_obj).days + 1

            if leave_type == 'Sick Leave' and profile.sick_leave_balance < leave_duration:
                messages.error(request, 'Insufficient sick leave balance.')
                return redirect('employee_portal')

            elif leave_type == 'Personal Leave' and profile.personal_leave_balance < leave_duration:
                messages.error(request, 'Insufficient personal leave balance.')
                return redirect('employee_portal')

            elif leave_type == 'Vacation' and profile.vacation_leave_balance < leave_duration:
                messages.error(request, 'Insufficient vacation leave balance.')
                return redirect('employee_portal')

            LeaveRequest.objects.create(
                user=request.user,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                status='Pending'
            )

            if leave_type == 'Sick Leave':
                profile.sick_leave_balance -= leave_duration
            elif leave_type == 'Personal Leave':
                profile.personal_leave_balance -= leave_duration
            elif leave_type == 'Vacation':
                profile.vacation_leave_balance -= leave_duration

            profile.save()
            messages.success(request, 'Leave application submitted successfully.')
            return redirect('employee_portal')

    leave_requests = LeaveRequest.objects.filter(user=request.user).order_by('-start_date')
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "employee_portal.html", {
        'leave_requests': leave_requests,
        'current_user': request.user,
        'profile': profile
    })

class EmployeePortalView(TemplateView):
    template_name = 'employee_portal.html'


@login_required
def profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    next_page = request.GET.get('next') or request.POST.get('next') or 'employee_portal'

    if request.method == 'POST':
        new_email = request.POST.get('email')
        new_username = request.POST.get('username')

        if new_email and new_email != user.email:
            user.email = new_email
        if new_username and new_username != user.username:
            user.username = new_username
        user.save()

        dob_str = request.POST.get('dob')
        try:
            if dob_str:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                profile.dob = dob
        except ValueError:
            messages.error(request, 'Invalid date format for DOB.')
            return redirect('profile')

        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']

        profile.mobile_number = request.POST.get('mobile_number')
        profile.address = request.POST.get('address')
        profile.father_name = request.POST.get('father_name')
        profile.mother_name = request.POST.get('mother_name')

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect(next_page)

    return render(request, 'profile.html', {'user': user, 'profile': profile})

class ProfileUpdateView(UpdateView):
    model = Profile
    fields = ['father_name', 'dob', 'mobile_number', 'address', 'email']
    template_name = 'profile_form.html'
    success_url = reverse_lazy('employee_portal')

    def form_valid(self, form):
        messages.success(self.request, 'Your profile information has been updated successfully.')
        return super().form_valid(form)



@user_passes_test(lambda u: u.is_staff)
def admin_portal(request):
    search_query = request.GET.get('search', '')  

    if search_query:
        leave_requests = LeaveRequest.objects.filter(
            Q(user__first_name__icontains=search_query) | Q(user__last_name__icontains=search_query)
        ).order_by('-start_date')
    else:
        leave_requests = LeaveRequest.objects.all().order_by('-start_date')

    return render(request, "admin_portal.html", {
        'leave_requests': leave_requests,
        'search_query': search_query
    })


@user_passes_test(lambda u: u.is_staff)
def approve_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = 'Approved'
    leave.save()
    messages.success(request, f"Leave for {leave.user.username} approved.")
    return redirect('admin_portal')


@user_passes_test(lambda u: u.is_staff)
def reject_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = 'Rejected'
    leave.save()
    messages.success(request, f"Leave for {leave.user.username} rejected.")
    return redirect('admin_portal')

@login_required
def edit_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id, user=request.user)

    if leave.status != 'Pending':
        messages.error(request, "You can only edit pending leave requests.")
        return redirect('employee_portal')

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            today = timezone.now().date()

            if start_date_obj < today:
                messages.error(request, "Start date cannot be in the past.")
                return redirect('edit_leave', leave_id=leave.id)

            if end_date_obj < start_date_obj:
                messages.error(request, "End date cannot be before start date.")
                return redirect('edit_leave', leave_id=leave.id)

            profile = Profile.objects.get(user=request.user)

            original_duration = (leave.end_date - leave.start_date).days + 1
            new_duration = (end_date_obj - start_date_obj).days + 1

            duration_difference = new_duration - original_duration

            if leave_type == 'Sick Leave':
                if profile.sick_leave_balance + original_duration < new_duration:
                    messages.error(request, "Insufficient sick leave balance.")
                    return redirect('edit_leave', leave_id=leave.id)
                profile.sick_leave_balance -= duration_difference

            elif leave_type == 'Personal Leave':
                if profile.personal_leave_balance + original_duration < new_duration:
                    messages.error(request, "Insufficient personal leave balance.")
                    return redirect('edit_leave', leave_id=leave.id)
                profile.personal_leave_balance -= duration_difference

            elif leave_type == 'Vacation':
                if profile.vacation_leave_balance + original_duration < new_duration:
                    messages.error(request, "Insufficient vacation leave balance.")
                    return redirect('edit_leave', leave_id=leave.id)
                profile.vacation_leave_balance -= duration_difference

            profile.save()

            leave.leave_type = leave_type
            leave.start_date = start_date_obj
            leave.end_date = end_date_obj
            leave.save()

            messages.success(request, "Leave request updated.")
            return redirect('employee_portal')

        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('edit_leave', leave_id=leave.id)

    return render(request, 'edit_leave.html', {'leave': leave})

@login_required
def delete_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id, user=request.user)

    if leave.status == 'Pending':
        profile = Profile.objects.get(user=request.user)

        leave_duration = (leave.end_date - leave.start_date).days + 1

        if leave.leave_type == 'Sick Leave':
            profile.sick_leave_balance += leave_duration
        elif leave.leave_type == 'Personal Leave':
            profile.personal_leave_balance += leave_duration
        elif leave.leave_type == 'Vacation':
            profile.vacation_leave_balance += leave_duration

        profile.save()

        leave.delete()
        messages.success(request, "Leave request deleted and balance updated.")
    else:
        messages.error(request, "Only pending requests can be deleted.")
    
    return redirect('employee_portal')


def submit_feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        response = requests.post(f"{FLASK_API_BASE_URL}/submit_feedback", data={
            'name': name,
            'email': email,
            'message': message
        })

        if response.status_code == 201:
            messages.success(request, "Feedback submitted successfully!")
        else:
            messages.error(request, "Failed to submit feedback.")

        return redirect('feedback_list')

def feedback_list(request):
    response = requests.get(f"{FLASK_API_BASE_URL}/feedback_list")
    feedbacks = response.json() if response.status_code == 200 else []
    return render(request, "feedback_list.html", {"feedback_list": feedbacks})


def show_feedback(request):
    feedback_list = Feedback.objects.all()  
    return render(request, 'feedback_list.html', {'feedback_list': feedback_list})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home_page')
