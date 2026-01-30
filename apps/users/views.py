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
    ChangePasswordSerializer,
    PetSitterSignupSerializer,
    PetSitterSerializer,
    PetSitterUpdateSerializer
)
from .models import Customer, User, PetSitter


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


# ============================================================================
# PETSITTER VIEWS
# ============================================================================

class PetSitterSignupView(generics.CreateAPIView):
    """
    API endpoint for petsitter registration.
    
    Allows new petsitters to sign up by providing their information.
    No authentication is required for this endpoint.
    """
    
    serializer_class = PetSitterSignupSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register a new petsitter",
        description="Create a new petsitter account with the provided information.",
        request=PetSitterSignupSerializer,
        responses={
            201: OpenApiResponse(
                response=PetSitterSerializer,
                description="PetSitter successfully created"
            ),
            400: OpenApiResponse(
                description="Bad request - validation errors"
            )
        },
        tags=['PetSitters']
    )
    def post(self, request, *args, **kwargs):
        """Handle petsitter signup POST request."""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            petsitter = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PetSitterListView(generics.ListAPIView):
    """
    API endpoint for listing all petsitters.
    
    Requires authentication. Returns a paginated list of all petsitters.
    """
    
    serializer_class = PetSitterSerializer
    permission_classes = [IsAuthenticated]
    queryset = PetSitter.objects.select_related('user').prefetch_related(
        'animal_types', 'service_types'
    ).all()
    
    @extend_schema(
        summary="List all petsitters",
        description="Retrieve a paginated list of all registered petsitters.",
        responses={
            200: OpenApiResponse(
                response=PetSitterSerializer(many=True),
                description="List of petsitters"
            )
        },
        tags=['PetSitters']
    )
    def get(self, request, *args, **kwargs):
        """Handle GET request for petsitter list."""
        return super().get(request, *args, **kwargs)


class PetSitterDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific petsitter.
    
    Requires authentication. Returns details of a single petsitter.
    """
    
    serializer_class = PetSitterSerializer
    permission_classes = [IsAuthenticated]
    queryset = PetSitter.objects.select_related('user').prefetch_related(
        'animal_types', 'service_types'
    ).all()
    lookup_field = 'user_id'
    
    @extend_schema(
        summary="Get petsitter details",
        description="Retrieve detailed information about a specific petsitter.",
        responses={
            200: OpenApiResponse(
                response=PetSitterSerializer,
                description="PetSitter details"
            ),
            404: OpenApiResponse(
                description="PetSitter not found"
            )
        },
        tags=['PetSitters']
    )
    def get(self, request, *args, **kwargs):
        """Handle GET request for petsitter detail."""
        return super().get(request, *args, **kwargs)


class PetSitterUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating petsitter information.
    
    Requires authentication. Petsitters can only update their own information.
    """
    
    serializer_class = PetSitterUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = PetSitter.objects.select_related('user').prefetch_related(
        'animal_types', 'service_types'
    ).all()
    lookup_field = 'user_id'
    
    def get_object(self):
        """Ensure users can only update their own profile."""
        petsitter_id = self.kwargs.get('user_id')
        petsitter = get_object_or_404(PetSitter, user_id=petsitter_id)
        
        # Check if user is updating their own profile or is staff
        if petsitter.user.id != self.request.user.id and not self.request.user.is_staff:
            self.permission_denied(
                self.request,
                message="You don't have permission to update this petsitter."
            )
        
        return petsitter
    
    @extend_schema(
        summary="Update petsitter information",
        description="Update petsitter profile information.",
        request=PetSitterUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=PetSitterSerializer,
                description="PetSitter updated successfully"
            ),
            400: OpenApiResponse(
                description="Bad request - validation errors"
            ),
            403: OpenApiResponse(
                description="Forbidden - can only update own profile"
            ),
            404: OpenApiResponse(
                description="PetSitter not found"
            )
        },
        tags=['PetSitters']
    )
    def put(self, request, *args, **kwargs):
        """Handle PUT request for petsitter update."""
        return self.update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update petsitter information",
        description="Partially update petsitter profile information.",
        request=PetSitterUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=PetSitterSerializer,
                description="PetSitter updated successfully"
            ),
            400: OpenApiResponse(
                description="Bad request - validation errors"
            ),
            403: OpenApiResponse(
                description="Forbidden - can only update own profile"
            ),
            404: OpenApiResponse(
                description="PetSitter not found"
            )
        },
        tags=['PetSitters']
    )
    def patch(self, request, *args, **kwargs):
        """Handle PATCH request for petsitter partial update."""
        return self.partial_update(request, *args, **kwargs)


class PetSitterDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting/deactivating a petsitter.
    
    Requires authentication. Performs soft delete by setting is_active to False.
    """
    
    permission_classes = [IsAuthenticated]
    queryset = PetSitter.objects.select_related('user').all()
    lookup_field = 'user_id'
    
    def get_object(self):
        """Ensure users can only delete their own profile or is staff."""
        petsitter_id = self.kwargs.get('user_id')
        petsitter = get_object_or_404(PetSitter, user_id=petsitter_id)
        
        # Check if user is deleting their own profile or is staff
        if petsitter.user.id != self.request.user.id and not self.request.user.is_staff:
            self.permission_denied(
                self.request,
                message="You don't have permission to delete this petsitter."
            )
        
        return petsitter
    
    @extend_schema(
        summary="Delete petsitter account",
        description="Soft delete a petsitter account by deactivating it (sets is_active to False).",
        responses={
            204: OpenApiResponse(
                description="PetSitter deactivated successfully"
            ),
            403: OpenApiResponse(
                description="Forbidden - can only delete own profile"
            ),
            404: OpenApiResponse(
                description="PetSitter not found"
            )
        },
        tags=['PetSitters']
    )
    def delete(self, request, *args, **kwargs):
        """Handle DELETE request - performs soft delete."""
        petsitter = self.get_object()
        
        # Soft delete - just deactivate the user
        petsitter.user.is_active = False
        petsitter.user.save()
        
        return Response(
            {'message': 'PetSitter account deactivated successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )
