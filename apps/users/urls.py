from django.urls import path
from .views import (
    CustomerSignupView,
    CustomerListView,
    CustomerDetailView,
    CustomerUpdateView,
    CustomerDeleteView,
    ChangePasswordView
)

app_name = 'users'

urlpatterns = [
    # Customer endpoints
    path('customers/signup/', CustomerSignupView.as_view(), name='customer-signup'),
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/<int:user_id>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<int:user_id>/update/', CustomerUpdateView.as_view(), name='customer-update'),
    path('customers/<int:user_id>/delete/', CustomerDeleteView.as_view(), name='customer-delete'),
    path('customers/change-password/', ChangePasswordView.as_view(), name='customer-change-password'),
    
    # PetSitter endpoints (to be implemented in the future)
    # path('petsitters/signup/', PetSitterSignupView.as_view(), name='petsitter-signup'),
    # path('petsitters/', PetSitterListView.as_view(), name='petsitter-list'),
    # path('petsitters/<int:user_id>/', PetSitterDetailView.as_view(), name='petsitter-detail'),
]
