
from django.db import models
from django.contrib.auth.models import User

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('Sick Leave', 'Sick Leave'),
        ('Vacation', 'Vacation'),
        ('Personal Leave', 'Personal Leave'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sick_leave_balance = models.IntegerField(default=10)  # Default sick leaves
    personal_leave_balance = models.IntegerField(default=5)  # Default personal leaves
    vacation_leave_balance = models.IntegerField(default=5)
    email = models.EmailField(default="example@example.com")  # Add this line for a default value
    dob = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=False, default="Not provided")  # Define a default value here
    address = models.CharField(max_length=255, null=False, default="No address provided")  # Define a default value here
    father_name = models.CharField(max_length=255, null=False, default="Unknown")
    mother_name = models.CharField(max_length=255, null=False, default="Unknown")

    def __str__(self):
        return self.user.username



class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
