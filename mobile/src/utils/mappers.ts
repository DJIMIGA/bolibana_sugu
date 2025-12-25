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
  let imageUrl: string | undefined;
  if (backendProduct.feature_image) {
    if (typeof backendProduct.feature_image === 'string') {
      imageUrl = ensureAbsoluteUrl(backendProduct.feature_image);
    } else if (backendProduct.feature_image.image) {
      imageUrl = ensureAbsoluteUrl(backendProduct.feature_image.image);
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

  return {
    id: backendProduct.id,
    title: backendProduct.name || backendProduct.title, // Backend retourne "name"
    slug: backendProduct.slug,
    description: backendProduct.description || undefined,
    price: parseFloat(backendProduct.price) || 0,
    discount_price: backendProduct.discount_price
      ? parseFloat(backendProduct.discount_price)
      : undefined,
    category: typeof backendProduct.category === 'object' && backendProduct.category
      ? backendProduct.category.id
      : backendProduct.category,
    supplier: backendProduct.supplier || undefined,
    brand: typeof backendProduct.brand === 'object' && backendProduct.brand
      ? (backendProduct.brand.name || backendProduct.brand)
      : backendProduct.brand || undefined,
    is_available: backendProduct.is_available !== false,
    is_salam: backendProduct.is_salam || false,
    stock: backendProduct.stock || 0,
    image: imageUrl,
    image_urls: Object.keys(imageUrls).length > 0 ? imageUrls : undefined,
    sku: backendProduct.sku || undefined,
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
    image: ensureAbsoluteUrl(backendCategory.image),
    description: backendCategory.description || undefined,
    color: backendCategory.color || '#10B981', // Couleur par défaut
    is_main: backendCategory.is_main !== undefined
      ? backendCategory.is_main
      : !backendCategory.parent, // Si pas de parent, c'est une catégorie principale
    order: backendCategory.order || 0,
    category_type: backendCategory.category_type || undefined,
    product_count: backendCategory.product_count || undefined,
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
  // Le backend peut retourner soit cart_items soit items
  const items = backendCart.cart_items || backendCart.items || [];
  
  return {
    id: backendCart.id,
    user: typeof backendCart.user === 'object'
      ? backendCart.user.id
      : backendCart.user || undefined,
    items: items.map((item: any) => ({
      id: item.id,
      product: mapProductFromBackend(item.product),
      quantity: item.quantity || 1,
      colors: Array.isArray(item.colors) 
        ? item.colors.map((c: any) => typeof c === 'object' ? c.id : c)
        : item.colors || [],
      sizes: Array.isArray(item.sizes)
        ? item.sizes.map((s: any) => typeof s === 'object' ? s.id : s)
        : item.sizes || [],
      variant: item.variant ? (typeof item.variant === 'object' ? item.variant.id : item.variant) : undefined,
    })),
    total_price: parseFloat(backendCart.total_price || backendCart.get_total_price?.() || 0),
    created_at: backendCart.created_at || new Date().toISOString(),
    updated_at: backendCart.updated_at || new Date().toISOString(),
  };
};




