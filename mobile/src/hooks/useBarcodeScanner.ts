import { useState, useCallback } from 'react';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Alert } from 'react-native';

export const useBarcodeScanner = () => {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [scannedData, setScannedData] = useState<string | null>(null);

  const handleBarCodeScanned = useCallback(({ data }: { data: string }) => {
    if (!scanned) {
      setScanned(true);
      setScannedData(data);
    }
  }, [scanned]);

  const resetScanner = useCallback(() => {
    setScanned(false);
    setScannedData(null);
  }, []);

  const checkPermissions = useCallback(async () => {
    if (!permission) {
      const result = await requestPermission();
      if (!result.granted) {
        Alert.alert(
          'Permission requise',
          'L\'accès à la caméra est nécessaire pour scanner les codes-barres.'
        );
        return false;
      }
    }
    return true;
  }, [permission, requestPermission]);

  return {
    permission,
    scanned,
    scannedData,
    handleBarCodeScanned,
    resetScanner,
    checkPermissions,
  };
};
