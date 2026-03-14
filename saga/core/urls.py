from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Pages Légales
    path('terms-conditions/', views.TermsConditionsView.as_view(), name='terms_conditions'),
    path('cgv/', views.CGVView.as_view(), name='cgv'),
    
    # Pages À propos
    path('about/', views.AboutView.as_view(), name='about'),
    path('about/story/', views.AboutStoryView.as_view(), name='about_story'),
    path('about/values/', views.AboutValuesView.as_view(), name='about_values'),
    
    # Pages Services
    path('services/loyalty/', views.ServiceLoyaltyView.as_view(), name='service_loyalty'),
    path('services/express/', views.ServiceExpressView.as_view(), name='service_express'),
    
    # Pages Assistance
    path('help/center/', views.HelpCenterView.as_view(), name='help_center'),
    path('help/returns/', views.HelpReturnsView.as_view(), name='help_returns'),
    path('help/warranty/', views.HelpWarrantyView.as_view(), name='help_warranty'),
    path('api/cookie-consent/', views.save_cookie_consent, name='save_cookie_consent'),
    

] 