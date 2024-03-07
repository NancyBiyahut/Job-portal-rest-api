from rest_framework import serializers
from .models import JobApplication, JobListing, Employee, Employer, JobApplicationStatus

class JobApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplicationStatus
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'

class JobListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobListing
        fields = ['id', 'title', 'description', 'location', 'salary', 'company']
        
class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = EmployeeSerializer(read_only=True)
    status = JobApplicationStatusSerializer(read_only=True)

    class Meta:
        model = JobApplication
        fields = '__all__'
