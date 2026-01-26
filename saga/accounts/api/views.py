from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from ..models import Shopper, ShippingAddress
from .serializers import UserSerializer, AddressSerializer, OrderSerializer
from cart.models import Order, Cart, CartItem

User = get_user_model()

# Serializer personnalisé pour utiliser email au lieu de username
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ajouter des claims personnalisés si nécessaire
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # Récupérer email depuis les attrs
        email = attrs.get('email')
        if not email:
            from rest_framework import serializers
            raise serializers.ValidationError('Email est requis')
        
        # Remplacer 'username' par 'email' pour la validation
        attrs['username'] = email
        return super().validate(attrs)

# Vue personnalisée pour obtenir le token avec email
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def _merge_anonymous_cart(self, request, user):
        try:
            session_key = request.session.session_key
            if not session_key:
                return
            anon_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if not anon_cart or not anon_cart.cart_items.exists():
                return

            user_cart, _ = Cart.objects.get_or_create(user=user)

            for item in anon_cart.cart_items.all():
                existing = CartItem.objects.filter(
                    cart=user_cart,
                    product=item.product,
                    variant=item.variant
                ).first()

                if existing:
                    existing.quantity = existing.quantity + item.quantity
                    existing.save()
                    if item.colors.exists():
                        existing.colors.add(*item.colors.all())
                    if item.sizes.exists():
                        existing.sizes.add(*item.sizes.all())
                    item.delete()
                else:
                    item.cart = user_cart
                    item.save()

            anon_cart.delete()
        except Exception:
            # Ne pas bloquer l'auth si la fusion échoue
            return

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = getattr(serializer, 'user', None)
        if user:
            self._merge_anonymous_cart(request, user)
        return Response(data, status=status.HTTP_200_OK)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        # Vérifier le mot de passe si fourni
        password = request.data.get('password')
        if password:
            from django.contrib.auth import authenticate
            user = authenticate(email=request.user.email, password=password)
            if not user:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'password': ['Mot de passe invalide']})
        
        # Retirer le mot de passe des données avant la mise à jour
        data = request.data.copy()
        data.pop('password', None)
        
        return super().update(request, *args, **kwargs)

class ProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class AddressListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

class AddressUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

class AddressDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Logique de suppression alignée avec la vue web `delete_address` :
        - Empêche la suppression si l'adresse est utilisée par des commandes
        - Empêche la suppression si c'est l'adresse par défaut et qu'il n'y a pas d'autre adresse
        """
        address = self.get_object()

        # Vérifier si l'adresse est utilisée par des commandes
        from cart.models import Order
        orders_using_address = Order.objects.filter(shipping_address=address)

        if orders_using_address.exists():
            orders_count = orders_using_address.count()
            return Response(
                {
                    "error": (
                        f"Impossible de supprimer cette adresse : "
                        f"elle est utilisée par {orders_count} commande(s). "
                        "Pour des raisons de sécurité, les adresses liées à des commandes "
                        "ne peuvent pas être supprimées."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifier si c'est l'adresse par défaut et s'il existe d'autres adresses
        if address.is_default:
            other_addresses = ShippingAddress.objects.filter(user=request.user).exclude(
                id=address.id
            )
            if not other_addresses.exists():
                return Response(
                    {
                        "error": (
                            "Impossible de supprimer cette adresse : "
                            "c'est votre seule adresse. Vous devez avoir au moins "
                            "une adresse de livraison."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Si tout est ok, on supprime
        return super().destroy(request, *args, **kwargs)

class SetDefaultAddressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
        ShippingAddress.objects.filter(user=request.user).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    """Vue pour l'inscription d'un nouvel utilisateur"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from rest_framework import serializers
        from django.contrib.auth import get_user_model
        from django.db import transaction
        
        User = get_user_model()
        
        # Validation des données
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        phone = request.data.get('phone')
        date_of_birth = request.data.get('date_of_birth')
        
        # Validations
        if not email:
            return Response(
                {'error': 'L\'email est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not password:
            return Response(
                {'error': 'Le mot de passe est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 8:
            return Response(
                {'error': 'Le mot de passe doit contenir au moins 8 caractères'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not first_name or not last_name:
            return Response(
                {'error': 'Le prénom et le nom sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si l'email existe déjà
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Cet email est déjà utilisé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Créer l'utilisateur
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone if phone else None,
                    date_of_birth=date_of_birth if date_of_birth else None,
                )
                
                # Sérialiser l'utilisateur créé
                serializer = UserSerializer(user)
                
                return Response(
                    {
                        'message': 'Inscription réussie',
                        'user': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la création du compte: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

class LoyaltyInfoView(APIView):
    """Vue pour récupérer les informations de fidélité de l'utilisateur"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from cart.models import Order
        from django.db.models import Sum
        
        # Compter les commandes de l'utilisateur
        total_orders = Order.objects.filter(
            user=request.user,
            status__in=['delivered', 'shipped', 'confirmed']
        ).count()
        
        # Calculer le total dépensé (commandes livrées uniquement)
        total_spent_result = Order.objects.filter(
            user=request.user,
            status='delivered'
        ).aggregate(
            total=Sum('total')
        )
        total_spent = float(total_spent_result['total'] or 0)
        
        # Calculer les points de fidélité (1 point par 1000 FCFA dépensés)
        loyalty_points = int(total_spent / 1000) if total_spent > 0 else 0
        
        # Déterminer le niveau de fidélité
        if loyalty_points >= 100:
            loyalty_level = "Diamant"
            loyalty_level_color = "#B9F2FF"  # Bleu clair pour diamant
        elif loyalty_points >= 50:
            loyalty_level = "Or"
            loyalty_level_color = "#FFD700"  # Or
        elif loyalty_points >= 20:
            loyalty_level = "Argent"
            loyalty_level_color = "#C0C0C0"  # Argent
        else:
            loyalty_level = "Bronze"
            loyalty_level_color = "#CD7F32"  # Bronze
        
        # Points nécessaires pour le niveau suivant
        if loyalty_level == "Bronze":
            next_level = "Argent"
            points_needed = 20 - loyalty_points
        elif loyalty_level == "Argent":
            next_level = "Or"
            points_needed = 50 - loyalty_points
        elif loyalty_level == "Or":
            next_level = "Diamant"
            points_needed = 100 - loyalty_points
        else:
            next_level = None
            points_needed = 0
        
        return Response({
            'fidelys_number': request.user.fidelys_number,
            'total_orders': total_orders,
            'loyalty_points': loyalty_points,
            'loyalty_level': loyalty_level,
            'loyalty_level_color': loyalty_level_color,
            'total_spent': total_spent,
            'next_level': next_level,
            'points_needed': points_needed,
        }, status=status.HTTP_200_OK)


class OrdersListView(generics.ListAPIView):
    """
    Liste des commandes de l'utilisateur connecté (pour le mobile).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        """
        Retourne les commandes triées par statut (actives en premier) puis par date de création.
        Ordre de priorité des statuts (alignés avec B2B):
        1. draft, confirmed, shipped (commandes actives)
        2. delivered (livrées)
        3. cancelled (annulées)
        """
        from django.db.models import Case, When, IntegerField
        
        # Définir l'ordre de priorité des statuts (alignés avec B2B)
        status_priority = Case(
            When(status=Order.DRAFT, then=1),
            When(status=Order.CONFIRMED, then=2),
            When(status=Order.SHIPPED, then=3),
            When(status=Order.DELIVERED, then=4),
            When(status=Order.CANCELLED, then=5),
            default=6,
            output_field=IntegerField()
        )
        
        # Récupérer toutes les commandes de l'utilisateur
        queryset = Order.objects.filter(user=self.request.user)
        
        # Debug: vérifier le nombre total de commandes
        total_orders = queryset.count()
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[OrdersListView] Utilisateur {self.request.user.id} - Total commandes: {total_orders}")
        
        # Annoter avec l'ordre de priorité des statuts
        queryset = queryset.annotate(status_order=status_priority)
        
        # Sélectionner les relations pour optimiser les requêtes
        queryset = queryset.select_related('shipping_address')
        queryset = queryset.prefetch_related('items__product')
        
        # Trier par statut puis par date
        queryset = queryset.order_by('status_order', '-created_at')
        
        # Debug: vérifier les commandes retournées
        orders_list = list(queryset[:10])  # Limiter pour les logs
        logger.info(f"[OrdersListView] Commandes retournées: {len(orders_list)}")
        for order in orders_list[:5]:  # Limiter à 5 pour les logs
            logger.info(f"[OrdersListView] Commande {order.id}: statut={order.status}, created_at={order.created_at}")
        
        return queryset


class ChangePasswordView(APIView):
    """Vue pour changer le mot de passe de l'utilisateur"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from rest_framework.exceptions import ValidationError
        from ..utils.validators import validate_password
        from django.contrib.auth import update_session_auth_hash

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_new_password = request.data.get('confirm_new_password')

        # Validations
        if not current_password:
            raise ValidationError({'current_password': ['Le mot de passe actuel est requis']})

        if not new_password:
            raise ValidationError({'new_password': ['Le nouveau mot de passe est requis']})

        if not confirm_new_password:
            raise ValidationError({'confirm_new_password': ['La confirmation du mot de passe est requise']})

        # Vérifier le mot de passe actuel
        if not request.user.check_password(current_password):
            raise ValidationError({'current_password': ['Mot de passe actuel invalide']})

        # Vérifier que les nouveaux mots de passe correspondent
        if new_password != confirm_new_password:
            raise ValidationError({'confirm_new_password': ['Les nouveaux mots de passe ne correspondent pas']})

        # Valider la sécurité du nouveau mot de passe
        try:
            validate_password(new_password)
        except Exception as e:
            raise ValidationError({'new_password': [str(e)]})

        # Changer le mot de passe
        request.user.set_password(new_password)
        request.user.save()

        # Mettre à jour la session pour éviter la déconnexion
        update_session_auth_hash(request, request.user)

        return Response(
            {'message': 'Votre mot de passe a été mis à jour avec succès !'},
            status=status.HTTP_200_OK
        )


class DeleteAccountView(APIView):
    """Vue pour supprimer le compte de l'utilisateur"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from django.contrib.auth import logout
        from django.contrib.sessions.models import Session

        user = request.user

        # Vérifier si l'utilisateur a des commandes en cours
        from cart.models import Order
        active_orders = Order.objects.filter(
            user=user,
            status__in=['draft', 'confirmed', 'shipped']
        ).exists()

        if active_orders:
            return Response(
                {
                    'error': (
                        'Impossible de supprimer votre compte : '
                        'vous avez des commandes en cours. '
                        'Veuillez attendre la livraison de vos commandes.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Supprimer toutes les sessions de l'utilisateur
        Session.objects.filter(session_key__in=[
            s.session_key for s in Session.objects.all()
            if s.get_decoded().get('_auth_user_id') == str(user.id)
        ]).delete()

        # Supprimer l'utilisateur
        user.delete()

        # Déconnecter l'utilisateur
        logout(request)

        return Response(
            {'message': 'Votre compte a été supprimé avec succès.'},
            status=status.HTTP_200_OK
        )
