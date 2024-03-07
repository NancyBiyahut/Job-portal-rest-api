from rest_framework.permissions import BasePermission

class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and an employer
        return request.user.is_authenticated and hasattr(request.user, 'employer')
