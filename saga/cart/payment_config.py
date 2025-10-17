# Configuration centralisée des méthodes de paiement
# Les méthodes de livraison sont gérées par le modèle Product.shipping_methods

# =============================================================================
# CONFIGURATION DES MÉTHODES DE PAIEMENT
# =============================================================================

# Configuration des méthodes de paiement
PAYMENT_METHODS_CONFIG = {
    'mobile_money': {
        'enabled': True,  # Activé avec l'intégration Orange Money
        'display_name': 'Orange Money',
        'description': 'Paiement rapide via Orange Money, MTN Mobile Money, etc.',
        'icon': 'mobile_money',
        'color': 'orange',
        'available_for': ['salam', 'classic', 'mixed'],  # Types de produits supportés
        'requires_immediate_payment': True,
        'disabled_message': {
            'title': 'Orange Money Temporairement Indisponible',
            'message': 'Le service Orange Money est temporairement indisponible. Veuillez utiliser une autre méthode de paiement.',
            'icon': '⚠️'
        }
    },
    'online_payment': {
        'enabled': True,  # Carte bancaire disponible
        'display_name': 'Carte bancaire',
        'description': 'Paiement sécurisé via carte bancaire (Visa, Mastercard, etc.)',
        'icon': 'credit_card',
        'color': 'green',
        'available_for': ['salam', 'classic', 'mixed'],
        'requires_immediate_payment': True,
        'disabled_message': {
            'title': 'Paiement en ligne indisponible',
            'message': 'Le paiement en ligne est temporairement indisponible.',
            'icon': '❌'
        }
    },
    'cash_on_delivery': {
        'enabled': True,  # Paiement à la livraison disponible
        'display_name': 'Paiement à la livraison',
        'description': 'Paiement en espèces à la réception de votre commande',
        'icon': 'cash',
        'color': 'yellow',
        'available_for': ['classic', 'mixed', 'salam'],  # Disponible pour tous les types de produits
        'requires_immediate_payment': False,
        'disabled_message': {
            'title': 'Paiement à la livraison indisponible',
            'message': 'Le paiement à la livraison n\'est pas disponible pour ce type de produit.',
            'icon': '❌'
        }
    }
}

# =============================================================================
# FONCTIONS UTILITAIRES - MÉTHODES DE PAIEMENT
# =============================================================================

def get_available_payment_methods(product_type=None):
    """
    Retourne la liste des méthodes de paiement disponibles
    Args:
        product_type: Type de produit ('salam', 'classic', 'mixed', None pour tous)
    """
    methods = []
    
    for method_key, config in PAYMENT_METHODS_CONFIG.items():
        if config['enabled']:
            if product_type is None or product_type in config['available_for']:
                methods.append(method_key)
    
    return methods

def get_payment_method_config(method):
    """
    Retourne la configuration complète d'une méthode de paiement
    """
    return PAYMENT_METHODS_CONFIG.get(method, {})

def get_payment_method_display_name(method):
    """
    Retourne le nom d'affichage d'une méthode de paiement
    """
    config = get_payment_method_config(method)
    return config.get('display_name', method)

def get_payment_method_description(method):
    """
    Retourne la description d'une méthode de paiement
    """
    config = get_payment_method_config(method)
    return config.get('description', '')

def is_payment_method_available(method, product_type=None):
    """
    Vérifie si une méthode de paiement est disponible
    Args:
        method: Clé de la méthode de paiement
        product_type: Type de produit ('salam', 'classic', 'mixed', None pour tous)
    """
    config = get_payment_method_config(method)
    if not config or not config.get('enabled'):
        return False
    
    if product_type and product_type not in config.get('available_for', []):
        return False
    
    return True

def get_disabled_payment_method_message(method):
    """
    Retourne le message d'erreur pour une méthode de paiement désactivée
    """
    config = get_payment_method_config(method)
    return config.get('disabled_message', {
        'title': 'Méthode de paiement indisponible',
        'message': f'La méthode de paiement {method} n\'est pas disponible actuellement.',
        'icon': '❌'
    })

def requires_immediate_payment(method):
    """
    Vérifie si une méthode de paiement nécessite un paiement immédiat
    """
    config = get_payment_method_config(method)
    return config.get('requires_immediate_payment', False)

# =============================================================================
# FONCTIONS DE VALIDATION
# =============================================================================

def validate_payment_method_for_product(method, product_type):
    """
    Valide qu'une méthode de paiement est appropriée pour un type de produit
    """
    if not is_payment_method_available(method, product_type):
        return False, f"Méthode de paiement '{method}' non disponible pour les produits {product_type}"
    
    return True, "Méthode de paiement valide"

# =============================================================================
# FONCTIONS DE COMPATIBILITÉ (pour la rétrocompatibilité)
# =============================================================================

# Variables de compatibilité pour l'ancien code
MOBILE_MONEY_ENABLED = PAYMENT_METHODS_CONFIG['mobile_money']['enabled']
ONLINE_PAYMENT_ENABLED = PAYMENT_METHODS_CONFIG['online_payment']['enabled']
CASH_ON_DELIVERY_ENABLED = PAYMENT_METHODS_CONFIG['cash_on_delivery']['enabled']

# Messages d'information pour les méthodes désactivées (compatibilité)
DISABLED_METHOD_MESSAGES = {
    method: config['disabled_message'] 
    for method, config in PAYMENT_METHODS_CONFIG.items()
}

# =============================================================================
# FONCTIONS UTILITAIRES POUR LES MÉTHODES DE LIVRAISON
# =============================================================================

def get_available_shipping_methods_for_cart(cart):
    """
    Récupère les méthodes de livraison disponibles pour un panier
    en fonction des produits qu'il contient
    """
    from product.models import ShippingMethod
    
    # Récupérer tous les produits du panier
    cart_products = [item.product for item in cart.cart_items.all()]
    
    if not cart_products:
        return ShippingMethod.objects.none()
    
    # Récupérer toutes les méthodes de livraison des produits du panier
    shipping_methods = set()
    for product in cart_products:
        if product.shipping_methods.exists():
            shipping_methods.update(product.shipping_methods.all())
    
    return list(shipping_methods)

def get_common_shipping_methods_for_cart(cart_or_items):
    """
    Récupère les méthodes de livraison communes à tous les produits du panier
    Accepte soit un objet Cart, soit un QuerySet de cart_items
    """
    from product.models import ShippingMethod
    
    # Si c'est un objet Cart, récupérer les cart_items
    if hasattr(cart_or_items, 'cart_items'):
        cart_items = cart_or_items.cart_items.all()
    else:
        # Sinon, c'est déjà un QuerySet de cart_items
        cart_items = cart_or_items
    
    cart_products = [item.product for item in cart_items]
    
    if not cart_products:
        return ShippingMethod.objects.none()
    
    # Commencer avec les méthodes du premier produit
    common_methods = set(cart_products[0].shipping_methods.all())
    
    # Intersection avec les méthodes des autres produits
    for product in cart_products[1:]:
        product_methods = set(product.shipping_methods.all())
        common_methods = common_methods.intersection(product_methods)
    
    return list(common_methods)

def calculate_shipping_cost_for_cart(cart, shipping_method):
    """
    Calcule le coût de livraison pour un panier avec une méthode donnée
    """
    cart_products = [item.product for item in cart.cart_items.all()]
    
    if not cart_products:
        return 0
    
    # Vérifier que la méthode est disponible pour tous les produits
    for product in cart_products:
        if shipping_method not in product.shipping_methods.all():
            return None  # Méthode non disponible pour ce produit
    
    # Retourner le prix de la méthode de livraison
    return shipping_method.price

# =============================================================================
# NOUVELLES FONCTIONS - CALCUL PAR FOURNISSEUR
# =============================================================================

def get_cart_suppliers_breakdown(cart):
    """
    Analyse le panier et groupe les produits par fournisseur
    Retourne un dictionnaire avec les informations par fournisseur
    """
    suppliers_data = {}
    
    for item in cart.cart_items.all():
        product = item.product
        supplier = product.supplier
        
        # Créer une clé basée sur l'adresse du fournisseur pour masquer le nom
        if supplier and supplier.address:
            supplier_key = f"Zone d'expédition : {supplier.address}"
        elif supplier:
            supplier_key = f"Zone d'expédition : {supplier.company_name}"
        else:
            supplier_key = "Zone d'expédition : SagaKore"
        
        if supplier_key not in suppliers_data:
            suppliers_data[supplier_key] = {
                'supplier': supplier,
                'supplier_name': supplier_key,
                'products': [],
                'total_items': 0,
                'subtotal': 0,
                'shipping_methods': set(),
                'selected_shipping_method': None,
                'shipping_cost': 0,
                'delivery_time': None
            }
        
        # Utiliser le prix promotionnel si disponible, sinon le prix normal
        unit_price = product.discount_price if hasattr(product, 'discount_price') and product.discount_price else product.price
        
        # Ajouter le produit
        product_data = {
            'product': product,
            'quantity': item.quantity,
            'unit_price': unit_price,
            'total_price': unit_price * item.quantity,
            'is_salam': product.is_salam
        }
        
        suppliers_data[supplier_key]['products'].append(product_data)
        suppliers_data[supplier_key]['total_items'] += item.quantity
        suppliers_data[supplier_key]['subtotal'] += unit_price * item.quantity
        
        # Ajouter les méthodes de livraison du produit
        if product.shipping_methods.exists():
            suppliers_data[supplier_key]['shipping_methods'].update(product.shipping_methods.all())
    
    return suppliers_data

def calculate_shipping_by_supplier(cart, selected_shipping_methods=None):
    """
    Calcule les frais de livraison par fournisseur
    Args:
        cart: Panier à analyser
        selected_shipping_methods: Dict {supplier_name: shipping_method_id}
    """
    suppliers_data = get_cart_suppliers_breakdown(cart)
    
    if not suppliers_data:
        return {
            'total_shipping_cost': 0,
            'suppliers_breakdown': {},
            'summary': {
                'total_items': 0,
                'subtotal': 0,
                'shipping_cost': 0,
                'total': 0
            }
        }
    
    total_shipping_cost = 0
    total_items = 0
    subtotal = 0
    
    # Calculer les frais de livraison pour chaque fournisseur
    for supplier_name, data in suppliers_data.items():
        shipping_methods = list(data['shipping_methods'])
        
        if not shipping_methods:
            # Aucune méthode de livraison disponible
            data['shipping_cost'] = 0
            data['selected_shipping_method'] = None
            data['delivery_time'] = "Non disponible"
        else:
            # Si une méthode est sélectionnée, l'utiliser
            if selected_shipping_methods and supplier_name in selected_shipping_methods:
                selected_method_id = selected_shipping_methods[supplier_name]
                selected_method = next(
                    (m for m in shipping_methods if m.id == selected_method_id), 
                    None
                )
                if selected_method:
                    data['selected_shipping_method'] = selected_method
                    data['shipping_cost'] = selected_method.price
                    data['delivery_time'] = f"{selected_method.min_delivery_days}-{selected_method.max_delivery_days} jours"
                else:
                    # Méthode sélectionnée non trouvée, utiliser la plus chère
                    max_cost_method = max(shipping_methods, key=lambda m: m.price)
                    data['selected_shipping_method'] = max_cost_method
                    data['shipping_cost'] = max_cost_method.price
                    data['delivery_time'] = f"{max_cost_method.min_delivery_days}-{max_cost_method.max_delivery_days} jours"
            else:
                # Aucune méthode sélectionnée, utiliser la plus chère par défaut
                max_cost_method = max(shipping_methods, key=lambda m: m.price)
                data['selected_shipping_method'] = max_cost_method
                data['shipping_cost'] = max_cost_method.price
                data['delivery_time'] = f"{max_cost_method.min_delivery_days}-{max_cost_method.max_delivery_days} jours"
        
        total_shipping_cost += data['shipping_cost']
        total_items += data['total_items']
        subtotal += data['subtotal']
    
    # Créer le résumé
    summary = {
        'total_items': total_items,
        'subtotal': subtotal,
        'shipping_cost': total_shipping_cost,
        'total': subtotal + total_shipping_cost,
        'suppliers_count': len(suppliers_data)
    }
    
    return {
        'total_shipping_cost': total_shipping_cost,
        'suppliers_breakdown': suppliers_data,
        'summary': summary
    }

def get_optimal_shipping_methods(cart):
    """
    Suggère les meilleures méthodes de livraison pour chaque fournisseur
    basé sur le coût et la rapidité
    """
    suppliers_data = get_cart_suppliers_breakdown(cart)
    optimal_methods = {}
    
    for supplier_name, data in suppliers_data.items():
        shipping_methods = list(data['shipping_methods'])
        
        if not shipping_methods:
            optimal_methods[supplier_name] = None
            continue
        
        # Trier par coût croissant
        sorted_methods = sorted(shipping_methods, key=lambda m: m.price)
        
        # Recommandation : méthode la moins chère
        optimal_methods[supplier_name] = {
            'recommended': sorted_methods[0],
            'all_options': sorted_methods
        }
    
    return optimal_methods

def validate_shipping_methods_for_cart(cart, selected_shipping_methods):
    """
    Valide que les méthodes de livraison sélectionnées sont disponibles
    pour tous les produits de chaque fournisseur
    """
    suppliers_data = get_cart_suppliers_breakdown(cart)
    validation_results = {}
    
    for supplier_name, data in suppliers_data.items():
        if supplier_name not in selected_shipping_methods:
            validation_results[supplier_name] = {
                'valid': False,
                'message': f"Aucune méthode de livraison sélectionnée pour {supplier_name}"
            }
            continue
        
        selected_method_id = selected_shipping_methods[supplier_name]
        available_methods = list(data['shipping_methods'])
        
        # Vérifier si la méthode sélectionnée est disponible
        selected_method = next(
            (m for m in available_methods if m.id == selected_method_id), 
            None
        )
        
        if selected_method:
            validation_results[supplier_name] = {
                'valid': True,
                'message': f"Méthode valide pour {supplier_name}",
                'method': selected_method
            }
        else:
            validation_results[supplier_name] = {
                'valid': False,
                'message': f"Méthode de livraison non disponible pour {supplier_name}"
            }
    
    return validation_results

def get_shipping_summary_for_display(cart, selected_shipping_methods=None):
    """
    Prépare les données pour l'affichage dans le template
    """
    shipping_data = calculate_shipping_by_supplier(cart, selected_shipping_methods)
    
    # Formater les données pour l'affichage
    display_data = {
        'suppliers': [],
        'summary': shipping_data['summary']
    }
    
    for supplier_name, data in shipping_data['suppliers_breakdown'].items():
        supplier_display = {
            'name': supplier_name,
            'products_count': len(data['products']),
            'total_items': data['total_items'],
            'subtotal': data['subtotal'],
            'shipping_method': data['selected_shipping_method'],
            'shipping_cost': data['shipping_cost'],
            'delivery_time': data['delivery_time'],
            'products': []
        }
        
        # Formater les produits
        for product_data in data['products']:
            supplier_display['products'].append({
                'title': product_data['product'].title,
                'quantity': product_data['quantity'],
                'unit_price': product_data['unit_price'],
                'total_price': product_data['total_price'],
                'is_salam': product_data['is_salam']
            })
        
        display_data['suppliers'].append(supplier_display)
    
    return display_data 