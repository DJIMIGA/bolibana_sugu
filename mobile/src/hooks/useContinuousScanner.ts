import { useState, useCallback, useRef } from 'react';
import { debounce } from '../utils/helpers';

export const useContinuousScanner = (onScan: (data: string) => void, debounceMs: number = 1000) => {
  const [scannedCodes, setScannedCodes] = useState<Set<string>>(new Set());
  const debouncedOnScan = useRef(debounce(onScan, debounceMs)).current;

  const handleScan = useCallback((data: string) => {
    // Éviter les doublons
    if (!scannedCodes.has(data)) {
      scannedCodes.add(data);
      setScannedCodes(new Set(scannedCodes));
      debouncedOnScan(data);
    }
  }, [scannedCodes, debouncedOnScan]);

  const reset = useCallback(() => {
    setScannedCodes(new Set());
  }, []);

  return {
    handleScan,
    reset,
  };
};
