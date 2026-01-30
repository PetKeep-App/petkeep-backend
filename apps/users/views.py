from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.shortcuts import get_object_or_404
from .serializers import (
    CustomerSignupSerializer, 
    CustomerSerializer, 
    CustomerUpdateSerializer,
    ChangePasswordSerializer
)
from .models import Customer, User


class CustomerSignupView(generics.CreateAPIView):
    """
    API endpoint for customer registration.
    
    Allows new customers to sign up by providing their information.
    No authentication is required for this endpoint.
    """
    
    serializer_class = CustomerSignupSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register a new customer",
        description="Create a new customer account with the provided information.",
        request=CustomerSignupSerializer,
        responses={
            201: OpenApiResponse(
                response=CustomerSerializer,
                description="Customer successfully created"
            ),
            400: OpenApiResponse(
                description="Bad request - validation errors"
            )
        },
        tags=['Customers']
    )
    def post(self, request, *args, **kwargs):
        """Handle customer signup POST request."""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            customer = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CustomerListView(generics.ListAPIView):
    """
    API endpoint for listing all customers.
    
    Requires authentication. Returns a paginated list of all customers.
    """
    
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.select_related('user').all()
    
    @extend_schema(
        summary="List all customers",
        description="Retrieve a paginated list of all registered customers.",
        responses={
            200: OpenApiResponse(
                response=CustomerSerializer(many=True),
                description="List of customers"
            )
        },
        tags=['Customers']
    )
    def get(self, request, *args, **kwargs):
        """Handle GET request for customer list."""
        return super().get(request, *args, **kwargs)


class CustomerDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific customer.
    
    Requires authentication. Returns details of a single customer.
    """
    
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.select_related('user').all()
    lookup_field = 'user_id'
    
    @extend_schema(
        summary="Get customer details",
        description="Retrieve detailed information about a specific customer.",
        responses={
            200: OpenApiResponse(
                response=CustomerSerializer,
                description="Customer details"
            ),
            404: OpenApiResponse(
                description="Customer not found"
            )
        },
        tags=['Customers']
    )
    def get(self, request, *args, **kwargs):
        """Handle GET request for customer detail."""
        return super().get(request, *args, **kwargs)


class CustomerUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating customer information.
    
    Requires authentication. Customers can only update their own information.
    """
    
    serializer_class = CustomerUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.select_related('user').all()
    lookup_field = 'user_id'
    
    def get_object(self):
        """Ensure users can only update their own profile."""
        customer_id = self.kwargs.get('user_id')
        customer = get_object_or_404(Customer, user_id=customer_id)
        
        # Check if user is updating their own profile or is staff
        if customer.user.id != self.request.user.id and not self.request.user.is_staff:
            self.permission_denied(
                self.request,
                message="You don't have permission to update this customer."
            )
        
        return customer
    
    @extend_schema(
        summary="Update customer information",
        description="Update customer profile information (full_name, phone).",
        request=CustomerUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=CustomerSerializer,
                description="Customer updated successfully"
            ),
            400: OpenApiResponse(
                description="Bad request - validation errors"
            ),
            403: OpenApiResponse(
                description="Forbidden - can only update own profile"
            ),
            404: OpenApiResponse(
                description="Customer not found"
            )
        },
        tags=['Customers']
    )
    def put(self, request, *args, **kwargs):
        """Handle PUT request for customer update."""
        return self.update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update customer information",
        description="Partially update customer profile information.",
        request=CustomerUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=CustomerSerializer,
                description="Customer updated successfully"
            ),
            400: OpenApiResponse(
                description="Bad request - validation errors"
            ),
            403: OpenApiResponse(
                description="Forbidden - can only update own profile"
            ),
            404: OpenApiResponse(
                description="Customer not found"
            )
        },
        tags=['Customers']
    )
    def patch(self, request, *args, **kwargs):
        """Handle PATCH request for customer partial update."""
        return self.partial_update(request, *args, **kwargs)


class CustomerDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting/deactivating a customer.
    
    Requires authentication. Performs soft delete by setting is_active to False.
    """
    
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.select_related('user').all()
    lookup_field = 'user_id'
    
    def get_object(self):
        """Ensure users can only delete their own profile or is staff."""
        customer_id = self.kwargs.get('user_id')
        customer = get_object_or_404(Customer, user_id=customer_id)
        
        # Check if user is deleting their own profile or is staff
        if customer.user.id != self.request.user.id and not self.request.user.is_staff:
            self.permission_denied(
                self.request,
                message="You don't have permission to delete this customer."
            )
        
        return customer
    
    @extend_schema(
        summary="Delete customer account",
        description="Soft delete a customer account by deactivating it (sets is_active to False).",
        responses={
            204: OpenApiResponse(
                description="Customer deactivated successfully"
            ),
            403: OpenApiResponse(
                description="Forbidden - can only delete own profile"
            ),
            404: OpenApiResponse(
                description="Customer not found"
            )
        },
        tags=['Customers']
    )
    def delete(self, request, *args, **kwargs):
        """Handle DELETE request - performs soft delete."""
        customer = self.get_object()
        
        # Soft delete - just deactivate the user
        customer.user.is_active = False
        customer.user.save()
        
        return Response(
            {'message': 'Customer account deactivated successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )


class ChangePasswordView(generics.GenericAPIView):
    """
    API endpoint for changing customer password.
    
    Requires authentication. Customers can only change their own password.
    """
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Change customer password",
        description="Change the password for the authenticated customer.",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Password changed successfully"
            ),
            400: OpenApiResponse(
                description="Bad request - validation errors"
            )
        },
        tags=['Customers']
    )
    def post(self, request, *args, **kwargs):
        """Handle password change POST request."""
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Password changed successfully.'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
