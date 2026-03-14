import { useCallback } from 'react';
import { useAppSelector } from '../store/hooks';
import { User } from '../types';

export const useUserPermissions = () => {
  const user = useAppSelector((state) => state.auth.user);

  const hasPermission = useCallback((permission: string): boolean => {
    if (!user) return false;
    
    // Vérifier les permissions basées sur le profil utilisateur
    // À adapter selon votre système de permissions
    if (user.is_staff) {
      return true; // Les staff ont tous les droits
    }

    // Ajouter d'autres vérifications selon vos besoins
    return false;
  }, [user]);

  const isAdmin = useCallback((): boolean => {
    return user?.is_staff || false;
  }, [user]);

  const isAuthenticated = useCallback((): boolean => {
    return !!user;
  }, [user]);

  return {
    user,
    hasPermission,
    isAdmin,
    isAuthenticated,
  };
};
