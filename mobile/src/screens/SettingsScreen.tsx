import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
  TextInput,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, API_ENDPOINTS } from '../utils/constants';
import apiClient from '../services/api';
import { useNavigation } from '@react-navigation/native';
import { useDispatch, useSelector } from 'react-redux';
import { logoutAsync } from '../store/slices/authSlice';
import { RootState } from '../store/store';
import { LoadingScreen } from '../components/LoadingScreen';

const SettingsScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useDispatch();
  const { isReadOnly } = useSelector((state: RootState) => state.auth);
  const [isPasswordModalVisible, setIsPasswordModalVisible] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);
  const [passwordForm, setPasswordForm] = React.useState({
    current_password: '',
    new_password: '',
    confirm_new_password: '',
  });
  const [showPasswords, setShowPasswords] = React.useState({
    current: false,
    new: false,
    confirm: false,
  });

  const handleChangePassword = async () => {
    // Validation
    if (!passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_new_password) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    if (passwordForm.new_password !== passwordForm.confirm_new_password) {
      Alert.alert('Erreur', 'Les nouveaux mots de passe ne correspondent pas');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      Alert.alert('Erreur', 'Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    setIsLoading(true);
    try {
      await apiClient.post(API_ENDPOINTS.CHANGE_PASSWORD, passwordForm);
      Alert.alert('Succès', 'Votre mot de passe a été mis à jour avec succès !', [
        {
          text: 'OK',
          onPress: () => {
            setIsPasswordModalVisible(false);
            setPasswordForm({
              current_password: '',
              new_password: '',
              confirm_new_password: '',
            });
          },
        },
      ]);
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.current_password?.[0] ||
        error.response?.data?.new_password?.[0] ||
        error.response?.data?.confirm_new_password?.[0] ||
        error.response?.data?.error ||
        'Une erreur est survenue lors du changement de mot de passe';
      Alert.alert('Erreur', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      'Supprimer le compte',
      'Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible et toutes vos données seront perdues.',
      [
        {
          text: 'Annuler',
          style: 'cancel',
        },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: async () => {
            setIsLoading(true);
            try {
              await apiClient.post(API_ENDPOINTS.DELETE_ACCOUNT);
              Alert.alert(
                'Compte supprimé',
                'Votre compte a été supprimé avec succès.',
                [
                  {
                    text: 'OK',
                    onPress: async () => {
                      await dispatch(logoutAsync() as any);
                      navigation.reset({
                        index: 0,
                        routes: [{ name: 'Products' as never }],
                      });
                    },
                  },
                ]
              );
            } catch (error: any) {
              const errorMessage =
                error.response?.data?.error || 'Une erreur est survenue lors de la suppression du compte';
              Alert.alert('Erreur', errorMessage);
            } finally {
              setIsLoading(false);
            }
          },
        },
      ]
    );
  };

  const handleAbout = () => {
    Alert.alert(
      'À propos',
      'Bolibana Sugu',
      [{ text: 'OK' }]
    );
  };

  const handleSupport = () => {
    Alert.alert(
      'Contact',
      'Pour toute question ou assistance, veuillez nous contacter :\n\nEmail: bolibanasugu@gmail.com\nTéléphone: 72 46 42 94\nBamako, Mali',
      [{ text: 'OK' }]
    );
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Paramètres</Text>
      </View>
      
      <View style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Compte</Text>
          
          <TouchableOpacity
            style={styles.menuItem}
            onPress={() => setIsPasswordModalVisible(true)}
          >
            <View style={styles.menuItemLeft}>
              <Ionicons name="lock-closed-outline" size={24} color={COLORS.TEXT} />
              <Text style={styles.menuItemText}>Changer le mot de passe</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={COLORS.TEXT_SECONDARY} />
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem} onPress={handleDeleteAccount}>
            <View style={styles.menuItemLeft}>
              <Ionicons name="trash-outline" size={24} color={COLORS.ERROR} />
              <Text style={[styles.menuItemText, { color: COLORS.ERROR }]}>
                Supprimer le compte
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={COLORS.TEXT_SECONDARY} />
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Application</Text>
          
          <TouchableOpacity style={styles.menuItem} onPress={handleAbout}>
            <View style={styles.menuItemLeft}>
              <Ionicons name="information-circle-outline" size={24} color={COLORS.TEXT} />
              <Text style={styles.menuItemText}>À propos</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={COLORS.TEXT_SECONDARY} />
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem} onPress={handleSupport}>
            <View style={styles.menuItemLeft}>
              <Ionicons name="help-circle-outline" size={24} color={COLORS.TEXT} />
              <Text style={styles.menuItemText}>Aide et support</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={COLORS.TEXT_SECONDARY} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Modal de changement de mot de passe */}
      <Modal
        visible={isPasswordModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setIsPasswordModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Changer le mot de passe</Text>
              <TouchableOpacity
                onPress={() => setIsPasswordModalVisible(false)}
                style={styles.modalCloseButton}
              >
                <Ionicons name="close" size={24} color={COLORS.TEXT} />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              <View style={styles.inputContainer}>
                <Text style={styles.inputLabel}>Mot de passe actuel *</Text>
                <View style={styles.passwordInputContainer}>
                  <TextInput
                    style={styles.passwordInput}
                    placeholder="Mot de passe actuel"
                    secureTextEntry={!showPasswords.current}
                    value={passwordForm.current_password}
                    onChangeText={(text) =>
                      setPasswordForm({ ...passwordForm, current_password: text })
                    }
                    autoCapitalize="none"
                  />
                  <TouchableOpacity
                    onPress={() =>
                      setShowPasswords({ ...showPasswords, current: !showPasswords.current })
                    }
                    style={styles.passwordToggle}
                  >
                    <Ionicons
                      name={showPasswords.current ? 'eye-off-outline' : 'eye-outline'}
                      size={20}
                      color={COLORS.TEXT_SECONDARY}
                    />
                  </TouchableOpacity>
                </View>
              </View>

              <View style={styles.inputContainer}>
                <Text style={styles.inputLabel}>Nouveau mot de passe *</Text>
                <View style={styles.passwordInputContainer}>
                  <TextInput
                    style={styles.passwordInput}
                    placeholder="Nouveau mot de passe"
                    secureTextEntry={!showPasswords.new}
                    value={passwordForm.new_password}
                    onChangeText={(text) =>
                      setPasswordForm({ ...passwordForm, new_password: text })
                    }
                    autoCapitalize="none"
                  />
                  <TouchableOpacity
                    onPress={() =>
                      setShowPasswords({ ...showPasswords, new: !showPasswords.new })
                    }
                    style={styles.passwordToggle}
                  >
                    <Ionicons
                      name={showPasswords.new ? 'eye-off-outline' : 'eye-outline'}
                      size={20}
                      color={COLORS.TEXT_SECONDARY}
                    />
                  </TouchableOpacity>
                </View>
              </View>

              <View style={styles.inputContainer}>
                <Text style={styles.inputLabel}>Confirmer le nouveau mot de passe *</Text>
                <View style={styles.passwordInputContainer}>
                  <TextInput
                    style={styles.passwordInput}
                    placeholder="Confirmer le nouveau mot de passe"
                    secureTextEntry={!showPasswords.confirm}
                    value={passwordForm.confirm_new_password}
                    onChangeText={(text) =>
                      setPasswordForm({ ...passwordForm, confirm_new_password: text })
                    }
                    autoCapitalize="none"
                  />
                  <TouchableOpacity
                    onPress={() =>
                      setShowPasswords({ ...showPasswords, confirm: !showPasswords.confirm })
                    }
                    style={styles.passwordToggle}
                  >
                    <Ionicons
                      name={showPasswords.confirm ? 'eye-off-outline' : 'eye-outline'}
                      size={20}
                      color={COLORS.TEXT_SECONDARY}
                    />
                  </TouchableOpacity>
                </View>
              </View>

              <TouchableOpacity
                style={[styles.saveButton, isLoading && styles.saveButtonDisabled]}
                onPress={handleChangePassword}
                disabled={isLoading}
              >
                <Text style={styles.saveButtonText}>Enregistrer</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  header: {
    backgroundColor: COLORS.PRIMARY,
    padding: 24,
    paddingTop: 60,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  content: {
    padding: 16,
  },
  section: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 16,
  },
  menuItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  menuItemText: {
    fontSize: 16,
    color: COLORS.TEXT,
    marginLeft: 12,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    width: '90%',
    maxHeight: '80%',
    padding: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.TEXT,
  },
  modalCloseButton: {
    padding: 4,
  },
  modalBody: {
    maxHeight: 400,
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 8,
  },
  passwordInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    paddingHorizontal: 12,
    backgroundColor: '#FFFFFF',
  },
  passwordInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
    color: COLORS.TEXT,
  },
  passwordToggle: {
    padding: 8,
  },
  saveButton: {
    backgroundColor: COLORS.PRIMARY,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 10,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default SettingsScreen;

