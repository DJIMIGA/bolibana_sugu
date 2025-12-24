import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS } from '../utils/constants';
import apiClient from '../services/api';
import { API_ENDPOINTS } from '../utils/constants';

const CITY_CHOICES = [
  { value: 'BKO', label: 'Bamako' },
  { value: 'KAY', label: 'Kayes' },
  { value: 'KOU', label: 'Koulikoro' },
  { value: 'SIK', label: 'Sikasso' },
  { value: 'SEG', label: 'Ségou' },
  { value: 'MOP', label: 'Mopti' },
  { value: 'TOM', label: 'Tombouctou' },
  { value: 'GAO', label: 'Gao' },
  { value: 'KID', label: 'Kidal' },
  { value: 'MEN', label: 'Ménaka' },
  { value: 'TAO', label: 'Taoudénit' },
];

const ADDRESS_TYPE_CHOICES = [
  { value: 'DOM', label: 'Domicile' },
  { value: 'BUR', label: 'Bureau' },
  { value: 'AUT', label: 'Autre' },
];

type AddAddressRouteParams = {
  mode?: 'create' | 'edit';
  address?: {
    id: number;
    full_name?: string;
    street_address: string;
    address_type: 'DOM' | 'BUR' | 'AUT';
    quarter: string;
    city: string;
    additional_info?: string;
    is_default: boolean;
  };
};

const AddAddressScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute<any>();
  const [form, setForm] = useState({
    full_name: '',
    street_address: '',
    address_type: 'DOM',
    quarter: '',
    city: 'BKO',
    additional_info: '',
    is_default: false,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showCityPicker, setShowCityPicker] = useState(false);
  const [showAddressTypePicker, setShowAddressTypePicker] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [addressId, setAddressId] = useState<number | null>(null);

  // Initialiser le formulaire en mode édition si des données sont passées
  useEffect(() => {
    const params: AddAddressRouteParams | undefined = route?.params;
    if (params?.mode === 'edit' && params.address) {
      const addr = params.address;
      setIsEditMode(true);
      setAddressId(addr.id);
      setForm({
        full_name: addr.full_name || '',
        street_address: addr.street_address || '',
        address_type: addr.address_type || 'DOM',
        quarter: addr.quarter || '',
        city: addr.city || 'BKO',
        additional_info: addr.additional_info || '',
        is_default: addr.is_default ?? false,
      });
    } else {
      setIsEditMode(false);
      setAddressId(null);
    }
  }, [route?.params]);

  const handleChange = (field: keyof typeof form, value: string | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const validateForm = () => {
    if (!form.full_name || form.full_name.trim() === '') {
      Alert.alert('Erreur', 'Le nom complet est requis');
      return false;
    }
    if (!form.street_address || form.street_address.trim() === '') {
      Alert.alert('Erreur', 'L\'adresse est requise');
      return false;
    }
    if (!form.quarter || form.quarter.trim() === '') {
      Alert.alert('Erreur', 'Le quartier est requis');
      return false;
    }
    if (!form.city) {
      Alert.alert('Erreur', 'La ville est requise');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setIsSubmitting(true);

      const payload = {
        full_name: form.full_name.trim(),
        street_address: form.street_address.trim(),
        address_type: form.address_type,
        quarter: form.quarter.trim(),
        city: form.city,
        additional_info: form.additional_info.trim() || undefined,
        is_default: form.is_default,
      };

      let response;
      if (isEditMode && addressId) {
        response = await apiClient.put(`/addresses/${addressId}/update/`, payload);
        console.log('[AddAddressScreen] Address updated:', response.data);
      } else {
        response = await apiClient.post(API_ENDPOINTS.ADDRESSES, payload);
        console.log('[AddAddressScreen] Address created:', response.data);
      }

      Alert.alert('Succès', isEditMode ? 'Adresse mise à jour avec succès.' : 'Adresse ajoutée avec succès.', [
        {
          text: 'OK',
          onPress: () => {
            (navigation as any).goBack();
          },
        },
      ]);
    } catch (error: any) {
      console.error('[AddAddressScreen] Error:', error?.response?.data || error);
      const errorMessage =
        error?.response?.data?.detail ||
        error?.response?.data?.error ||
        error?.response?.data?.message ||
        "Impossible d'ajouter l'adresse. Veuillez réessayer.";
      Alert.alert('Erreur', errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => (navigation as any).goBack()}
          >
            <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>
            {isEditMode ? 'Modifier une adresse' : 'Ajouter une adresse'}
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.subtitle}>
            Renseignez vos informations de livraison pour vos prochaines commandes
          </Text>

          {/* Nom complet */}
          <View style={styles.field}>
            <Text style={styles.label}>Nom complet *</Text>
            <TextInput
              style={styles.input}
              placeholder="Nom complet"
              placeholderTextColor={COLORS.TEXT_SECONDARY}
              value={form.full_name}
              onChangeText={(text) => handleChange('full_name', text)}
            />
          </View>

          {/* Adresse */}
          <View style={styles.field}>
            <Text style={styles.label}>Adresse *</Text>
            <TextInput
              style={styles.input}
              placeholder="Rue, porte, etc."
              placeholderTextColor={COLORS.TEXT_SECONDARY}
              value={form.street_address}
              onChangeText={(text) => handleChange('street_address', text)}
            />
          </View>

          {/* Type d'adresse & Quartier */}
          <View style={styles.row}>
            <View style={[styles.field, styles.rowItem]}>
              <Text style={styles.label}>Type d'adresse</Text>
              <TouchableOpacity
                style={styles.pickerButton}
                onPress={() => setShowAddressTypePicker(!showAddressTypePicker)}
              >
                <Text style={styles.pickerText}>
                  {ADDRESS_TYPE_CHOICES.find((t) => t.value === form.address_type)?.label || 'Sélectionner'}
                </Text>
                <Ionicons name="chevron-down" size={20} color={COLORS.TEXT_SECONDARY} />
              </TouchableOpacity>
              {showAddressTypePicker && (
                <View style={styles.pickerOptions}>
                  {ADDRESS_TYPE_CHOICES.map((type) => (
                    <TouchableOpacity
                      key={type.value}
                      style={styles.pickerOption}
                      onPress={() => {
                        handleChange('address_type', type.value);
                        setShowAddressTypePicker(false);
                      }}
                    >
                      <Text style={styles.pickerOptionText}>{type.label}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              )}
            </View>
            <View style={[styles.field, styles.rowItem]}>
              <Text style={styles.label}>Quartier *</Text>
              <TextInput
                style={styles.input}
                placeholder="Quartier"
                placeholderTextColor={COLORS.TEXT_SECONDARY}
                value={form.quarter}
                onChangeText={(text) => handleChange('quarter', text)}
              />
            </View>
          </View>

          {/* Ville */}
          <View style={styles.field}>
            <Text style={styles.label}>Ville *</Text>
            <TouchableOpacity
              style={styles.pickerButton}
              onPress={() => setShowCityPicker(!showCityPicker)}
            >
              <Text style={styles.pickerText}>
                {CITY_CHOICES.find((c) => c.value === form.city)?.label || 'Sélectionner'}
              </Text>
              <Ionicons name="chevron-down" size={20} color={COLORS.TEXT_SECONDARY} />
            </TouchableOpacity>
            {showCityPicker && (
              <View style={styles.pickerOptions}>
                {CITY_CHOICES.map((city) => (
                  <TouchableOpacity
                    key={city.value}
                    style={styles.pickerOption}
                    onPress={() => {
                      handleChange('city', city.value);
                      setShowCityPicker(false);
                    }}
                  >
                    <Text style={styles.pickerOptionText}>{city.label}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </View>

          {/* Informations complémentaires */}
          <View style={styles.field}>
            <Text style={styles.label}>Informations complémentaires</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Bâtiment, étage, point de repère..."
              placeholderTextColor={COLORS.TEXT_SECONDARY}
              value={form.additional_info}
              onChangeText={(text) => handleChange('additional_info', text)}
              multiline
              numberOfLines={3}
            />
          </View>

          {/* Adresse par défaut */}
          <View style={styles.defaultRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.label}>Adresse par défaut</Text>
              <Text style={styles.helperText}>
                Utilisée automatiquement pour vos prochaines commandes
              </Text>
            </View>
            <Switch
              value={form.is_default}
              onValueChange={(val) => handleChange('is_default', val)}
              trackColor={{ false: '#D1D5DB', true: COLORS.PRIMARY }}
              thumbColor="#FFFFFF"
            />
          </View>

          {/* Boutons */}
          <View style={styles.actions}>
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={() => (navigation as any).goBack()}
              disabled={isSubmitting}
            >
              <Text style={styles.cancelText}>Annuler</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.button, styles.saveButton, isSubmitting && styles.buttonDisabled]}
              onPress={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Text style={styles.saveText}>
                  {isEditMode ? 'Enregistrer les modifications' : 'Ajouter cette adresse'}
                </Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    paddingBottom: 32,
  },
  header: {
    backgroundColor: COLORS.PRIMARY,
    paddingTop: 60,
    paddingBottom: 16,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    marginRight: 12,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  card: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  subtitle: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 20,
  },
  field: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    color: COLORS.TEXT,
    backgroundColor: '#F9FAFB',
  },
  textArea: {
    height: 90,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  rowItem: {
    flex: 1,
  },
  pickerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 12,
    backgroundColor: '#F9FAFB',
  },
  pickerText: {
    fontSize: 16,
    color: COLORS.TEXT,
  },
  pickerOptions: {
    marginTop: 4,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 10,
    backgroundColor: '#FFFFFF',
    maxHeight: 200,
    overflow: 'hidden',
  },
  pickerOption: {
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  pickerOptionText: {
    fontSize: 16,
    color: COLORS.TEXT,
  },
  defaultRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 8,
  },
  helperText: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 2,
  },
  actions: {
    flexDirection: 'row',
    marginTop: 24,
    gap: 12,
  },
  button: {
    flex: 1,
    borderRadius: 10,
  paddingVertical: 16,
  paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelButton: {
    backgroundColor: '#F3F4F6',
  },
  saveButton: {
    backgroundColor: COLORS.PRIMARY,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  cancelText: {
    color: COLORS.TEXT,
    fontSize: 16,
    fontWeight: '600',
  },
  saveText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default AddAddressScreen;

