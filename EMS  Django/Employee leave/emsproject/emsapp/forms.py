from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['father_name', 'dob', 'mobile_number', 'address', 'email']  # Your model fields
