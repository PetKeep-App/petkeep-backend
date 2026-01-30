from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    CurrentUserView,
    CustomerSignupView,
    CustomerListView,
    CustomerDetailView,
    CustomerUpdateView,
    CustomerDeleteView,
    ChangePasswordView,
    PetSitterSignupView,
    PetSitterListView,
    PetSitterDetailView,
    PetSitterUpdateView,
    PetSitterDeleteView
)

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    
    # Customer endpoints
    path('customers/signup/', CustomerSignupView.as_view(), name='customer-signup'),
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/<int:user_id>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<int:user_id>/update/', CustomerUpdateView.as_view(), name='customer-update'),
    path('customers/<int:user_id>/delete/', CustomerDeleteView.as_view(), name='customer-delete'),
    path('customers/change-password/', ChangePasswordView.as_view(), name='customer-change-password'),
    
    # PetSitter endpoints
    path('petsitters/signup/', PetSitterSignupView.as_view(), name='petsitter-signup'),
    path('petsitters/', PetSitterListView.as_view(), name='petsitter-list'),
    path('petsitters/<int:user_id>/', PetSitterDetailView.as_view(), name='petsitter-detail'),
    path('petsitters/<int:user_id>/update/', PetSitterUpdateView.as_view(), name='petsitter-update'),
    path('petsitters/<int:user_id>/delete/', PetSitterDeleteView.as_view(), name='petsitter-delete'),
]
