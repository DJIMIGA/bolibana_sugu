import { AxiosError } from 'axios';
import { ApiError } from '../types';

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum ErrorType {
  NETWORK = 'network',
  AUTHENTICATION = 'authentication',
  VALIDATION = 'validation',
  SERVER = 'server',
  UNKNOWN = 'unknown',
}

interface ErrorLog {
  message: string;
  type: ErrorType;
  severity: ErrorSeverity;
  timestamp: number;
  details?: Record<string, any>;
}

class ErrorService {
  private logs: ErrorLog[] = [];

  classifyError(error: any): { type: ErrorType; severity: ErrorSeverity } {
    // Détecter les erreurs de mode hors ligne forcé
    if (error.isOfflineBlocked || error.code === 'OFFLINE_MODE_FORCED' || error.message === 'OFFLINE_MODE_FORCED') {
      // Ne pas traiter comme une erreur critique en mode hors ligne
      return { type: ErrorType.NETWORK, severity: ErrorSeverity.LOW };
    }

    if (error instanceof AxiosError) {
      if (!error.response) {
        // Erreur réseau
        return { type: ErrorType.NETWORK, severity: ErrorSeverity.MEDIUM };
      }

      const status = error.response.status;

      if (status === 401 || status === 403) {
        return { type: ErrorType.AUTHENTICATION, severity: ErrorSeverity.HIGH };
      }

      if (status >= 400 && status < 500) {
        return { type: ErrorType.VALIDATION, severity: ErrorSeverity.MEDIUM };
      }

      if (status >= 500) {
        return { type: ErrorType.SERVER, severity: ErrorSeverity.CRITICAL };
      }
    }

    return { type: ErrorType.UNKNOWN, severity: ErrorSeverity.MEDIUM };
  }

  getUserMessage(error: any): string {
    // Si l'erreur est déjà une chaîne, la renvoyer directement
    if (typeof error === 'string') return error;

    // Si c'est une erreur de mode hors ligne, retourner un message silencieux
    if (error.isOfflineBlocked || error.code === 'OFFLINE_MODE_FORCED' || error.message === 'OFFLINE_MODE_FORCED' || error.message === '') {
      return ''; // Message vide pour ne pas afficher d'erreur
    }

    const { type } = this.classifyError(error);

    if (error instanceof AxiosError) {
      if (error.response?.data) {
        const data = error.response.data;
        
        // Messages d'erreur du backend
        if (data.detail) {
          // Gestion spécifique des erreurs de connexion JWT
          const detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
          
          // Erreurs de mot de passe/email incorrect
          if (
            detail.toLowerCase().includes('no active account') ||
            detail.toLowerCase().includes('unable to log in') ||
            detail.toLowerCase().includes('invalid credentials') ||
            detail.toLowerCase().includes('incorrect') ||
            detail.toLowerCase().includes('invalid password') ||
            detail.toLowerCase().includes('mot de passe') ||
            detail.toLowerCase().includes('email')
          ) {
            return 'Email ou mot de passe incorrect. Veuillez vérifier vos identifiants.';
          }
          
          return detail;
        }
        if (data.message) return data.message;
        if (data.error) {
          const errorMsg = Array.isArray(data.error) ? data.error.join(', ') : data.error;
          return errorMsg;
        }
        
        // Erreurs de validation par champ
        if (data.password) {
          if (Array.isArray(data.password)) {
            return data.password.join(', ');
          }
          return data.password;
        }
        
        if (data.email) {
          if (Array.isArray(data.email)) {
            return data.email.join(', ');
          }
          return data.email;
        }
        
        // Erreurs de validation générales
        if (data.non_field_errors) {
          const errors = Array.isArray(data.non_field_errors)
            ? data.non_field_errors.join(', ')
            : data.non_field_errors;
          
          // Vérifier si c'est une erreur d'authentification
          if (
            errors.toLowerCase().includes('no active account') ||
            errors.toLowerCase().includes('unable to log in') ||
            errors.toLowerCase().includes('invalid credentials') ||
            errors.toLowerCase().includes('incorrect')
          ) {
            return 'Email ou mot de passe incorrect. Veuillez vérifier vos identifiants.';
          }
          
          return errors;
        }

        // Extraire toutes les erreurs de validation par champ et les combiner
        // Format Django REST Framework : {'field1': ['error1', 'error2'], 'field2': ['error3']}
        const fieldErrors: string[] = [];
        if (typeof data === 'object' && data !== null) {
          Object.keys(data).forEach((key) => {
            // Ignorer les clés déjà traitées
            if (['detail', 'message', 'error', 'non_field_errors', 'password', 'email'].includes(key)) {
              return;
            }
            
            const fieldValue = data[key];
            if (Array.isArray(fieldValue) && fieldValue.length > 0) {
              fieldErrors.push(`${key}: ${fieldValue.join(', ')}`);
            } else if (typeof fieldValue === 'string' && fieldValue.trim()) {
              fieldErrors.push(`${key}: ${fieldValue}`);
            }
          });
        }

        // Si on a trouvé des erreurs de champ, les retourner
        if (fieldErrors.length > 0) {
          return fieldErrors.join(' | ');
        }
      }

      if (!error.response) {
        return 'Problème de connexion. Vérifiez votre connexion internet.';
      }
    }

    // Messages par type (fallback générique uniquement si aucun message spécifique n'a été trouvé)
    switch (type) {
      case ErrorType.NETWORK:
        return 'Problème de connexion. Vérifiez votre connexion internet.';
      case ErrorType.AUTHENTICATION:
        // Si c'est une erreur 401 lors de la connexion, c'est probablement un mauvais mot de passe
        if (error instanceof AxiosError && error.config?.url?.includes('/token/')) {
          return 'Email ou mot de passe incorrect. Veuillez vérifier vos identifiants.';
        }
        return 'Votre session a expiré. Veuillez vous reconnecter.';
      case ErrorType.VALIDATION:
        // Essayer d'extraire un message plus spécifique de l'erreur
        if (error instanceof AxiosError && error.response?.data) {
          const data = error.response.data;
          // Si c'est un objet avec des erreurs, essayer de les formater
          if (typeof data === 'object' && data !== null) {
            const allErrors: string[] = [];
            Object.keys(data).forEach((key) => {
              const value = data[key];
              if (Array.isArray(value)) {
                allErrors.push(...value);
              } else if (typeof value === 'string') {
                allErrors.push(value);
              }
            });
            if (allErrors.length > 0) {
              return allErrors.join(' | ');
            }
          }
        }
        return 'Les données saisies sont invalides.';
      case ErrorType.SERVER:
        return 'Une erreur serveur est survenue. Veuillez réessayer plus tard.';
      default:
        return 'Une erreur inattendue est survenue.';
    }
  }

  handleApiError(error: any): ApiError {
    const { type, severity } = this.classifyError(error);
    const message = this.getUserMessage(error);
    const isOfflineBlocked = error.isOfflineBlocked || error.code === 'OFFLINE_MODE_FORCED' || error.message === 'OFFLINE_MODE_FORCED';

    const apiError: ApiError = {
      message,
      code: type,
      status: error instanceof AxiosError ? error.response?.status : undefined,
      details: error instanceof AxiosError ? error.response?.data : undefined,
      isOfflineBlocked,
    };

    // Préparer les détails pour le log (inclure l'URL pour détecter les endpoints B2B)
    const logDetails: any = {
      ...(apiError.details || {}),
      url: error instanceof AxiosError ? error.config?.url : undefined,
      config: error instanceof AxiosError ? { url: error.config?.url } : undefined,
    };

    // Logging
    this.log({
      message: apiError.message,
      type,
      severity,
      timestamp: Date.now(),
      details: logDetails,
    });

    return apiError;
  }

  log(errorLog: ErrorLog): void {
    // Ne pas logger les erreurs de mode hors ligne
    if (errorLog.message === 'OFFLINE_MODE_FORCED' || errorLog.severity === ErrorSeverity.LOW) {
      return;
    }

    // Ne pas logger les erreurs B2B optionnelles (endpoints inventory avec synced/categories)
    if (errorLog.details && typeof errorLog.details === 'object') {
      const url = (errorLog.details as any).url || (errorLog.details as any).config?.url;
      if (url && typeof url === 'string' && 
          (url.includes('/inventory/') || url.includes('/api/inventory/')) && 
          (url.includes('/synced/') || url.includes('/categories/'))) {
        return; // Erreur B2B optionnelle, ne pas logger
      }
    }

    this.logs.push(errorLog);
    
    // Garder seulement les 100 derniers logs
    if (this.logs.length > 100) {
      this.logs = this.logs.slice(-100);
    }

    // Logging console en développement (sauf pour les erreurs de mode hors ligne)
    if (__DEV__ && errorLog.severity !== ErrorSeverity.LOW) {
      console.error(`[${errorLog.severity.toUpperCase()}] ${errorLog.type}:`, errorLog.message, errorLog.details);
    }
  }

  getLogs(): ErrorLog[] {
    return [...this.logs];
  }

  clearLogs(): void {
    this.logs = [];
  }
}

export const errorService = new ErrorService();

