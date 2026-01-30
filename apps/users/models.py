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


class AnimalType(models.Model):
    """Animal types that petsitters can care for."""
    
    ANIMAL_CHOICES = [
        ('dog', 'Cachorro'),
        ('cat', 'Gato'),
        ('bird', 'Pássaro'),
        ('rabbit', 'Coelho'),
        ('chicken', 'Galinha'),
        ('hamster', 'Hamster'),
        ('other', 'Outros'),
    ]
    
    animal_type = models.CharField(max_length=20, choices=ANIMAL_CHOICES, unique=True)
    
    class Meta:
        db_table = 'animal_types'
        verbose_name = 'Animal Type'
        verbose_name_plural = 'Animal Types'
    
    def __str__(self):
        return self.get_animal_type_display()


class ServiceType(models.Model):
    """Service types that petsitters can offer."""
    
    SERVICE_CHOICES = [
        ('keepsitter', 'KeepSitter'),
        ('keephost', 'KeepHost'),
        ('keepwalk', 'KeepWalk'),
    ]
    
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, unique=True)
    
    class Meta:
        db_table = 'service_types'
        verbose_name = 'Service Type'
        verbose_name_plural = 'Service Types'
    
    def __str__(self):
        return self.get_service_type_display()


class PetSitter(models.Model):
    """PetSitter profile model."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='petsitter_profile'
    )
    
    # PetSitter specific fields
    location = models.CharField(
        max_length=255, 
        blank=True,
        default='',
        help_text='Location/Address of the petsitter'
    )
    about = models.TextField(
        blank=True,
        default='',
        help_text='About the petsitter, their experience, etc.'
    )
    other_animals = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Other animals if "Outros" is selected'
    )
    
    # Many-to-many relationships
    animal_types = models.ManyToManyField(
        AnimalType,
        related_name='petsitters',
        help_text='Types of animals the petsitter can care for'
    )
    
    service_types = models.ManyToManyField(
        ServiceType,
        related_name='petsitters',
        help_text='Services offered by the petsitter'
    )
    
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
