from django.urls import path
from . import views

app_name = 'accounts_api'

urlpatterns = [
    # JWT endpoints personnalisés
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Les autres endpoints JWT (refresh, verify) sont définis dans saga/urls.py
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('addresses/', views.AddressListView.as_view(), name='address_list'),
    path('addresses/create/', views.AddressCreateView.as_view(), name='address_create'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address_detail'),
    path('addresses/<int:pk>/update/', views.AddressUpdateView.as_view(), name='address_update'),
    path('addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('addresses/<int:pk>/set-default/', views.SetDefaultAddressView.as_view(), name='set_default_address'),
    path('loyalty/', views.LoyaltyInfoView.as_view(), name='loyalty_info'),
    path('orders/', views.OrdersListView.as_view(), name='orders_list'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    # 2FA
    path('2fa/verify/', views.TwoFactorVerifyView.as_view(), name='2fa_verify'),
    path('2fa/setup/', views.TwoFactorSetupView.as_view(), name='2fa_setup'),
    path('2fa/disable/', views.TwoFactorDisableView.as_view(), name='2fa_disable'),
    # Password reset
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
] 