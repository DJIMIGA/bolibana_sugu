import { useState, useCallback } from 'react';
import * as ImagePicker from 'expo-image-picker';
import { uploadFile } from '../services/api';
import { Alert } from 'react-native';

interface ImageUploadResult {
  url: string;
  success: boolean;
  error?: string;
}

export const useImageManager = () => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pickImage = useCallback(async (): Promise<string | null> => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', 'L\'accès à la galerie est nécessaire.');
        return null;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        return result.assets[0].uri;
      }
      return null;
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la sélection de l\'image');
      return null;
    }
  }, []);

  const takePhoto = useCallback(async (): Promise<string | null> => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', 'L\'accès à la caméra est nécessaire.');
        return null;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        return result.assets[0].uri;
      }
      return null;
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la prise de photo');
      return null;
    }
  }, []);

  const uploadImage = useCallback(async (
    endpoint: string,
    imageUri: string,
    additionalData?: Record<string, any>
  ): Promise<ImageUploadResult> => {
    setUploading(true);
    setError(null);

    try {
      // Créer un objet File à partir de l'URI
      const filename = imageUri.split('/').pop() || 'image.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : 'image/jpeg';

      const formData = new FormData();
      formData.append('file', {
        uri: imageUri,
        name: filename,
        type,
      } as any);

      if (additionalData) {
        Object.keys(additionalData).forEach((key) => {
          formData.append(key, additionalData[key]);
        });
      }

      const response = await uploadFile(endpoint, formData, additionalData);
      
      setUploading(false);
      return {
        url: response.data.url || response.data.file || imageUri,
        success: true,
      };
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Erreur lors de l\'upload';
      setError(errorMessage);
      setUploading(false);
      return {
        url: '',
        success: false,
        error: errorMessage,
      };
    }
  }, []);

  return {
    pickImage,
    takePhoto,
    uploadImage,
    uploading,
    error,
  };
};
