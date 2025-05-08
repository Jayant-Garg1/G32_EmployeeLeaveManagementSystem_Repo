from django.urls import path, include
from . import views
from django.contrib import admin

app_name = 'app2'

urlpatterns = [
    path('admin/events/', views.events_dashboard, name='admin_event_list'),  # THIS ONE
    path('admin/events/create/', views.create_event, name='create_event'),
    path('admin/events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('admin/events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('admin/events/add/', views.add_event, name='add_event'),
    path('admin/', admin.site.urls),
    path('events/', views.employee_event_list, name='employee_event_list'),
    path('employee/events/', views.employee_event_list, name='employee_event_list'),
    path('register/', views.employee_register, name='employee_register'),
    path('employee/register-event/<int:event_id>/', views.register_for_event, name='register_for_event'),
    path('staff/event/<int:event_id>/registrations/', views.view_registrations, name='view_registrations'),

]





