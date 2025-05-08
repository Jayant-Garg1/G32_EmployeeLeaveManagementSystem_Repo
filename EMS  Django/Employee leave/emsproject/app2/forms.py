from django import forms
from .models import Event
from .models import Employee
from .models import EventRegistration

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'start_time', 'end_time']  # 👈 update here!
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }



class EmployeeRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = ['full_name', 'email', 'employee_id', 'password']



class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['employee', 'event']
