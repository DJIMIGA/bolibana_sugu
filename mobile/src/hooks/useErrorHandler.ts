import { useCallback } from 'react';
import { errorService, ErrorSeverity } from '../services/errorService';
import { ApiError } from '../types';

export const useErrorHandler = () => {
  const handleError = useCallback((error: any): ApiError => {
    return errorService.handleApiError(error);
  }, []);

  const getUserMessage = useCallback((error: any): string => {
    return errorService.getUserMessage(error);
  }, []);

  return {
    handleError,
    getUserMessage,
  };
};
