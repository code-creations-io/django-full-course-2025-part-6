from rest_framework.permissions import BasePermission, SAFE_METHODS

class ReadOnly(BasePermission):
    """Allow all safe (GET, HEAD, OPTIONS) requests."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS