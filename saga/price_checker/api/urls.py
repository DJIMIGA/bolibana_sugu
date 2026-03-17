from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('cities', views.CityViewSet)
router.register('prices', views.PriceEntryViewSet)
router.register('submissions', views.PriceSubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
]
