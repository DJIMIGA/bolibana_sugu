import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Linking,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { useNavigation } from '@react-navigation/native';
import { COLORS } from '../utils/constants';
import Logo from '../components/Logo';
import apiClient from '../services/api';
import { API_ENDPOINTS } from '../utils/constants';
import { Ionicons } from '@expo/vector-icons';
import { LoadingScreen } from '../components/LoadingScreen';

const SignupScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const { isLoggingIn } = useAppSelector((state) => state.auth);
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    passwordConfirm: '',
    first_name: '',
    last_name: '',
    phone: '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [acceptedCGV, setAcceptedCGV] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.email) {
      newErrors.email = 'L\'email est requis';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'L\'email n\'est pas valide';
    }

    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Le mot de passe doit contenir au moins 8 caractères';
    }

    if (!formData.passwordConfirm) {
      newErrors.passwordConfirm = 'Veuillez confirmer le mot de passe';
    } else if (formData.password !== formData.passwordConfirm) {
      newErrors.passwordConfirm = 'Les mots de passe ne correspondent pas';
    }

    if (!formData.first_name) {
      newErrors.first_name = 'Le prénom est requis';
    }

    if (!formData.last_name) {
      newErrors.last_name = 'Le nom est requis';
    }

    if (formData.phone && !/^\+?[0-9]{8,15}$/.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = 'Le numéro de téléphone n\'est pas valide';
    }

    if (!acceptedCGV) {
      newErrors.cgv = 'Vous devez accepter les conditions générales de vente';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSignup = async () => {
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      // Appeler l'endpoint d'inscription API
      const response = await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, {
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone || undefined,
      });

      Alert.alert(
        'Inscription réussie',
        'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.',
        [
          {
            text: 'OK',
            onPress: () => {
              // Naviguer vers l'écran de connexion
              (navigation as any).navigate('Login');
            },
          },
        ]
      );
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.error ||
                          error.response?.data?.detail ||
                          'Une erreur est survenue lors de l\'inscription';
      
      if (error.response?.data) {
        // Gérer les erreurs de validation du backend
        const backendErrors = error.response.data;
        const newErrors: Record<string, string> = {};
        
        // Gérer l'erreur générale
        if (backendErrors.error) {
          const generalError = Array.isArray(backendErrors.error) 
            ? backendErrors.error[0] 
            : backendErrors.error;
          
          // Essayer de mapper l'erreur générale aux champs spécifiques
          if (generalError.includes('email')) {
            newErrors.email = generalError;
          } else if (generalError.includes('mot de passe') || generalError.includes('password')) {
            newErrors.password = generalError;
          } else if (generalError.includes('prénom') || generalError.includes('first_name')) {
            newErrors.first_name = generalError;
          } else if (generalError.includes('nom') || generalError.includes('last_name')) {
            newErrors.last_name = generalError;
          } else {
            // Si on ne peut pas mapper, afficher l'erreur générale
            Alert.alert('Erreur', generalError);
            return;
          }
        }
        
        // Gérer les erreurs spécifiques par champ
        if (backendErrors.email) {
          newErrors.email = Array.isArray(backendErrors.email) 
            ? backendErrors.email[0] 
            : backendErrors.email;
        }
        if (backendErrors.password) {
          newErrors.password = Array.isArray(backendErrors.password) 
            ? backendErrors.password[0] 
            : backendErrors.password;
        }
        if (backendErrors.first_name) {
          newErrors.first_name = Array.isArray(backendErrors.first_name) 
            ? backendErrors.first_name[0] 
            : backendErrors.first_name;
        }
        if (backendErrors.last_name) {
          newErrors.last_name = Array.isArray(backendErrors.last_name) 
            ? backendErrors.last_name[0] 
            : backendErrors.last_name;
        }
        
        if (Object.keys(newErrors).length > 0) {
          setErrors(newErrors);
        } else {
          Alert.alert('Erreur', errorMessage);
        }
      } else {
        Alert.alert('Erreur', errorMessage);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitting || isLoggingIn) {
    return <LoadingScreen />;
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.content}>
          <View style={styles.logoContainer}>
            <Logo size="medium" dimension={110} showText={false} />
            <Text style={styles.appTitle}>Sugu</Text>
          </View>
          <Text style={styles.subtitle}>Créez votre compte</Text>

          <View style={styles.form}>
            <View style={styles.nameRow}>
              <View style={[styles.nameInput, { marginRight: 8 }]}>
                <Text style={styles.label}>Prénom *</Text>
                <TextInput
                  style={[styles.input, errors.first_name && styles.inputError]}
                  placeholder="Prénom"
                  placeholderTextColor={COLORS.TEXT_SECONDARY}
                  value={formData.first_name}
                  onChangeText={(text) => {
                    setFormData({ ...formData, first_name: text });
                    if (errors.first_name) setErrors({ ...errors, first_name: '' });
                  }}
                  autoCapitalize="words"
                />
                {errors.first_name && (
                  <Text style={styles.errorText}>{errors.first_name}</Text>
                )}
              </View>
              <View style={[styles.nameInput, { marginLeft: 8 }]}>
                <Text style={styles.label}>Nom *</Text>
                <TextInput
                  style={[styles.input, errors.last_name && styles.inputError]}
                  placeholder="Nom"
                  placeholderTextColor={COLORS.TEXT_SECONDARY}
                  value={formData.last_name}
                  onChangeText={(text) => {
                    setFormData({ ...formData, last_name: text });
                    if (errors.last_name) setErrors({ ...errors, last_name: '' });
                  }}
                  autoCapitalize="words"
                />
                {errors.last_name && (
                  <Text style={styles.errorText}>{errors.last_name}</Text>
                )}
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Email *</Text>
              <TextInput
                style={[styles.input, errors.email && styles.inputError]}
                placeholder="Email"
                placeholderTextColor={COLORS.TEXT_SECONDARY}
                value={formData.email}
                onChangeText={(text) => {
                  setFormData({ ...formData, email: text });
                  if (errors.email) setErrors({ ...errors, email: '' });
                }}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />
              {errors.email && (
                <Text style={styles.errorText}>{errors.email}</Text>
              )}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Téléphone</Text>
              <TextInput
                style={[styles.input, errors.phone && styles.inputError]}
                placeholder="+223 XX XX XX XX"
                placeholderTextColor={COLORS.TEXT_SECONDARY}
                value={formData.phone}
                onChangeText={(text) => {
                  setFormData({ ...formData, phone: text });
                  if (errors.phone) setErrors({ ...errors, phone: '' });
                }}
                keyboardType="phone-pad"
              />
              {errors.phone && (
                <Text style={styles.errorText}>{errors.phone}</Text>
              )}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Mot de passe *</Text>
              <View style={styles.passwordContainer}>
                <TextInput
                  style={[styles.passwordInput, errors.password && styles.inputError]}
                  placeholder="Mot de passe (min. 8 caractères)"
                  placeholderTextColor={COLORS.TEXT_SECONDARY}
                  value={formData.password}
                  onChangeText={(text) => {
                    setFormData({ ...formData, password: text });
                    if (errors.password) setErrors({ ...errors, password: '' });
                  }}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                />
                <TouchableOpacity
                  style={styles.passwordToggle}
                  onPress={() => setShowPassword((prev) => !prev)}
                >
                  <Ionicons
                    name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                    size={20}
                    color={COLORS.TEXT_SECONDARY}
                  />
                </TouchableOpacity>
              </View>
              {errors.password && (
                <Text style={styles.errorText}>{errors.password}</Text>
              )}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Confirmer le mot de passe *</Text>
              <View style={styles.passwordContainer}>
                <TextInput
                  style={[styles.passwordInput, errors.passwordConfirm && styles.inputError]}
                  placeholder="Confirmer le mot de passe"
                  placeholderTextColor={COLORS.TEXT_SECONDARY}
                  value={formData.passwordConfirm}
                  onChangeText={(text) => {
                    setFormData({ ...formData, passwordConfirm: text });
                    if (errors.passwordConfirm) setErrors({ ...errors, passwordConfirm: '' });
                  }}
                  secureTextEntry={!showPasswordConfirm}
                  autoCapitalize="none"
                />
                <TouchableOpacity
                  style={styles.passwordToggle}
                  onPress={() => setShowPasswordConfirm((prev) => !prev)}
                >
                  <Ionicons
                    name={showPasswordConfirm ? 'eye-off-outline' : 'eye-outline'}
                    size={20}
                    color={COLORS.TEXT_SECONDARY}
                  />
                </TouchableOpacity>
              </View>
              {errors.passwordConfirm && (
                <Text style={styles.errorText}>{errors.passwordConfirm}</Text>
              )}
            </View>

            {/* Checkbox CGV */}
            <View style={styles.cgvContainer}>
              <TouchableOpacity
                style={styles.checkboxContainer}
                onPress={() => setAcceptedCGV(!acceptedCGV)}
              >
                <View style={[styles.checkbox, acceptedCGV && styles.checkboxChecked]}>
                  {acceptedCGV && (
                    <Text style={styles.checkboxCheckmark}>✓</Text>
                  )}
                </View>
                <Text style={styles.cgvText}>
                  J'accepte les{' '}
                  <Text
                    style={styles.cgvLink}
                    onPress={() => {
                      (navigation as any).navigate('WebView', {
                        url: 'https://www.bolibana.com/core/cgv/',
                        title: 'Conditions Générales de Vente',
                      });
                    }}
                  >
                    Conditions Générales de Vente
                  </Text>
                  {' '}et les{' '}
                  <Text
                    style={styles.cgvLink}
                    onPress={() => {
                      (navigation as any).navigate('WebView', {
                        url: 'https://www.bolibana.com/core/terms-conditions/',
                        title: 'Mentions Légales',
                      });
                    }}
                  >
                    Mentions Légales
                  </Text>
                </Text>
              </TouchableOpacity>
              {errors.cgv && (
                <Text style={styles.errorText}>{errors.cgv}</Text>
              )}
            </View>

            <TouchableOpacity
              style={[styles.button, (isSubmitting || !acceptedCGV) && styles.buttonDisabled]}
              onPress={handleSignup}
              disabled={isSubmitting || !acceptedCGV}
            >
              <Text style={styles.buttonText}>Créer un compte</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => (navigation as any).navigate('Login')}
            >
              <Text style={styles.linkText}>
                Vous avez déjà un compte ? <Text style={styles.linkTextBold}>Se connecter</Text>
              </Text>
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
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: 16,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'center',
    gap: 8,
    marginBottom: 4,
  },
  appTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: COLORS.PRIMARY,
    letterSpacing: 0.5,
  },
  subtitle: {
    fontSize: 15,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    marginBottom: 8,
  },
  form: {
    width: '100%',
  },
  nameRow: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  nameInput: {
    flex: 1,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.TEXT,
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    padding: 16,
    fontSize: 16,
    color: COLORS.TEXT,
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  passwordInput: {
    flex: 1,
    padding: 16,
    fontSize: 16,
    color: COLORS.TEXT,
    paddingRight: 8,
  },
  passwordToggle: {
    paddingHorizontal: 16,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  inputError: {
    borderWidth: 1,
    borderColor: COLORS.ERROR,
  },
  button: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  linkButton: {
    marginTop: 8,
    alignItems: 'center',
  },
  linkText: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
  },
  linkTextBold: {
    color: COLORS.PRIMARY,
    fontWeight: '600',
  },
  errorText: {
    color: COLORS.ERROR,
    fontSize: 12,
    marginTop: 4,
  },
  cgvContainer: {
    marginTop: 8,
    marginBottom: 8,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  checkbox: {
    width: 24,
    height: 24,
    borderWidth: 2,
    borderColor: COLORS.TEXT_SECONDARY,
    borderRadius: 4,
    marginRight: 12,
    marginTop: 2,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  checkboxChecked: {
    backgroundColor: COLORS.PRIMARY,
    borderColor: COLORS.PRIMARY,
  },
  checkboxCheckmark: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cgvText: {
    flex: 1,
    fontSize: 14,
    color: COLORS.TEXT,
    lineHeight: 20,
  },
  cgvLink: {
    color: COLORS.PRIMARY,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
});

export default SignupScreen;

