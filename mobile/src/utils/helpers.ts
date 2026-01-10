// Fonctions utilitaires
import { MAX_RETRY_ATTEMPTS, RETRY_BACKOFF_BASE } from './constants';

export const formatPrice = (price: number): string => {
  return `${price.toLocaleString('fr-FR')} FCFA`;
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export const isExpired = (timestamp: number, ttl: number): boolean => {
  return Date.now() - timestamp > ttl;
};

export const sleep = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

export const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = MAX_RETRY_ATTEMPTS,
  baseDelay: number = RETRY_BACKOFF_BASE
): Promise<T> => {
  let lastError: Error;
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (i < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, i);
        await sleep(delay);
      }
    }
  }
  throw lastError!;
};

/**
 * Nettoie les données de log pour retirer le HTML et limiter la taille
 * @param data - Les données à nettoyer (peuvent être string, object, etc.)
 * @param maxLength - Longueur maximale du message (défaut: 200)
 * @returns Message nettoyé sans HTML
 */
export const cleanLogData = (data: any, maxLength: number = 200): string => {
  if (!data) return 'N/A';
  
  // Si c'est une string
  if (typeof data === 'string') {
    // Détecter si c'est du HTML
    const isHtml = data.includes('<!DOCTYPE') || 
                   data.includes('<html') || 
                   data.includes('<body') ||
                   data.length > 500;
    
    if (isHtml) {
      // Extraire un message simple depuis le HTML si possible
      const titleMatch = data.match(/<title[^>]*>([^<]+)<\/title>/i);
      if (titleMatch) {
        return titleMatch[1].trim().substring(0, maxLength);
      }
      
      const h1Match = data.match(/<h1[^>]*>([^<]+)<\/h1>/i);
      if (h1Match) {
        return h1Match[1].trim().substring(0, maxLength);
      }
      
      // Sinon, retourner un message générique
      return 'Réponse HTML (contenu non affiché)';
    }
    
    // Nettoyer les balises HTML restantes et limiter la taille
    const cleaned = data
      .replace(/<[^>]+>/g, '') // Retirer toutes les balises HTML
      .replace(/\s+/g, ' ') // Normaliser les espaces
      .trim();
    
    return cleaned.length > maxLength 
      ? cleaned.substring(0, maxLength) + '...' 
      : cleaned;
  }
  
  // Si c'est un objet
  if (typeof data === 'object') {
    // Vérifier si l'objet contient des propriétés avec du HTML
    const cleaned: any = {};
    for (const [key, value] of Object.entries(data)) {
      if (typeof value === 'string') {
        cleaned[key] = cleanLogData(value, maxLength);
      } else if (value !== null && value !== undefined) {
        cleaned[key] = value;
      }
    }
    
    // Convertir en string JSON avec limite de taille
    const jsonStr = JSON.stringify(cleaned);
    return jsonStr.length > maxLength 
      ? jsonStr.substring(0, maxLength) + '...' 
      : jsonStr;
  }
  
  // Pour les autres types, convertir en string
  const str = String(data);
  return str.length > maxLength 
    ? str.substring(0, maxLength) + '...' 
    : str;
};

/**
 * Nettoie les données d'erreur pour les logs (retire HTML, limite taille)
 * @param error - L'erreur à nettoyer
 * @returns Message d'erreur nettoyé
 */
export const cleanErrorForLog = (error: any): string => {
  if (!error) return 'Erreur inconnue';
  
  // Priorité 1: error.response?.data
  if (error.response?.data) {
    const cleaned = cleanLogData(error.response.data);
    if (cleaned !== 'N/A' && !cleaned.includes('Réponse HTML')) {
      return cleaned;
    }
  }
  
  // Priorité 2: error.message
  if (error.message) {
    return cleanLogData(error.message);
  }
  
  // Priorité 3: error.toString()
  return cleanLogData(error.toString());
};


