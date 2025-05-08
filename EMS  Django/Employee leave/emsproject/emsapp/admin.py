from django.contrib import admin
# from django.
# Register your models here.
# admin.site.register(User)


from .models import Feedback

# Register the Feedback model
admin.site.register(Feedback)
