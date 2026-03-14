import React from 'react';
import { Product, Category } from '../types';
import ProductCardDefault from './ProductCardDefault';
import ProductCardSalam from './ProductCardSalam';
import ProductCardPhone from './ProductCardPhone';
import { useAppSelector } from '../store/hooks';

interface DynamicProductCardProps {
  product: Product;
}

// Fonction helper pour trouver une catégorie et ses parents par ID
const findCategoryWithParents = (categoryId: number, categories: Category[]): Category | null => {
  const category = categories.find(cat => cat.id === categoryId);
  return category || null;
};

// Fonction helper pour vérifier si une catégorie ou ses parents correspondent à un slug
const isCategoryOrParent = (category: Category | null, targetSlugs: string[], categories: Category[]): boolean => {
  if (!category) return false;
  
  // Vérifier la catégorie elle-même
  if (targetSlugs.includes(category.slug)) {
    return true;
  }
  
  // Vérifier les parents récursivement
  if (category.parent) {
    const parentCategory = findCategoryWithParents(category.parent, categories);
    if (parentCategory && isCategoryOrParent(parentCategory, targetSlugs, categories)) {
      return true;
    }
  }
  
  return false;
};

const DynamicProductCard: React.FC<DynamicProductCardProps> = ({ product }) => {
  const categories = useAppSelector((state) => state.product.categories);
  
  // Vérifier d'abord si c'est un produit SALAM
  if (product.is_salam) {
    return <ProductCardSalam product={product} />;
  }

  // Trouver la catégorie du produit
  const productCategory = typeof product.category === 'number'
    ? findCategoryWithParents(product.category, categories)
    : null;

  // Déterminer le type de carte selon la catégorie (comme dans le web)
  if (productCategory) {
    // Téléphones
    if (isCategoryOrParent(productCategory, ['telephones'], categories)) {
      return <ProductCardPhone product={product} />;
    }

    // Vêtements
    if (isCategoryOrParent(productCategory, ['vetements'], categories)) {
      // TODO: Créer ProductCardClothing si nécessaire
      return <ProductCardDefault product={product} />;
    }

    // Tissus
    if (isCategoryOrParent(productCategory, ['tissus'], categories)) {
      // TODO: Créer ProductCardFabric si nécessaire
      return <ProductCardDefault product={product} />;
    }

    // Articles culturels
    if (isCategoryOrParent(productCategory, ['produits-culturels', 'culture', 'articles-culturels'], categories)) {
      // TODO: Créer ProductCardCultural si nécessaire
      return <ProductCardDefault product={product} />;
    }
  }

  // Par défaut, utiliser ProductCardDefault
  return <ProductCardDefault product={product} />;
};

export default DynamicProductCard;

