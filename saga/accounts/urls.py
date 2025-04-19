from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
app_name = 'accounts'
urlpatterns = [
    path('signup', views.signup, name="signup"),
    path('login', views.LoginView.as_view(), name="login"),
    path('logout', views.logout_user, name="logout"),
    path('profile', views.profile, name="profile"),
    path('update_profile', views.update_profile, name="update_profile"),
    path("addresses/", views.manage_addresses, name="manage_addresses"),
    path("addresses/set-default/<int:address_id>/", views.set_default_address, name="set_default_address"),
    path("addresses/delete/<int:address_id>/", views.delete_address, name="delete_address"),
    path("addresses/edit/<int:address_id>/", views.edit_address, name="edit_address"),
    path('edit_password', views.edit_password, name="edit_password"),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
