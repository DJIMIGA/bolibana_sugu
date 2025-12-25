from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from .serializers import CartSerializer, CartItemSerializer
from cart.models import Cart, CartItem
from product.models import Product, Phone


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]  # Permettre aux utilisateurs anonymes d'accéder au panier

    def get_queryset(self):
        """Retourne le panier de l'utilisateur connecté ou anonyme"""
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user).prefetch_related(
                'cart_items__product',
                'cart_items__variant',
                'cart_items__colors',
                'cart_items__sizes'
            )
        else:
            # Pour les utilisateurs anonymes, utiliser la session
            if not self.request.session.session_key:
                self.request.session.create()
                self.request.session.save()
            session_key = self.request.session.session_key
            return Cart.objects.filter(session_key=session_key).prefetch_related(
                'cart_items__product',
                'cart_items__variant',
                'cart_items__colors',
                'cart_items__sizes'
            )

    def get_object(self):
        """Récupère ou crée le panier de l'utilisateur"""
        queryset = self.get_queryset()
        cart = queryset.first()
        
        if not cart:
            # Créer un nouveau panier
            if self.request.user.is_authenticated:
                cart = Cart.objects.create(user=self.request.user)
            else:
                if not self.request.session.session_key:
                    self.request.session.create()
                    self.request.session.save()
                cart = Cart.objects.create(session_key=self.request.session.session_key)
        
        return cart

    def list(self, request, *args, **kwargs):
        """Récupère le panier de l'utilisateur"""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Récupère le panier (même comportement que list)"""
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Ajoute un article au panier"""
        cart = self.get_object()
        
        product_id = request.data.get('product')
        variant_id = request.data.get('variant')
        quantity = int(request.data.get('quantity', 1))
        colors = request.data.get('colors', [])
        sizes = request.data.get('sizes', [])

        if not product_id:
            return Response(
                {'error': 'Le produit est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Produit introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérifier le stock si ce n'est pas un produit Salam
        if not product.is_salam and product.stock < quantity:
            return Response(
                {'error': f'Stock insuffisant. Disponible: {product.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si une variante est spécifiée
        variant = None
        if variant_id:
            try:
                variant = Phone.objects.get(id=variant_id, product=product)
                if variant.stock < quantity:
                    return Response(
                        {'error': f'Stock insuffisant pour cette variante. Disponible: {variant.stock}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Phone.DoesNotExist:
                return Response(
                    {'error': 'Variante introuvable'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Chercher un item existant avec les mêmes caractéristiques
        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).first()

        if cart_item:
            # Mettre à jour la quantité
            new_quantity = cart_item.quantity + quantity
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            # Créer un nouvel item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity
            )
            if colors:
                cart_item.colors.set(colors)
            if sizes:
                cart_item.sizes.set(sizes)

        # Retourner le panier mis à jour
        # Re-chercher le panier pour s'assurer que les items sont à jour
        cart = self.get_queryset().filter(id=cart.id).first()
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Supprime le panier ou un item selon le contexte"""
        try:
            # Si un pk est fourni, c'est pour supprimer un item
            if 'pk' in kwargs and kwargs['pk']:
                item_id = kwargs['pk']
                cart = self.get_object()
                try:
                    cart_item = CartItem.objects.get(id=item_id, cart=cart)
                    cart_item.delete()
                    
                    # Re-chercher le panier pour s'assurer que les items sont à jour
                    cart = self.get_queryset().filter(id=cart.id).first()
                    serializer = self.get_serializer(cart)
                    return Response(serializer.data)
                except CartItem.DoesNotExist:
                    return Response(
                        {'error': 'Article introuvable'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Sinon, vider le panier
                return self.clear(request)
        except Exception as e:
            print(f"ERROR in CartViewSet.destroy: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Met à jour un article du panier"""
        try:
            # Si un pk est fourni, c'est pour mettre à jour un item
            if 'pk' in kwargs and kwargs['pk']:
                item_id = kwargs['pk']
                cart = self.get_object()
                try:
                    cart_item = CartItem.objects.get(id=item_id, cart=cart)
                except CartItem.DoesNotExist:
                    return Response(
                        {'error': 'Article introuvable'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                quantity = request.data.get('quantity')
                if quantity is not None:
                    quantity = int(quantity)
                    if quantity <= 0:
                        cart_item.delete()
                    else:
                        # Vérifier le stock
                        product = cart_item.product
                        variant = cart_item.variant
                        
                        if variant:
                            if variant.stock < quantity:
                                return Response(
                                    {'error': f'Stock insuffisant. Disponible: {variant.stock}'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        elif not product.is_salam and product.stock < quantity:
                            return Response(
                                {'error': f'Stock insuffisant. Disponible: {product.stock}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        
                        cart_item.quantity = quantity
                        cart_item.save()

                # Re-chercher le panier pour s'assurer que les items sont à jour
                cart = self.get_queryset().filter(id=cart.id).first()
                serializer = self.get_serializer(cart)
                return Response(serializer.data)
            else:
                # Sinon, mettre à jour le panier lui-même (non implémenté pour l'instant)
                return Response(
                    {'error': 'Mise à jour du panier non supportée'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"ERROR in CartViewSet.update: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        """Met à jour partiellement un article du panier"""
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        """Vide le panier (supprime tous les items)"""
        print(f"DEBUG: Clear cart called for user {request.user}")
        try:
            cart = self.get_object()
            if not cart:
                return Response({'items': [], 'total_price': 0})
                
            cart.cart_items.all().delete()
            
            # Retourner un objet panier vide propre
            return Response({
                'id': cart.id,
                'items': [],
                'total_price': 0,
                'items_count': 0
            })
        except Exception as e:
            print(f"ERROR in CartViewSet.clear: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 