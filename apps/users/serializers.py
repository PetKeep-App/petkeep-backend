from typing import Any, Dict, Optional
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from .models import User, Customer, PetSitter, AnimalType, ServiceType


# ============================================================================
# AUTHENTICATION SERIALIZERS
# ============================================================================

class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.'
        }
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank.'
        }
    )
    
    def validate(self, attrs):
        """Authenticate user credentials."""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.'
                )
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError(
            'Must include "email" and "password".'
        )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for authenticated user information."""
    
    profile_type = serializers.SerializerMethodField()
    profile_data = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone', 'user_type',
            'is_active', 'profile_type', 'profile_data',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'user_type', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.CharField())
    def get_profile_type(self, obj: User) -> str:
        """Return the type of profile (customer or petsitter)."""
        return obj.user_type
    
    @extend_schema_field(serializers.DictField())
    def get_profile_data(self, obj: User) -> Optional[Dict[str, Any]]:
        """Return profile-specific data based on user type."""
        if obj.user_type == 'customer':
            try:
                customer = obj.customer_profile
                return {
                    'id': customer.user.id,
                    'created_at': customer.created_at,
                    'updated_at': customer.updated_at
                }
            except Customer.DoesNotExist:
                return None
        
        elif obj.user_type == 'petsitter':
            try:
                petsitter = obj.petsitter_profile
                from .serializers import PetSitterSerializer
                # Use the full serializer for petsitters
                return PetSitterSerializer(petsitter).data
            except PetSitter.DoesNotExist:
                return None
        
        return None


# ============================================================================
# CUSTOMER SERIALIZERS
# ============================================================================

class CustomerSignupSerializer(serializers.Serializer):
    """Serializer for customer signup/registration."""
    
    full_name = serializers.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': 'Full name is required.',
            'blank': 'Full name cannot be blank.'
        }
    )
    
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.'
        }
    )
    
    phone = serializers.CharField(
        max_length=20,
        required=True,
        error_messages={
            'required': 'Phone is required.',
            'blank': 'Phone cannot be blank.'
        }
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank.'
        }
    )
    
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Password confirmation is required.',
            'blank': 'Password confirmation cannot be blank.'
        }
    )
    
    def validate_email(self, value):
        """Check if email is already registered."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value.lower()
    
    def validate_password(self, value):
        """Validate password using Django's password validators."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create user and customer profile."""
        # Remove confirm_password as it's not needed for model creation
        validated_data.pop('confirm_password')
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone=validated_data['phone'],
            user_type='customer'
        )
        
        # Create customer profile
        customer = Customer.objects.create(user=user)
        
        return customer
    
    def to_representation(self, instance):
        """Return customer data without sensitive information."""
        return {
            'id': instance.user.id,
            'email': instance.user.email,
            'full_name': instance.user.full_name,
            'phone': instance.user.phone,
            'user_type': instance.user.user_type,
            'created_at': instance.created_at,
        }


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer data retrieval."""
    
    id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'email', 'full_name', 'phone', 'is_active', 'user_type', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CustomerUpdateSerializer(serializers.Serializer):
    """Serializer for updating customer information."""
    
    full_name = serializers.CharField(
        max_length=255,
        required=False,
        error_messages={
            'blank': 'Full name cannot be blank.'
        }
    )
    
    phone = serializers.CharField(
        max_length=20,
        required=False,
        error_messages={
            'blank': 'Phone cannot be blank.'
        }
    )
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update customer user information."""
        user = instance.user
        
        if 'full_name' in validated_data:
            user.full_name = validated_data['full_name']
        
        if 'phone' in validated_data:
            user.phone = validated_data['phone']
        
        user.save()
        instance.save()
        
        return instance
    
    def to_representation(self, instance):
        """Return updated customer data."""
        return CustomerSerializer(instance).data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing customer password."""
    
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Old password is required.',
            'blank': 'Old password cannot be blank.'
        }
    )
    
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'New password is required.',
            'blank': 'New password cannot be blank.'
        }
    )
    
    confirm_new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Password confirmation is required.',
            'blank': 'Password confirmation cannot be blank.'
        }
    )
    
    def validate_old_password(self, value):
        """Validate old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
    
    def validate_new_password(self, value):
        """Validate new password using Django's password validators."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs.get('new_password') != attrs.get('confirm_new_password'):
            raise serializers.ValidationError({
                'confirm_new_password': 'Passwords do not match.'
            })
        return attrs
    
    def save(self):
        """Change the user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


# ============================================================================
# PETSITTER SERIALIZERS
# ============================================================================

class AnimalTypeSerializer(serializers.ModelSerializer):
    """Serializer for AnimalType model."""
    
    display_name = serializers.CharField(source='get_animal_type_display', read_only=True)
    
    class Meta:
        model = AnimalType
        fields = ['id', 'animal_type', 'display_name']


class ServiceTypeSerializer(serializers.ModelSerializer):
    """Serializer for ServiceType model."""
    
    display_name = serializers.CharField(source='get_service_type_display', read_only=True)
    
    class Meta:
        model = ServiceType
        fields = ['id', 'service_type', 'display_name']


class PetSitterSerializer(serializers.ModelSerializer):
    """Serializer for petsitter data retrieval."""
    
    id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    animal_types = AnimalTypeSerializer(many=True, read_only=True)
    service_types = ServiceTypeSerializer(many=True, read_only=True)
    
    class Meta:
        model = PetSitter
        fields = [
            'id', 'email', 'full_name', 'phone', 'is_active', 'user_type',
            'location', 'about', 'animal_types', 'service_types', 'other_animals',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PetSitterSignupSerializer(serializers.Serializer):
    """Serializer for petsitter signup/registration."""
    
    full_name = serializers.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': 'Full name is required.',
            'blank': 'Full name cannot be blank.'
        }
    )
    
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.'
        }
    )
    
    phone = serializers.CharField(
        max_length=20,
        required=True,
        error_messages={
            'required': 'Phone is required.',
            'blank': 'Phone cannot be blank.'
        }
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank.'
        }
    )
    
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Password confirmation is required.',
            'blank': 'Password confirmation cannot be blank.'
        }
    )
    
    location = serializers.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': 'Location is required.',
            'blank': 'Location cannot be blank.'
        }
    )
    
    about = serializers.CharField(
        required=True,
        error_messages={
            'required': 'About field is required.',
            'blank': 'About field cannot be blank.'
        }
    )
    
    animal_types = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=False,
        error_messages={
            'required': 'At least one animal type is required.',
            'empty': 'At least one animal type must be selected.'
        }
    )
    
    other_animals = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    
    service_types = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=False,
        error_messages={
            'required': 'At least one service type is required.',
            'empty': 'At least one service type must be selected.'
        }
    )
    
    def validate_email(self, value):
        """Check if email is already registered."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value.lower()
    
    def validate_password(self, value):
        """Validate password using Django's password validators."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate_animal_types(self, value):
        """Validate that animal types exist."""
        valid_types = [choice[0] for choice in AnimalType.ANIMAL_CHOICES]
        for animal_type in value:
            if animal_type not in valid_types:
                raise serializers.ValidationError(f'Invalid animal type: {animal_type}')
        return value
    
    def validate_service_types(self, value):
        """Validate that service types exist."""
        valid_types = [choice[0] for choice in ServiceType.SERVICE_CHOICES]
        for service_type in value:
            if service_type not in valid_types:
                raise serializers.ValidationError(f'Invalid service type: {service_type}')
        return value
    
    def validate(self, attrs):
        """Validate that passwords match and other_animals if 'other' is selected."""
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        
        # If 'other' is selected in animal_types, other_animals must be provided
        if 'other' in attrs.get('animal_types', []):
            if not attrs.get('other_animals'):
                raise serializers.ValidationError({
                    'other_animals': 'Please specify other animals when "Outros" is selected.'
                })
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create user and petsitter profile."""
        # Remove fields not needed for user creation
        validated_data.pop('confirm_password')
        animal_types = validated_data.pop('animal_types')
        service_types = validated_data.pop('service_types')
        location = validated_data.pop('location')
        about = validated_data.pop('about')
        other_animals = validated_data.pop('other_animals', '')
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone=validated_data['phone'],
            user_type='petsitter'
        )
        
        # Create petsitter profile
        petsitter = PetSitter.objects.create(
            user=user,
            location=location,
            about=about,
            other_animals=other_animals
        )
        
        # Add animal types (create if don't exist)
        for animal_type in animal_types:
            animal_obj, _ = AnimalType.objects.get_or_create(animal_type=animal_type)
            petsitter.animal_types.add(animal_obj)
        
        # Add service types (create if don't exist)
        for service_type in service_types:
            service_obj, _ = ServiceType.objects.get_or_create(service_type=service_type)
            petsitter.service_types.add(service_obj)
        
        return petsitter
    
    def to_representation(self, instance):
        """Return petsitter data without sensitive information."""
        return PetSitterSerializer(instance).data


class PetSitterUpdateSerializer(serializers.Serializer):
    """Serializer for updating petsitter information."""
    
    full_name = serializers.CharField(
        max_length=255,
        required=False,
        error_messages={'blank': 'Full name cannot be blank.'}
    )
    
    phone = serializers.CharField(
        max_length=20,
        required=False,
        error_messages={'blank': 'Phone cannot be blank.'}
    )
    
    location = serializers.CharField(
        max_length=255,
        required=False,
        error_messages={'blank': 'Location cannot be blank.'}
    )
    
    about = serializers.CharField(
        required=False,
        error_messages={'blank': 'About field cannot be blank.'}
    )
    
    animal_types = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    other_animals = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    
    service_types = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    def validate_animal_types(self, value):
        """Validate that animal types exist."""
        if value:
            valid_types = [choice[0] for choice in AnimalType.ANIMAL_CHOICES]
            for animal_type in value:
                if animal_type not in valid_types:
                    raise serializers.ValidationError(f'Invalid animal type: {animal_type}')
        return value
    
    def validate_service_types(self, value):
        """Validate that service types exist."""
        if value:
            valid_types = [choice[0] for choice in ServiceType.SERVICE_CHOICES]
            for service_type in value:
                if service_type not in valid_types:
                    raise serializers.ValidationError(f'Invalid service type: {service_type}')
        return value
    
    def validate(self, attrs):
        """Validate other_animals if 'other' is selected."""
        animal_types = attrs.get('animal_types', [])
        if 'other' in animal_types:
            if not attrs.get('other_animals'):
                raise serializers.ValidationError({
                    'other_animals': 'Please specify other animals when "Outros" is selected.'
                })
        return attrs
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update petsitter information."""
        user = instance.user
        
        # Update user fields
        if 'full_name' in validated_data:
            user.full_name = validated_data['full_name']
        
        if 'phone' in validated_data:
            user.phone = validated_data['phone']
        
        user.save()
        
        # Update petsitter fields
        if 'location' in validated_data:
            instance.location = validated_data['location']
        
        if 'about' in validated_data:
            instance.about = validated_data['about']
        
        if 'other_animals' in validated_data:
            instance.other_animals = validated_data['other_animals']
        
        instance.save()
        
        # Update animal types if provided
        if 'animal_types' in validated_data:
            instance.animal_types.clear()
            for animal_type in validated_data['animal_types']:
                animal_obj, _ = AnimalType.objects.get_or_create(animal_type=animal_type)
                instance.animal_types.add(animal_obj)
        
        # Update service types if provided
        if 'service_types' in validated_data:
            instance.service_types.clear()
            for service_type in validated_data['service_types']:
                service_obj, _ = ServiceType.objects.get_or_create(service_type=service_type)
                instance.service_types.add(service_obj)
        
        return instance
    
    def to_representation(self, instance):
        """Return updated petsitter data."""
        return PetSitterSerializer(instance).data
