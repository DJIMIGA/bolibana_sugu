// Mappers pour adapter les données du backend Django aux types TypeScript

import { User, Product, Category, Cart, ShippingAddress } from '../types';
import { MEDIA_BASE_URL } from '../services/api';

/**
 * Assure qu'une URL d'image est absolue
 */
const ensureAbsoluteUrl = (url: string | undefined): string | undefined => {
  if (!url) return undefined;
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url;
  }
  // Si l'URL commence par /, on enlève le slash pour éviter les doubles //
  const cleanUrl = url.startsWith('/') ? url.substring(1) : url;
  return `${MEDIA_BASE_URL}/${cleanUrl}`;
};

/**
 * Mappe les données utilisateur du backend vers le type mobile
 */
export const mapUserFromBackend = (backendUser: any): User => {
  return {
    id: backendUser.id,
    email: backendUser.email,
    phone: backendUser.phone || undefined,
    full_name: backendUser.first_name && backendUser.last_name
      ? `${backendUser.first_name} ${backendUser.last_name}`
      : backendUser.first_name || backendUser.last_name || undefined,
    fidelys_number: backendUser.fidelys_number || undefined,
    date_of_birth: backendUser.date_of_birth || undefined,
    is_staff: backendUser.is_staff || false,
    is_superuser: backendUser.is_superuser || false,
    created_at: backendUser.created_at || new Date().toISOString(),
    updated_at: backendUser.updated_at || new Date().toISOString(),
  };
};

/**
 * Mappe les données produit du backend vers le type mobile
 */
export const mapProductFromBackend = (backendProduct: any): Product => {
  // Vérification de sécurité
  if (!backendProduct || !backendProduct.id) {
    console.error('mapProductFromBackend: produit invalide', backendProduct);
    throw new Error('Produit invalide');
  }

  // Extraire l'image principale
  // L'API B2B utilise 'image_url', l'API normale utilise 'feature_image' ou 'image'
  let imageUrl: string | undefined;
  if (backendProduct.image_url) {
    // API B2B utilise image_url directement
    imageUrl = ensureAbsoluteUrl(backendProduct.image_url);
  } else if (backendProduct.feature_image) {
    if (typeof backendProduct.feature_image === 'string') {
      imageUrl = ensureAbsoluteUrl(backendProduct.feature_image);
    } else if (typeof backendProduct.feature_image === 'object') {
      // feature_image peut être {image: url} ou un objet avec d'autres propriétés
      imageUrl = ensureAbsoluteUrl(
        backendProduct.feature_image.image || 
        backendProduct.feature_image.url ||
        (typeof backendProduct.feature_image === 'object' && backendProduct.feature_image !== null 
          ? Object.values(backendProduct.feature_image)[0] as string 
          : undefined)
      );
    }
  } else if (backendProduct.image) {
    imageUrl = ensureAbsoluteUrl(backendProduct.image);
  } else if (backendProduct.images && backendProduct.images.length > 0) {
    const firstImage = backendProduct.images[0];
    imageUrl = ensureAbsoluteUrl(typeof firstImage === 'string' ? firstImage : firstImage.image);
  }

  // Extraire les URLs d'images pour la galerie
  const imageUrls: { main?: string; gallery?: string[] } = {};
  if (imageUrl) {
    imageUrls.main = imageUrl;
  }
  if (backendProduct.images && Array.isArray(backendProduct.images)) {
    imageUrls.gallery = backendProduct.images
      .map((img: any) => ensureAbsoluteUrl(typeof img === 'string' ? img : img.image))
      .filter(Boolean) as string[];
  }

  // Construire les specifications en incluant les données de téléphone si disponibles
  let specifications = backendProduct.specifications || {};
  
  // Détecter le type de produit (comme sur le web : phone, clothing_product, fabric_product, cultural_product)
  let productType: 'phone' | 'clothing' | 'fabric' | 'cultural' | undefined;
  
  if (backendProduct.phone) {
    productType = 'phone';
    specifications = {
      ...specifications,
      // Données de téléphone (avec vérifications de sécurité)
      brand: backendProduct.phone?.brand || undefined,
      model: backendProduct.phone?.model || undefined,
      color: backendProduct.phone?.color_name || backendProduct.phone?.color || undefined,
      color_name: backendProduct.phone?.color_name || undefined,
      color_code: backendProduct.phone?.color_code || undefined,
      storage: backendProduct.phone?.storage || undefined,
      ram: backendProduct.phone?.ram || undefined,
      screen_size: backendProduct.phone?.screen_size ? String(backendProduct.phone.screen_size) : undefined,
      resolution: backendProduct.phone?.resolution || undefined,
      operating_system: backendProduct.phone?.operating_system || undefined,
      processor: backendProduct.phone?.processor || undefined,
      battery_capacity: backendProduct.phone?.battery_capacity || undefined,
      camera_main: backendProduct.phone?.camera_main || undefined,
      camera_front: backendProduct.phone?.camera_front || undefined,
      network: backendProduct.phone?.network || undefined,
      is_new: backendProduct.phone?.is_new || undefined,
      box_included: backendProduct.phone?.box_included || undefined,
      accessories: backendProduct.phone?.accessories || undefined,
    };
  } else if (backendProduct.clothing_product) {
    productType = 'clothing';
  } else if (backendProduct.fabric_product) {
    productType = 'fabric';
  } else if (backendProduct.cultural_product) {
    productType = 'cultural';
  }
  
  // Ajouter le type de produit dans les specifications pour faciliter le filtrage
  if (productType) {
    specifications.product_type = productType;
  }

  // Gérer le prix : l'API B2B utilise 'selling_price', l'API normale utilise 'price'
  const priceValue = backendProduct.selling_price || backendProduct.price;
  const price = priceValue ? parseFloat(priceValue) : 0;
  
  // Gérer la disponibilité : l'API B2B utilise 'is_available_b2c', l'API normale utilise 'is_available'
  const isAvailable = backendProduct.is_available_b2c !== undefined 
    ? backendProduct.is_available_b2c 
    : (backendProduct.is_available !== false);
  
  // Gérer le stock : l'API B2B utilise 'quantity', l'API normale utilise 'stock'
  const stockValue = backendProduct.quantity !== undefined 
    ? backendProduct.quantity 
    : backendProduct.stock;
  const stock = stockValue ? parseFloat(stockValue) : 0;

  return {
    id: backendProduct.id,
    title: backendProduct.name || backendProduct.title, // Backend retourne "name"
    slug: backendProduct.slug,
    description: backendProduct.description || undefined,
    price: price,
    discount_price: backendProduct.discount_price
      ? parseFloat(backendProduct.discount_price)
      : undefined,
    category: typeof backendProduct.category === 'object' && backendProduct.category
      ? (backendProduct.category.id || backendProduct.category)
      : backendProduct.category,
    supplier: backendProduct.supplier || undefined,
    brand: typeof backendProduct.brand === 'object' && backendProduct.brand
      ? (backendProduct.brand.name || backendProduct.brand)
      : backendProduct.brand || undefined,
    is_available: isAvailable,
    is_salam: backendProduct.is_salam || false,
    stock: stock,
    image: imageUrl,
    image_urls: Object.keys(imageUrls).length > 0 ? imageUrls : undefined,
    sku: backendProduct.cug || backendProduct.sku || undefined,
    specifications: Object.keys(specifications).length > 0 ? specifications : undefined,
    weight: backendProduct.weight ? parseFloat(backendProduct.weight) : undefined,
    dimensions: backendProduct.dimensions || undefined,
    condition: backendProduct.condition || 'new',
    has_warranty: backendProduct.has_warranty || false,
    is_trending: backendProduct.is_trending || false,
    sales_count: backendProduct.sales_count || 0,
    average_rating: backendProduct.average_rating
      ? parseFloat(backendProduct.average_rating)
      : undefined,
    review_count: backendProduct.review_count || 0,
    created_at: backendProduct.created_at || new Date().toISOString(),
    updated_at: backendProduct.updated_at || new Date().toISOString(),
  };
};

/**
 * Mappe les données catégorie du backend vers le type mobile
 */
export const mapCategoryFromBackend = (backendCategory: any): Category => {
  // Gérer le parent correctement (peut être null, un objet, ou un nombre)
  let parentId: number | undefined;
  if (backendCategory.parent === null || backendCategory.parent === undefined) {
    parentId = undefined;
  } else if (typeof backendCategory.parent === 'object' && backendCategory.parent !== null) {
    parentId = backendCategory.parent.id;
  } else {
    parentId = backendCategory.parent;
  }

  return {
    id: backendCategory.id,
    name: backendCategory.name,
    slug: backendCategory.slug,
    parent: parentId,
    // Certaines API renvoient `image_url` au lieu de `image`
    image: ensureAbsoluteUrl(backendCategory.image || backendCategory.image_url),
    description: backendCategory.description || undefined,
    color: backendCategory.color || '#10B981', // Couleur par défaut
    is_main: backendCategory.is_main !== undefined
      ? backendCategory.is_main
      : !backendCategory.parent, // Si pas de parent, c'est une catégorie principale
    order: backendCategory.order || 0,
    category_type: backendCategory.category_type || undefined,
    product_count: backendCategory.product_count || undefined,
    // Gérer rayon_type : peut être null, string, ou undefined
    rayon_type: backendCategory.rayon_type !== null && backendCategory.rayon_type !== undefined
      ? backendCategory.rayon_type
      : undefined,
    // Gérer level : peut être null, number, ou undefined
    level: backendCategory.level !== null && backendCategory.level !== undefined
      ? backendCategory.level
      : undefined,
  };
};

/**
 * Mappe les données adresse du backend vers le type mobile
 */
export const mapAddressFromBackend = (backendAddress: any): ShippingAddress => {
  return {
    id: backendAddress.id,
    user: typeof backendAddress.user === 'object'
      ? backendAddress.user.id
      : backendAddress.user,
    full_name: backendAddress.full_name || undefined,
    address_type: backendAddress.address_type || 'DOM',
    quarter: backendAddress.quarter,
    street_address: backendAddress.street_address,
    city: backendAddress.city,
    additional_info: backendAddress.additional_info || undefined,
    is_default: backendAddress.is_default || false,
  };
};

/**
 * Mappe les données panier du backend vers le type mobile
 */
export const mapCartFromBackend = (backendCart: any): Cart => {
  // Vérification de sécurité : si backendCart est null ou undefined
  if (!backendCart) {
    return {
      id: 0,
      items: [],
      total_price: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }

  // Le backend peut retourner soit cart_items soit items
  const items = backendCart.cart_items || backendCart.items || [];
  
  // Calculer le total si non fourni
  let totalPrice = parseFloat(backendCart.total_price || backendCart.get_total_price?.() || 0);
  
  // Si le total est 0, le calculer depuis les items
  if (totalPrice === 0 && items.length > 0) {
    totalPrice = items.reduce((sum: number, item: any) => {
      // Vérifier que l'item et le produit existent
      if (!item || !item.product) return sum;
      
      const unitPrice = item.unit_price || 
                       (item.variant && (item.variant.discount_price || item.variant.price)) ||
                       (item.product && (item.product.discount_price || item.product.price)) ||
                       0;
      return sum + (unitPrice * (item.quantity || 1));
    }, 0);
  }
  
  // Filtrer et mapper les items valides uniquement
  const validItems = items
    .filter((item: any) => {
      // Vérifier que l'item a un id et un produit valide
      if (!item || !item.id) {
        return false;
      }
      if (!item.product) {
        return false;
      }
      return true;
    })
    .map((item: any) => {
      try {
        // Mapper le produit avec vérification de sécurité
        if (!item.product || !item.product.id) {
          console.error('mapCartFromBackend: produit invalide', item.product);
          throw new Error('Produit invalide dans le panier');
        }
        
        const product = mapProductFromBackend(item.product);
        
        // Si une variante existe, mettre à jour le produit avec les infos de la variante
        if (item.variant) {
          const variant = item.variant;
          // Mettre à jour le prix avec celui de la variante
          if (variant.discount_price || variant.price) {
            product.discount_price = variant.discount_price ? parseFloat(variant.discount_price) : undefined;
            product.price = parseFloat(variant.price);
          }
          // Mettre à jour le stock avec celui de la variante
          if (variant.stock !== undefined) {
            product.stock = variant.stock;
          }
          // Ajouter les spécifications de la variante
          if (variant.color_name || variant.color) {
            product.specifications = {
              ...product.specifications,
              color: variant.color_name || variant.color,
              color_name: variant.color_name,
              color_code: variant.color_code,
              storage: variant.storage,
              ram: variant.ram,
            };
          }
        }
        
        return {
          id: item.id,
          product,
          quantity: item.quantity || 1,
          colors: Array.isArray(item.colors) 
            ? item.colors.map((c: any) => typeof c === 'object' && c ? c.id : c).filter((id: any) => id !== null && id !== undefined)
            : item.colors || [],
          sizes: Array.isArray(item.sizes)
            ? item.sizes.map((s: any) => typeof s === 'object' && s ? s.id : s).filter((id: any) => id !== null && id !== undefined)
            : item.sizes || [],
          variant: item.variant ? (typeof item.variant === 'object' && item.variant ? item.variant.id : item.variant) : undefined,
        };
      } catch (error) {
        console.error('mapCartFromBackend: erreur lors du mapping d\'un item', error, item);
        return null;
      }
    })
    .filter((item: any) => item !== null); // Filtrer les items qui ont échoué
  
  return {
    id: backendCart.id || 0,
    user: typeof backendCart.user === 'object' && backendCart.user
      ? backendCart.user.id
      : backendCart.user || undefined,
    items: validItems,
    total_price: totalPrice,
    created_at: backendCart.created_at || new Date().toISOString(),
    updated_at: backendCart.updated_at || new Date().toISOString(),
  };
};




