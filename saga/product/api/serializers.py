from rest_framework import serializers
from product.models import Product, Category, ImageProduct, Phone
import logging

logger = logging.getLogger(__name__)



class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    slug = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'children',
            'image', 'image_url', 'description', 'color', 'is_main', 'order',
            'category_type', 'product_count', 'rayon_type', 'level'
        ]
        extra_kwargs = {
            'slug': {'required': False, 'allow_null': True, 'allow_blank': True},
            'name': {'required': False},
            'description': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

    def get_parent(self, obj):
        """Retourne l'ID du parent au lieu de l'objet complet"""
        try:
            return obj.parent_id if obj.parent_id else None
        except (AttributeError, TypeError):
            return None
    
    def get_children(self, obj):
        # Sérialiser les enfants sans récursion profonde pour éviter les problèmes
        children = obj.children.all()
        if not children:
            return []
        
        # Sérialiser les enfants avec le même serializer mais sans récursion
        children_data = []
        for child in children:
            try:
                child_dict = {
                    'id': child.id,
                    'name': child.name or '',
                    'slug': child.slug or '',
                    'parent': child.parent_id if hasattr(child, 'parent_id') else None,
                    'image': self.get_image(child),
                    'image_url': self.get_image_url(child),
                    'description': child.description or '',
                    'color': child.color or 'blue',
                    'is_main': getattr(child, 'is_main', False),
                    'order': getattr(child, 'order', 0),
                    'category_type': getattr(child, 'category_type', 'MODEL') or 'MODEL',
                    # Priorité à l'annotation (utilisée par /api/inventory/categories/synced/)
                    'product_count': (
                        getattr(child, 'b2b_product_count', None)
                        if getattr(child, 'b2b_product_count', None) is not None
                        else getattr(child, 'product_count', 0) or 0
                    ),
                    'rayon_type': getattr(child, 'rayon_type', None),
                    'level': getattr(child, 'level', None),
                    'children': []  # Ne pas récurser pour éviter les problèmes
                }
                children_data.append(child_dict)
            except Exception as e:
                logger.warning(f"Erreur lors de la sérialisation de l'enfant {child.id}: {str(e)}")
                continue
        
        return children_data

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_image_url(self, obj):
        if getattr(obj, 'image_url', None):
            return obj.image_url
        return self.get_image(obj)

    def get_product_count(self, obj):
        """Retourne le nombre de produits disponibles dans cette catégorie"""
        # IMPORTANT:
        # - Category a déjà une property "product_count" (read-only), donc une annotation du même nom provoque un crash.
        # - L'endpoint inventory annote maintenant "b2b_product_count".
        if getattr(obj, 'b2b_product_count', None) is not None:
            return obj.b2b_product_count
        try:
            return obj.product_count
        except (AttributeError, TypeError):
            return 0

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ImageProduct
        fields = ['id', 'image', 'ordre', 'created_at', 'updated_at']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None



class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    feature_image = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    promo_price = serializers.SerializerMethodField()
    has_promotion = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    promotion_start_date = serializers.SerializerMethodField()
    promotion_end_date = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    clothing_product = serializers.SerializerMethodField()
    fabric_product = serializers.SerializerMethodField()
    cultural_product = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'discount_price',
            'category', 'brand', 'feature_image',
            'image_url', 'images', 'image_urls', 'gallery',
            'promo_price', 'has_promotion', 'discount_percent', 'promotion_start_date', 'promotion_end_date',
            'is_available', 'is_trending', 'is_salam', 'stock', 'specifications',
            'phone', 'clothing_product', 'fabric_product', 'cultural_product', 'created_at'
        ]

    def get_feature_image(self, obj):
        # Retourner l'image principale du produit ou la première image de la galerie
        if obj.image:
            request = self.context.get('request')
            if request:
                return {'image': request.build_absolute_uri(obj.image.url)}
            return {'image': obj.image.url}
        feature_image = obj.images.first()
        if feature_image:
            return ProductImageSerializer(feature_image, context=self.context).data
        return None

    def _abs(self, url: str):
        """Construit une URL absolue si possible"""
        if not url:
            return None
        request = self.context.get('request')
        if request and isinstance(url, str) and url.startswith('/'):
            return request.build_absolute_uri(url)
        return url

    def get_image_url(self, obj):
        """Compat B2B: image_url string (principale)"""
        try:
            url = obj.get_display_image_url() if hasattr(obj, 'get_display_image_url') else None
            return self._abs(url) if url else None
        except Exception:
            return None

    def get_images(self, obj):
        """Compat B2B: images[] (liste d'URLs)"""
        try:
            # Priorité B2B: si la synchro a stocké les URLs externes, on les renvoie directement
            if obj.specifications and isinstance(obj.specifications, dict):
                b2b_urls = obj.specifications.get('b2b_image_urls') or []
                if isinstance(b2b_urls, list) and len(b2b_urls) > 0:
                    return [u for u in b2b_urls if isinstance(u, str) and u]

            urls = []
            if hasattr(obj, 'get_all_image_urls'):
                all_urls = obj.get_all_image_urls() or {}
                main = all_urls.get('main')
                gallery = all_urls.get('gallery') or []
                if main:
                    urls.append(self._abs(main))
                for u in gallery:
                    if u and u not in urls:
                        urls.append(self._abs(u))
            return [u for u in urls if u]
        except Exception:
            return []

    def get_gallery(self, obj):
        """Alias de images[] pour compat 'gallery'"""
        return self.get_images(obj)

    def get_image_urls(self, obj):
        """Compat B2B: image_urls[] (liste d'URLs)"""
        return self.get_images(obj)

    def get_specifications(self, obj):
        """Expose uniquement les champs utiles pour le poids dans les listes/paniers."""
        try:
            if not obj.specifications or not isinstance(obj.specifications, dict):
                return {}
            specs = obj.specifications
            allowed_keys = {
                'sold_by_weight',
                'unit_type',
                'weight_unit',
                'price_per_kg',
                'discount_price_per_kg',
                'available_weight_kg',
            }
            return {key: specs.get(key) for key in allowed_keys if key in specs}
        except Exception:
            return {}

    def get_has_promotion(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                if obj.specifications.get('has_promotion') is True:
                    return True
            return bool(obj.discount_price and obj.discount_price > 0)
        except Exception:
            return False

    def get_promo_price(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                promo = obj.specifications.get('promo_price')
                if promo is not None:
                    return promo
            return obj.discount_price
        except Exception:
            return None

    def get_discount_percent(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                dp = obj.specifications.get('discount_percent')
                if dp is not None:
                    return dp
            promo = self.get_promo_price(obj)
            if promo and obj.price and obj.price > 0:
                return round(((obj.price - promo) / obj.price) * 100, 2)
            return None
        except Exception:
            return None

    def get_promotion_start_date(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                return obj.specifications.get('promotion_start_date')
        except Exception:
            pass
        return None

    def get_promotion_end_date(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                return obj.specifications.get('promotion_end_date')
        except Exception:
            pass
        return None
    
    def get_phone(self, obj):
        if hasattr(obj, 'phone') and obj.phone:
            return PhoneSerializer(obj.phone, context=self.context).data
        return None
    
    def get_clothing_product(self, obj):
        """Retourne True si le produit a un vêtement associé, None sinon (comme sur le web)"""
        try:
            if hasattr(obj, 'clothing_product'):
                clothing = obj.clothing_product
                if clothing is not None:
                    return True
        except Exception:
            pass
        return None
    
    def get_fabric_product(self, obj):
        """Retourne True si le produit a un tissu associé, None sinon (comme sur le web)"""
        try:
            if hasattr(obj, 'fabric_product'):
                fabric = obj.fabric_product
                if fabric is not None:
                    return True
        except Exception:
            pass
        return None
    
    def get_cultural_product(self, obj):
        """Retourne True si le produit a un article culturel associé, None sinon (comme sur le web)"""
        try:
            if hasattr(obj, 'cultural_product'):
                cultural = obj.cultural_product
                if cultural is not None:
                    return True
        except Exception:
            pass
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    feature_image = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    promo_price = serializers.SerializerMethodField()
    has_promotion = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    promotion_start_date = serializers.SerializerMethodField()
    promotion_end_date = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    clothing_product = serializers.SerializerMethodField()
    fabric_product = serializers.SerializerMethodField()
    cultural_product = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description',
            'price', 'discount_price', 'category', 'brand',
            'images', 'feature_image', 'stock', 'is_trending', 'is_salam',
            'is_available', 'created_at', 'updated_at',
            'image_url', 'image_urls', 'gallery',
            'promo_price', 'has_promotion', 'discount_percent', 'promotion_start_date', 'promotion_end_date',
            'specifications', 'weight', 'dimensions', 'phone',
            'clothing_product', 'fabric_product', 'cultural_product'
        ]
    
    def get_feature_image(self, obj):
        # Retourner l'image principale du produit ou la première image de la galerie
        if obj.image:
            request = self.context.get('request')
            if request:
                return {'image': request.build_absolute_uri(obj.image.url)}
            return {'image': obj.image.url}
        feature_image = obj.images.first()
        if feature_image:
            return ProductImageSerializer(feature_image, context=self.context).data
        return None

    def _abs(self, url: str):
        if not url:
            return None
        request = self.context.get('request')
        if request and isinstance(url, str) and url.startswith('/'):
            return request.build_absolute_uri(url)
        return url

    def get_image_url(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                b2b_urls = obj.specifications.get('b2b_image_urls') or []
                if isinstance(b2b_urls, list) and len(b2b_urls) > 0 and isinstance(b2b_urls[0], str):
                    return b2b_urls[0]
            url = obj.get_display_image_url() if hasattr(obj, 'get_display_image_url') else None
            return self._abs(url) if url else None
        except Exception:
            return None

    def get_image_urls(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                b2b_urls = obj.specifications.get('b2b_image_urls') or []
                if isinstance(b2b_urls, list) and len(b2b_urls) > 0:
                    first = b2b_urls[0] if isinstance(b2b_urls[0], str) else None
                    gallery = [u for u in b2b_urls if isinstance(u, str) and u]
                    return {'main': first, 'gallery': gallery}

            if hasattr(obj, 'get_all_image_urls'):
                all_urls = obj.get_all_image_urls() or {}
                main = all_urls.get('main')
                gallery = all_urls.get('gallery') or []
                return {
                    'main': self._abs(main) if main else None,
                    'gallery': [self._abs(u) for u in gallery if u],
                }
        except Exception:
            pass
        return {}

    def get_gallery(self, obj):
        try:
            return (self.get_image_urls(obj) or {}).get('gallery') or []
        except Exception:
            return []

    def get_has_promotion(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                if obj.specifications.get('has_promotion') is True:
                    return True
            return bool(obj.discount_price and obj.discount_price > 0)
        except Exception:
            return False

    def get_promo_price(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                promo = obj.specifications.get('promo_price')
                if promo is not None:
                    return promo
            return obj.discount_price
        except Exception:
            return None

    def get_discount_percent(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                dp = obj.specifications.get('discount_percent')
                if dp is not None:
                    return dp
            promo = self.get_promo_price(obj)
            if promo and obj.price and obj.price > 0:
                return round(((obj.price - promo) / obj.price) * 100, 2)
            return None
        except Exception:
            return None

    def get_promotion_start_date(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                return obj.specifications.get('promotion_start_date')
        except Exception:
            pass
        return None

    def get_promotion_end_date(self, obj):
        try:
            if obj.specifications and isinstance(obj.specifications, dict):
                return obj.specifications.get('promotion_end_date')
        except Exception:
            pass
        return None
    
    def get_phone(self, obj):
        if hasattr(obj, 'phone') and obj.phone:
            return PhoneSerializer(obj.phone, context=self.context).data
        return None
    
    def get_clothing_product(self, obj):
        """Retourne True si le produit a un vêtement associé, None sinon (comme sur le web)"""
        try:
            if hasattr(obj, 'clothing_product'):
                clothing = obj.clothing_product
                if clothing is not None:
                    return True
        except Exception:
            pass
        return None
    
    def get_fabric_product(self, obj):
        """Retourne True si le produit a un tissu associé, None sinon (comme sur le web)"""
        try:
            if hasattr(obj, 'fabric_product'):
                fabric = obj.fabric_product
                if fabric is not None:
                    return True
        except Exception:
            pass
        return None
    
    def get_cultural_product(self, obj):
        """Retourne True si le produit a un article culturel associé, None sinon (comme sur le web)"""
        try:
            if hasattr(obj, 'cultural_product'):
                cultural = obj.cultural_product
                if cultural is not None:
                    return True
        except Exception:
            pass
        return None

class PhoneSerializer(serializers.ModelSerializer):
    color_name = serializers.SerializerMethodField()
    color_code = serializers.SerializerMethodField()
    
    class Meta:
        model = Phone
        fields = [
            'id', 'brand', 'model', 'color', 'color_name', 'color_code',
            'storage', 'ram', 'screen_size', 'resolution', 'operating_system',
            'processor', 'battery_capacity', 'camera_main', 'camera_front',
            'network', 'is_new', 'box_included', 'accessories'
        ]
    
    def get_color_name(self, obj):
        if obj.color:
            return obj.color.name
        return None
    
    def get_color_code(self, obj):
        if obj.color:
            return obj.color.code
        return None 