from rest_framework import serializers
from product.models import Product, Category, ImageProduct, Phone
import logging

logger = logging.getLogger(__name__)



class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    slug = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'children',
            'image', 'description', 'color', 'is_main', 'order',
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
    phone = serializers.SerializerMethodField()
    clothing_product = serializers.SerializerMethodField()
    fabric_product = serializers.SerializerMethodField()
    cultural_product = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'discount_price',
            'category', 'brand', 'feature_image',
            'is_available', 'is_trending', 'is_salam', 'stock',
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