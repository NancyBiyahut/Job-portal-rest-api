from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import JobApplication, JobListing, Employee, Employer, JobApplicationStatus
from .serializers import JobApplicationSerializer, JobListingSerializer, EmployeeSerializer, EmployerSerializer
from .permissions import IsEmployer



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
        applications = JobApplication.objects.filter(job_listing=job_listing)
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
    # Implement filtering options based on request parameters
    # For example, filter by location, salary range, etc.
    # queryset = apply_filters(request, queryset)
    serializer = JobListingSerializer(queryset, many=True)
    return Response(serializer.data)




# Employee to make an account (update/edit)
@api_view(['PUT'])
def update_employee_profile(request):
    user = request.user
    employee = Employee.objects.get(user=user)
    serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Employer to make an account (update/edit)
@api_view(['PUT'])
def update_employer_profile(request):
    user = request.user
    employer = Employer.objects.get(user=user)
    serializer = EmployerSerializer(employer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
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