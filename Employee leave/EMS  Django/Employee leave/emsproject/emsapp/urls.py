from django.urls import path
from . import views
from .views import employee_portal
from .views import EmployeePortalView, ProfileUpdateView


urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('about-us/', views.about_us, name='about_us'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('employee-portal/', views.employee_portal, name='employee_portal'),
    path('login/', views.login, name='login'),
    # path('login1/', views.login1, name='login1'),
    path('privacy-and-policy/', views.privacy_and_policy, name='privacy_and_policy'),
    path('profile/', views.profile, name='profile'),  # Profile page
    # path('signup/', views.signup, name='signup'),
    path('register/', views.register, name='register'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('update-profile/', ProfileUpdateView.as_view(), name='update_profile'),  
    path('approve_leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject_leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('edit-leave/<int:leave_id>/', views.edit_leave, name='edit_leave'),
    path('delete-leave/<int:leave_id>/', views.delete_leave, name='delete_leave'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('feedback/', views.show_feedback, name='feedback_list'),
    path('logout/', views.logout_view, name='logout'),
]