from rest_framework import serializers
from core.models import StaticPage, SiteConfiguration


class StaticPageListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste des pages."""
    class Meta:
        model = StaticPage
        fields = ['slug', 'title', 'updated_at']


class StaticPageDetailSerializer(serializers.ModelSerializer):
    """Serializer complet avec le contenu de la page."""
    class Meta:
        model = StaticPage
        fields = ['slug', 'title', 'content', 'created_at', 'updated_at']


class SiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfiguration
        fields = [
            'site_name', 'phone_number', 'email', 'address',
            'whatsapp_number', 'facebook_url', 'instagram_url', 'twitter_url', 'tiktok_url',
            'company_name', 'company_address', 'rccm',
            'opening_hours', 'opening_hours_detailed',
            'delivery_info', 'return_policy',
            'logo_url', 'logo_small_url', 'favicon_url',
            'brand_primary_color', 'brand_secondary_color', 'brand_accent_color',
            'brand_tagline', 'brand_short_tagline',
            'meta_description', 'meta_keywords',
            'about_story_title', 'about_values_title',
            'service_loyalty_title', 'service_express_title',
            'help_center_title', 'help_returns_title', 'help_warranty_title',
        ]
