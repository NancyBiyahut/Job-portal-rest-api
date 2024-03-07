from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(JobApplicationStatus)
admin.site.register(JobListing)
admin.site.register(JobApplication)
admin.site.register(Employer)
admin.site.register(Employee)
