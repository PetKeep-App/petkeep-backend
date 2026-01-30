from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to access it.
    """
    
    message = "You don't have permission to access this resource."
    
    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted, False otherwise.
        """
        # Admin users have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if the object has a user attribute (Customer, PetSitter models)
        if hasattr(obj, 'user'):
            return obj.user.id == request.user.id
        
        # Check if the object is a User instance
        if hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False


class IsCustomer(permissions.BasePermission):
    """
    Permission to check if user is a customer.
    """
    
    message = "Only customers can access this resource."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is a customer."""
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'user_type') and
            request.user.user_type == 'customer'
        )


class IsPetSitter(permissions.BasePermission):
    """
    Permission to check if user is a petsitter.
    """
    
    message = "Only petsitters can access this resource."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is a petsitter."""
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'user_type') and
            request.user.user_type == 'petsitter'
        )
