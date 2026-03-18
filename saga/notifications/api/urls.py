from django.urls import path
from . import views

urlpatterns = [
    path('register-token/', views.RegisterPushTokenView.as_view(), name='register-push-token'),
    path('unregister-token/', views.UnregisterPushTokenView.as_view(), name='unregister-push-token'),
    path('preferences/', views.NotificationPreferencesView.as_view(), name='notification-preferences'),
]
