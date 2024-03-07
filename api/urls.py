from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    
    # Add job application by employee
    path('job-listings/<int:job_listing_id>/apply/', add_job_application, name='add_job_application'),

    # Review list of applications by employer for a job posting
    path('job-listings/<int:job_listing_id>/applications/', applications_for_job_listing, name='applications_for_job_listing'),

    # Employer to make a job posting and see jobs of their company
    path('job-listings/', job_listings, name='job_listings'),

    # Employee to see all job postings with filtering options
    path('job-listings/', job_listings_with_filters, name='job_listings_with_filters'),

    # Employee to make an account (update/edit)
    path('employee/update-profile/', update_employee_profile, name='update_employee_profile'),

    # Employer to make an account (update/edit)
    path('employer/update-profile/', update_employer_profile, name='update_employer_profile'),

    # Employee to see all the applications they made
    path('employee/applications/', employee_applications, name='employee_applications'),

    #employer to manage the application status
    path('applications/<int:application_id>/status/', update_application_status, name='update_application_status'),
]
