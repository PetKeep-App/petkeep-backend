from django.contrib import admin
from .models import User, Customer, PetSitter, AnimalType, ServiceType


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'full_name', 'user_type', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['email', 'full_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['get_id', 'get_email', 'get_full_name', 'get_phone', 'get_is_active', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__full_name', 'user__phone']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_id(self, obj):
        return obj.user.id
    get_id.short_description = 'ID'
    get_id.admin_order_field = 'user__id'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__full_name'
    
    def get_phone(self, obj):
        return obj.user.phone
    get_phone.short_description = 'Phone'
    get_phone.admin_order_field = 'user__phone'
    
    def get_is_active(self, obj):
        return obj.user.is_active
    get_is_active.short_description = 'Active'
    get_is_active.boolean = True
    get_is_active.admin_order_field = 'user__is_active'


@admin.register(PetSitter)
class PetSitterAdmin(admin.ModelAdmin):
    list_display = ['get_id', 'get_email', 'get_full_name', 'get_phone', 'location', 'get_is_active', 'created_at']
    list_filter = ['created_at', 'animal_types', 'service_types']
    search_fields = ['user__email', 'user__full_name', 'user__phone', 'location']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['animal_types', 'service_types']
    ordering = ['-created_at']
    
    def get_id(self, obj):
        return obj.user.id
    get_id.short_description = 'ID'
    get_id.admin_order_field = 'user__id'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__full_name'
    
    def get_phone(self, obj):
        return obj.user.phone
    get_phone.short_description = 'Phone'
    get_phone.admin_order_field = 'user__phone'
    
    def get_is_active(self, obj):
        return obj.user.is_active
    get_is_active.short_description = 'Active'
    get_is_active.boolean = True
    get_is_active.admin_order_field = 'user__is_active'


@admin.register(AnimalType)
class AnimalTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'animal_type', 'get_animal_type_display']
    search_fields = ['animal_type']
    ordering = ['animal_type']


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'service_type', 'get_service_type_display']
    search_fields = ['service_type']
    ordering = ['service_type']
