from rest_framework.decorators import api_view , permission_classes
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from .models import JobApplication, JobListing, Employee, Employer, JobApplicationStatus
from .serializers import JobApplicationSerializer, JobListingSerializer, EmployeeSerializer, EmployerSerializer
from .permissions import IsEmployer
import django_filters


# Applying for a lob listing by employee
@api_view(['POST'])
def add_job_application(request, job_listing_id):
    try:
        job_listing = JobListing.objects.get(pk=job_listing_id)
        user = request.user
        employee = Employee.objects.get(user=user)
        application_status = JobApplicationStatus.objects.get(name='AP')  
        application, created = JobApplication.objects.get_or_create(
            job_listing=job_listing,
            applicant=employee,
            defaults={'status': application_status}
        )

        if created:
            return Response({"message": "Job application submitted successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Job application already exists for this job listing."}, status=status.HTTP_400_BAD_REQUEST)
    except JobListing.DoesNotExist:
        return Response({"error": "Job listing does not exist."}, status=status.HTTP_404_NOT_FOUND)
    except Employee.DoesNotExist:
        return Response({"error": "Employee does not exist."}, status=status.HTTP_404_NOT_FOUND)
    except JobApplicationStatus.DoesNotExist:
        return Response({"error": "Application status does not exist."}, status=status.HTTP_404_NOT_FOUND)





# Review list of applications by employer for a job posting
@api_view(['GET'])
@permission_classes([IsEmployer])
def applications_for_job_listing(request, job_listing_id):
    try:
        job_listing = JobListing.objects.get(pk=job_listing_id)
        application_status = JobApplicationStatus.objects.get(name='RE') 
        applications = JobApplication.objects.filter(job_listing=job_listing).exclude(status=  application_status)
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    
    except JobListing.DoesNotExist:
        return Response({"error": "Job listing does not exist."}, status=status.HTTP_404_NOT_FOUND)



# Employer to make a job posting and see jobs of their company
@api_view(['GET', 'POST'])
@permission_classes([IsEmployer])  
def job_listings(request):
    if request.method == 'GET':
        employer = request.user.employer  # Fetch the employer associated with the authenticated user
        job_listings = JobListing.objects.filter(company=employer)
        serializer = JobListingSerializer(job_listings, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = JobListingSerializer(data=request.data)
        serializer.initial_data['company'] = request.user.employer.id
        print(serializer.initial_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Employee to see all job postings with filtering options
@api_view(['GET'])
def job_listings_with_filters(request):
    queryset = JobListing.objects.all()
    filterset = ApplicationFilter(request.GET, queryset=queryset)
    queryset = filterset.qs  # Apply the filter
    serializer = JobListingSerializer(queryset, many=True)
    return Response(serializer.data)

class ApplicationFilter(django_filters.FilterSet):
    class Meta:
        model = JobListing  # Use the correct model for filtering
        fields = '__all__'  # Specify the fields for filtering

# Employee to make an account (create/update)
@api_view(['PUT', 'POST'])
def update_employee_profile(request):
    user = request.user
    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        employee = None
    request.data['user'] = request.user.id

    # put for update and post for new user
    if request.method == 'PUT':
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    elif request.method == 'POST':
        serializer = EmployeeSerializer(data=request.data)
        
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data , status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Employer to make an account (create/update)
@api_view(['PUT', 'POST'])
def update_employer_profile(request):
    user = request.user
    try:
        employer = Employer.objects.get(user=user)
    except Employer.DoesNotExist:
        employer = None

    # put for update and post for new user
    request.data['user'] = request.user.id
    if request.method == 'PUT':
        serializer = EmployerSerializer(employer, data=request.data, partial=True)
    elif request.method == 'POST':
        serializer = EmployerSerializer(data=request.data)
        
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data , status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Employer to manage the application status 
@api_view(['PUT'])
@permission_classes([IsEmployer])
def update_application_status(request, application_id):
    try:
        application = JobApplication.objects.get(pk=application_id)
        
        # Check if the application belongs to the employer's job listing
        if application.job_listing.company != request.user.employer:
            return Response({"error": "You do not have permission to update this application."},
                            status=status.HTTP_403_FORBIDDEN)
        
        # Update the application status
        new_status = request.data.get('status')
        if new_status:
            try:
                status_instance = JobApplicationStatus.objects.get(name=new_status)
                application.status = status_instance
                application.save()
                serializer = JobApplicationSerializer(application)
                return Response(serializer.data)
            except JobApplicationStatus.DoesNotExist:
                return Response({"error": f"Invalid status value '{new_status}'."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Status field is required in the request data."},
                            status=status.HTTP_400_BAD_REQUEST)
    except JobApplication.DoesNotExist:
        return Response({"error": "Job application does not exist."}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def employee_applications(request):
    try:
        user = request.user
        employee = user.employee  
        
        # Retrieve all job applications submitted by the authenticated employee
        applications = JobApplication.objects.filter(applicant=employee)
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def withdraw_application(request, job_application_id):
    try:
        job_application = JobApplication.objects.get(id=job_application_id)
    except JobApplication.DoesNotExist:
        return Response({"error": "Job application does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the current user is the owner of the job application
    if job_application.applicant.user != request.user:
        return Response({"error": "You do not have permission to withdraw this application."}, status=status.HTTP_403_FORBIDDEN)

    # Delete the job application
    job_application.delete()

    return Response({"message": "Job application withdrawn successfully."}, status=status.HTTP_204_NO_CONTENT)


# Employer to update /edit the job listing
@api_view(['PUT', 'PATCH'])
@permission_classes([IsEmployer])
def update_job_listing(request, pk):
    try:
        job_listing = JobListing.objects.get(pk=pk)
        # Check if the logged-in user is the owner of the job listing
        if request.user != job_listing.company.user:
            return Response({"error": "You do not have permission to update this job listing."},
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = JobListingSerializer(job_listing, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except JobListing.DoesNotExist:
        return Response({"error": "Job listing does not exist."}, status=status.HTTP_404_NOT_FOUND)