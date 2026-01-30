from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Base user model for authentication - serves as base for Customer and PetSitter."""
    
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('petsitter', 'PetSitter'),
    ]
    
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    # Permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.user_type})"


class Customer(models.Model):
    """Customer profile model."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='customer_profile'
    )
    
    # Customer specific fields can be added here in the future
    # For example: address, preferred_payment_method, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Customer: {self.user.full_name}"
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def full_name(self):
        return self.user.full_name
    
    @property
    def phone(self):
        return self.user.phone
    
    @property
    def is_active(self):
        return self.user.is_active


class PetSitter(models.Model):
    """PetSitter profile model - to be implemented in the future."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='petsitter_profile'
    )
    
    # PetSitter specific fields will be added here
    # For example: bio, hourly_rate, available_services, certifications, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'petsitters'
        verbose_name = 'PetSitter'
        verbose_name_plural = 'PetSitters'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PetSitter: {self.user.full_name}"
