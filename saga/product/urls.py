from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
                  path('', views.index, name='product_index'),
                  path('search/', views.search, name='search'),
                  path('product/<int:product_id>/', views.detail, name='product_detail'),
                  path('review/<int:product_id>/', views.review, name='review'),
                  path('quick_view/<int:product_id>/', views.quick_view, name='product_quick_view'),
                  path('category/', views.category, name='category'),
                  path('product_list/', views.product_list, name='product_list'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
