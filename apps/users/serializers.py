from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from .models import User, Customer


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
