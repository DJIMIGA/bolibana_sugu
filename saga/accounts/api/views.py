from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core import signing
from django.utils import timezone
from ..models import Shopper, ShippingAddress, LoyaltyHistory
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
        user = getattr(serializer, 'user', None)

        # Si 2FA activée, ne pas envoyer les tokens tout de suite
        if user and user.has_2fa_enabled():
            # Générer un token temporaire signé (valide 5 min)
            temp_token = signing.dumps(
                {'user_id': user.id},
                salt='2fa-login'
            )
            return Response({
                'requires_2fa': True,
                'temp_token': temp_token,
            }, status=status.HTTP_200_OK)

        data = serializer.validated_data
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
        
        loyalty_tiers = [
            {"name": "Bronze", "min_points": 0, "color": "#CD7F32"},
            {"name": "Argent", "min_points": 20, "color": "#C0C0C0"},
            {"name": "Or", "min_points": 50, "color": "#FFD700"},
            {"name": "Diamant", "min_points": 100, "color": "#B9F2FF"},
        ]

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
        current_tier_index = 0
        for idx, tier in enumerate(loyalty_tiers):
            if loyalty_points >= tier["min_points"]:
                current_tier_index = idx
        current_tier = loyalty_tiers[current_tier_index]
        loyalty_level = current_tier["name"]
        loyalty_level_color = current_tier["color"]

        next_tier = loyalty_tiers[current_tier_index + 1] if current_tier_index + 1 < len(loyalty_tiers) else None
        next_level = next_tier["name"] if next_tier else None
        next_min_points = next_tier["min_points"] if next_tier else None
        points_needed = (next_min_points - loyalty_points) if next_min_points is not None else 0

        # Progression vers le prochain palier
        if next_min_points is not None:
            current_min_points = current_tier["min_points"]
            range_points = max(1, next_min_points - current_min_points)
            progress_to_next_tier = (loyalty_points - current_min_points) / range_points
            progress_to_next_tier = max(0, min(1, progress_to_next_tier))
        else:
            progress_to_next_tier = 1

        # Messages dynamiques
        messages = []
        if total_orders == 0:
            messages.append("Passez votre première commande pour commencer à gagner des points.")
        if next_level:
            messages.append(f"Plus que {points_needed} points pour atteindre le niveau {next_level}.")
        else:
            messages.append("Vous êtes au niveau le plus élevé. Merci pour votre fidélité !")

        # Payload QR signé pour éviter d'exposer un identifiant brut
        qr_payload = signing.dumps(
            {
                "uid": request.user.id,
                "fid": request.user.fidelys_number,
                "ts": timezone.now().isoformat(),
            },
            salt="loyalty-qr",
        )

        # Historiser uniquement si le statut a changé
        last_history = LoyaltyHistory.objects.filter(user=request.user).first()
        if (
            not last_history
            or last_history.loyalty_points != loyalty_points
            or last_history.loyalty_level != loyalty_level
            or last_history.total_spent != total_spent
            or last_history.total_orders != total_orders
        ):
            LoyaltyHistory.objects.create(
                user=request.user,
                loyalty_points=loyalty_points,
                loyalty_level=loyalty_level,
                total_spent=total_spent,
                total_orders=total_orders,
                metadata={"source": "api"},
            )

        history_items = [
            {
                "loyalty_points": item.loyalty_points,
                "loyalty_level": item.loyalty_level,
                "total_spent": item.total_spent,
                "total_orders": item.total_orders,
                "created_at": item.created_at.isoformat(),
            }
            for item in LoyaltyHistory.objects.filter(user=request.user)[:10]
        ]
        
        return Response({
            'fidelys_number': request.user.fidelys_number,
            'total_orders': total_orders,
            'loyalty_points': loyalty_points,
            'loyalty_level': loyalty_level,
            'loyalty_level_color': loyalty_level_color,
            'total_spent': total_spent,
            'next_level': next_level,
            'points_needed': points_needed,
            'next_tier_name': next_level,
            'progress_to_next_tier': progress_to_next_tier,
            'loyalty_tiers': loyalty_tiers,
            'points_expires_at': None,
            'messages': messages,
            'qr_payload': qr_payload,
            'history': history_items,
        }, status=status.HTTP_200_OK)


class OrdersListView(generics.ListAPIView):
    """
    Liste des commandes de l'utilisateur connecté (pour le mobile).
    Retourne toutes les commandes sans pagination.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = None  # Désactiver la pagination pour retourner toutes les commandes

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
        
        # Annoter avec l'ordre de priorité des statuts
        queryset = queryset.annotate(status_order=status_priority)
        
        # Sélectionner les relations pour optimiser les requêtes
        queryset = queryset.select_related('shipping_address')
        queryset = queryset.prefetch_related('items__product')
        
        # Trier par statut puis par date
        queryset = queryset.order_by('status_order', '-created_at')
        
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


class LogoutView(APIView):
    """Déconnexion : blackliste le refresh token pour l'invalider."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response(
                {'error': 'Le champ "refresh" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            # Token déjà expiré ou invalide — on considère le logout réussi
            pass
        return Response(
            {'message': 'Déconnexion réussie.'},
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


# ========== 2FA API ==========

class TwoFactorVerifyView(APIView):
    """Vérifie le code TOTP après login et retourne les JWT tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        temp_token = request.data.get('temp_token')
        code = request.data.get('code')
        if not temp_token or not code:
            return Response(
                {'error': 'Les champs "temp_token" et "code" sont requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Décoder le token temporaire (5 min max)
        try:
            data = signing.loads(temp_token, salt='2fa-login', max_age=300)
        except signing.BadSignature:
            return Response(
                {'error': 'Token temporaire invalide ou expiré.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = get_object_or_404(Shopper, id=data['user_id'])

        if not user.verify_2fa_code(code):
            return Response(
                {'error': 'Code 2FA invalide.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Code valide — émettre les JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class TwoFactorSetupView(APIView):
    """Setup 2FA : retourne le secret TOTP et le QR code en base64."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retourne le statut 2FA et le QR code si un device non confirmé existe."""
        from django_otp.plugins.otp_totp.models import TOTPDevice
        user = request.user

        confirmed_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if confirmed_device:
            return Response({
                'is_enabled': True,
                'message': 'La 2FA est déjà activée.',
            })

        # Créer ou récupérer un device non confirmé
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
        if not device:
            device = TOTPDevice.objects.create(user=user, name='default', confirmed=False)

        # Générer le QR code en base64
        import qrcode, base64
        from io import BytesIO
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(device.config_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_b64 = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            'is_enabled': False,
            'qr_code': f'data:image/png;base64,{qr_b64}',
            'secret': device.key,
        })

    def post(self, request):
        """Confirme l'activation 2FA avec un code TOTP."""
        from django_otp.plugins.otp_totp.models import TOTPDevice
        code = request.data.get('code')
        if not code:
            return Response(
                {'error': 'Le champ "code" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
        if not device:
            return Response(
                {'error': 'Aucun appareil 2FA en attente de confirmation.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if device.verify_token(code):
            device.confirmed = True
            device.save()
            return Response({'message': '2FA activée avec succès.', 'is_enabled': True})
        else:
            return Response(
                {'error': 'Code invalide.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class TwoFactorDisableView(APIView):
    """Désactive la 2FA après vérification du code TOTP."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from django_otp.plugins.otp_totp.models import TOTPDevice
        code = request.data.get('code')
        if not code:
            return Response(
                {'error': 'Le champ "code" est requis pour désactiver la 2FA.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
        if not device:
            return Response(
                {'error': 'La 2FA n\'est pas activée.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if device.verify_token(code):
            device.delete()
            return Response({'message': '2FA désactivée avec succès.', 'is_enabled': False})
        else:
            return Response(
                {'error': 'Code invalide.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


# ========== PASSWORD RESET API ==========

class PasswordResetRequestView(APIView):
    """Envoie un email de reset mot de passe."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.contrib.auth.forms import PasswordResetForm
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Le champ "email" est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Toujours retourner 200 pour ne pas révéler si l'email existe
        form = PasswordResetForm(data={'email': email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='password_reset_email.html',
                subject_template_name='password_reset_subject.txt',
            )
        return Response(
            {'message': 'Si un compte existe avec cet email, un lien de réinitialisation a été envoyé.'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """Confirme le reset de mot de passe avec uid, token et nouveau mot de passe."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode

        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uid or not token or not new_password:
            return Response(
                {'error': 'Les champs "uid", "token" et "new_password" sont requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'Lien de réinitialisation invalide.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Le lien de réinitialisation a expiré ou est invalide.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 8:
            return Response(
                {'error': 'Le mot de passe doit contenir au moins 8 caractères.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {'message': 'Votre mot de passe a été réinitialisé avec succès.'},
            status=status.HTTP_200_OK
        )
