from django.db import models
from django.contrib.auth.models import User



class JobApplicationStatus(models.Model):
    status_choices = (
        ('AP', 'Applied'),
        ('PR', 'In Progress'),
        ('RE', 'Rejected'),
        ('AC', 'Accepted')
    )
    name = models.CharField(max_length=20, choices=status_choices)

    def __str__(self):
        return self.get_name_display()



class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    years_of_experience = models.IntegerField()
    university = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')
    email = models.EmailField()

    def __str__(self):
        return self.name

class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    company_description = models.TextField()
    email = models.EmailField()

    def __str__(self):
        return self.company_name

class JobListing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Employer, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
class JobApplication(models.Model):
    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    applicant = models.ForeignKey(Employee, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(JobApplicationStatus, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.applicant.name} applied for {self.job_listing.title}"