from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Event
from .forms import EventForm
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
from .models import Event
from .models import Event, Employee, EventRegistration

# ---------------- Admin Views ----------------

@user_passes_test(lambda u: u.is_staff)
def admin_event_list(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'admin_events.html', {'events': events})

@user_passes_test(lambda u: u.is_staff)
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully.")
            return redirect('app2:admin_event_list')
    else:
        form = EventForm()
    return render(request, 'event_form.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('app2:admin_event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'edit_event.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event.delete()
    return redirect('app2:admin_event_list')

# ---------------- Employee View ----------------

@login_required
@login_required
def employee_event_list(request):
    # Get today's date
    today = now().date()

    # Get all events from the database
    all_events = Event.objects.all().order_by('date')

    # Filter upcoming events (events that are today or later)
    upcoming_events = all_events.filter(date__gte=today)

    # Filter past events (events that happened before today)
    past_events = all_events.filter(date__lt=today)

    # Render the events to the template
    return render(request, 'employee_events.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events
    })

@user_passes_test(lambda u: u.is_staff)
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app2:admin_event_list')
    else:
        form = EventForm()
    return render(request, 'event_form.html', {
        'form': form,
        'form_title': 'Add Event',
        'button_text': 'Create'
    })


from .forms import EmployeeRegistrationForm

def employee_register(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_events.html') 
    else:
        form = EmployeeRegistrationForm()
    return render(request, 'app2/employee_register.html', {'form': form})


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Your employee profile is missing.")
        return redirect('app2:employee_event_list')  

    if EventRegistration.objects.filter(event=event, employee=employee).exists():
        messages.info(request, "You have already registered for this event.")
    else:
        EventRegistration.objects.create(event=event, employee=employee)
        messages.success(request, "You have registered successfully.")

    return redirect('app2:employee_event_list')

def view_registrations(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registrations = EventRegistration.objects.filter(event=event)

    return render(request, 'app2/view_registrations.html', {
        'event': event,
        'registrations': registrations
    })

from datetime import date
from django.utils.timezone import now

def events_dashboard(request):
    all_events = Event.objects.all().order_by('date')
    today = now().date()
    upcoming_events = all_events.filter(date__gte=today)
    past_events = all_events.filter(date__lt=today)

    return render(request, 'admin_events.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events
    })

