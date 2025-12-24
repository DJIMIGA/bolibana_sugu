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
        if (data.error) return data.error;
        
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
      }

      if (!error.response) {
        return 'Problème de connexion. Vérifiez votre connexion internet.';
      }
    }

    // Messages par type
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

    const apiError: ApiError = {
      message,
      code: type,
      status: error instanceof AxiosError ? error.response?.status : undefined,
      details: error instanceof AxiosError ? error.response?.data : undefined,
    };

    // Logging
    this.log({
      message: apiError.message,
      type,
      severity,
      timestamp: Date.now(),
      details: apiError.details,
    });

    return apiError;
  }

  log(errorLog: ErrorLog): void {
    this.logs.push(errorLog);
    
    // Garder seulement les 100 derniers logs
    if (this.logs.length > 100) {
      this.logs = this.logs.slice(-100);
    }

    // Logging console en développement
    if (__DEV__) {
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

