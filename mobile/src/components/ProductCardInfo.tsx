import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { Product } from '../types';
import { COLORS } from '../utils/constants';

interface ProductCardInfoProps {
  product: Product;
  showBrand?: boolean;
  showSpecs?: boolean;
  compact?: boolean;
}

const ProductCardInfo: React.FC<ProductCardInfoProps> = ({ 
  product, 
  showBrand = true, 
  showSpecs = false,
  compact = false 
}) => {
  // Fonction helper pour extraire et nettoyer une valeur de marque
  // Basée sur la logique du template tag get_brand_name du web
  const extractBrand = (value: any): string | null => {
    if (!value) return null;
    
    // Si c'est un objet/dict (comme {id: 10, name: 'nike'})
    if (typeof value === 'object' && !Array.isArray(value) && value !== null) {
      // Chercher la propriété name en priorité (comme dans get_brand_name)
      if (value.name) {
        const brandName = String(value.name).trim();
        if (brandName.length > 0) return brandName;
      }
      // Si pas de name, retourner la représentation string de l'objet (comme dans get_brand_name)
      return String(value);
    }
    
    // Si c'est une string
    if (typeof value === 'string') {
      const trimmed = value.trim();
      // Si la string ressemble à un dict (commence par {), essayer de parser
      if (trimmed.startsWith('{')) {
        try {
          const parsed = JSON.parse(trimmed);
          if (parsed && typeof parsed === 'object' && parsed.name) {
            return String(parsed.name).trim();
          }
        } catch {
          // Si le parsing JSON échoue, essayer d'extraire avec regex (comme dans get_brand_name)
          const match = trimmed.match(/'name':\s*['"]([^'"]+)['"]/);
          if (match && match[1]) {
            return match[1].trim();
          }
        }
      }
      return trimmed.length > 0 ? trimmed : null;
    }
    
    // Convertir en string si possible
    try {
      const str = String(value).trim();
      return str.length > 0 ? str : null;
    } catch {
      return null;
    }
  };

  // Extraire la marque depuis plusieurs sources possibles (dans l'ordre de priorité)
  const brand = 
    extractBrand(product.brand) ||
    extractBrand(product.specifications?.brand) ||
    extractBrand(product.specifications?.manufacturer) ||
    extractBrand(product.specifications?.brand_name) ||
    null;
  
  // Extraire le modèle (depuis specifications.model)
  const model = product.specifications?.model 
    ? (typeof product.specifications.model === 'string' 
        ? product.specifications.model.trim() 
        : String(product.specifications.model).trim())
    : null;
  
  // Extraire les spécifications pour les téléphones
  const phoneData = product.specifications || {};
  const isNew = phoneData.is_new !== undefined 
    ? phoneData.is_new 
    : product.condition === 'new';
  
  // Construire le texte de marque/modèle
  const brandText = brand 
    ? (model && model.length > 0 
        ? `${brand} ${model}` 
        : brand)
    : null;

  return (
    <View style={styles.container}>
      {/* Marque */}
      {showBrand && brandText && (
        <View style={[styles.brandContainer, compact && styles.brandContainerCompact]}>
          <MaterialIcons 
            name="business" 
            size={compact ? 10 : 12} 
            color={COLORS.PRIMARY} 
          />
          <Text style={[styles.brand, compact && styles.brandCompact]} numberOfLines={1}>
            {brandText}
          </Text>
        </View>
      )}

      {/* Spécifications techniques (pour téléphones uniquement) */}
      {showSpecs && (phoneData.storage || phoneData.ram || product.has_warranty || isNew !== undefined) && (
        <View style={[styles.specsContainer, compact && styles.specsContainerCompact]}>
          {/* État (Neuf/Occasion) */}
          {isNew !== undefined && (
            <View style={[styles.specBadge, isNew ? styles.specBadgeNew : styles.specBadgeUsed]}>
              <Text style={[styles.specBadgeText, isNew ? styles.specBadgeTextNew : styles.specBadgeTextUsed]}>
                {isNew ? 'Neuf' : 'Occasion'}
              </Text>
            </View>
          )}

          {/* Stockage */}
          {phoneData.storage && (
            <View style={[styles.specBadge, styles.specBadgePurple]}>
              <Text style={[styles.specBadgeText, styles.specBadgeTextPurple]}>
                {phoneData.storage} GB
              </Text>
            </View>
          )}

          {/* RAM */}
          {phoneData.ram && (
            <View style={[styles.specBadge, styles.specBadgeBlue]}>
              <Text style={[styles.specBadgeText, styles.specBadgeTextBlue]}>
                {phoneData.ram} GB RAM
              </Text>
            </View>
          )}

          {/* Garantie */}
          {product.has_warranty && (
            <View style={[styles.specBadge, styles.specBadgeYellow]}>
              <Text style={[styles.specBadgeText, styles.specBadgeTextYellow]}>
                Garantie
              </Text>
            </View>
          )}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 4,
  },
  brandContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  brandContainerCompact: {
    marginBottom: 4,
  },
  brand: {
    fontSize: 11,
    color: COLORS.PRIMARY,
    marginLeft: 4,
    fontWeight: '600',
  },
  brandCompact: {
    fontSize: 10,
  },
  specsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
    marginBottom: 8,
  },
  specsContainerCompact: {
    gap: 3,
    marginBottom: 4,
  },
  specBadge: {
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 8,
    borderWidth: 1,
  },
  specBadgeNew: {
    backgroundColor: '#D1FAE5',
    borderColor: '#A7F3D0',
  },
  specBadgeUsed: {
    backgroundColor: '#FED7AA',
    borderColor: '#FDBA74',
  },
  specBadgePurple: {
    backgroundColor: '#E9D5FF',
    borderColor: '#D8B4FE',
  },
  specBadgeBlue: {
    backgroundColor: '#DBEAFE',
    borderColor: '#BFDBFE',
  },
  specBadgeYellow: {
    backgroundColor: '#FEF3C7',
    borderColor: '#FDE68A',
  },
  specBadgeText: {
    fontSize: 9,
    fontWeight: '700',
  },
  specBadgeTextNew: {
    color: '#065F46',
  },
  specBadgeTextUsed: {
    color: '#9A3412',
  },
  specBadgeTextPurple: {
    color: '#6B21A8',
  },
  specBadgeTextBlue: {
    color: '#1E40AF',
  },
  specBadgeTextYellow: {
    color: '#92400E',
  },
});

export default ProductCardInfo;
