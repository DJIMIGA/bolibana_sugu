from django.urls import path
from . import views

app_name = 'accounts_api'

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('addresses/', views.AddressListView.as_view(), name='address_list'),
    path('addresses/create/', views.AddressCreateView.as_view(), name='address_create'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address_detail'),
    path('addresses/<int:pk>/update/', views.AddressUpdateView.as_view(), name='address_update'),
    path('addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('addresses/<int:pk>/set-default/', views.SetDefaultAddressView.as_view(), name='set_default_address'),
] 