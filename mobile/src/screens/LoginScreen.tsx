import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { loginAsync } from '../store/slices/authSlice';
import { useErrorHandler } from '../hooks/useErrorHandler';
import { useNavigation } from '@react-navigation/native';
import { COLORS } from '../utils/constants';
import Logo from '../components/Logo';
import { Ionicons } from '@expo/vector-icons';
import { LoadingScreen } from '../components/LoadingScreen';

const LoginScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const { isLoggingIn, error, sessionExpired, isAuthenticated } = useAppSelector((state) => state.auth);
  const { handleError, getUserMessage } = useErrorHandler();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionExpired) {
      Alert.alert(
        'Session expirée',
        'Votre session a expiré. Veuillez vous reconnecter.',
        [{ text: 'OK' }]
      );
    }
  }, [sessionExpired]);

  // SUPPRIMÉ : Plus de useEffect qui écoute isAuthenticated ou loginSuccess
  // Cela évite toute redirection automatique non désirée
  // La navigation se fera UNIQUEMENT dans handleLogin en cas de succès explicite

  const handleLogin = async () => {
    setLoginError(null);
    
    if (!email || !password) {
      setLoginError('Veuillez remplir tous les champs');
      return;
    }

    try {
      setLoginError(null);
      
      const result = await dispatch(loginAsync({ email, password })).unwrap();
      
      // Vérifier explicitement que la connexion a réussi avec tous les éléments nécessaires
      if (result && result.user && result.access) {
        setLoginError(null);
        
        // Attendre un peu pour s'assurer que le state Redux est complètement mis à jour
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Navigation EXPLICITE uniquement en cas de succès
        const nav = navigation as any;
        if (nav.goBack) {
          nav.goBack();
        }
      }
    } catch (err: any) {
      // En cas d'erreur avec unwrap(), err est directement le message d'erreur (string)
      // renvoyé par rejectWithValue dans authSlice.ts
      const errorMessage = typeof err === 'string' ? err : getUserMessage(err);
      
      setLoginError(errorMessage);
      // Afficher aussi une alerte pour attirer l'attention
      Alert.alert('Erreur', errorMessage);
      
      // L'utilisateur reste sur l'écran de connexion pour voir l'erreur
    }
  };

  if (isLoggingIn) {
    return <LoadingScreen />;
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Logo size="large" showText={false} />
          <Text style={styles.appTitle}>Sugu</Text>
        </View>
        <Text style={styles.subtitle}>Connectez-vous à votre compte</Text>

        <View style={styles.form}>
          <TextInput
            style={[
              styles.input,
              (loginError || error) && styles.inputError
            ]}
            placeholder="Email"
            placeholderTextColor={COLORS.TEXT_SECONDARY}
            value={email}
            onChangeText={(text) => {
              setEmail(text);
              if (loginError) setLoginError(null);
            }}
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
          />

          <View style={[
            styles.passwordContainer,
            (loginError || error) && styles.passwordContainerError
          ]}>
            <TextInput
              style={styles.passwordInput}
              placeholder="Mot de passe"
              placeholderTextColor={COLORS.TEXT_SECONDARY}
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                if (loginError) setLoginError(null);
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

          {(loginError || error) && (
            <View style={styles.errorContainer}>
              <Ionicons name="alert-circle" size={16} color={COLORS.ERROR} />
              <Text style={styles.errorText}>{loginError || error}</Text>
            </View>
          )}

          <TouchableOpacity
            style={[styles.button, isLoggingIn && styles.buttonDisabled]}
            onPress={handleLogin}
            disabled={isLoggingIn}
          >
            <Text style={styles.buttonText}>Se connecter</Text>
          </TouchableOpacity>

          <View style={styles.legalTextContainer}>
            <Text style={styles.legalText}>
              En vous connectant, vous acceptez nos{' '}
              <Text
                style={styles.legalLink}
                onPress={() => {
                  const nav = navigation as any;
                  if (nav.navigate) {
                    nav.navigate('WebView', {
                      url: 'https://www.bolibana.com/core/cgv/',
                      title: 'Conditions Générales de Vente',
                    });
                  }
                }}
              >
                Conditions Générales de Vente
              </Text>
              {' '}et nos{' '}
              <Text
                style={styles.legalLink}
                onPress={() => {
                  const nav = navigation as any;
                  if (nav.navigate) {
                    nav.navigate('WebView', {
                      url: 'https://www.bolibana.com/core/terms-conditions/',
                      title: 'Mentions Légales',
                    });
                  }
                }}
              >
                Mentions Légales
              </Text>
            </Text>
          </View>

          <TouchableOpacity
            style={styles.linkButton}
            onPress={() => {
              const nav = navigation as any;
              if (nav.navigate) {
                nav.navigate('Signup');
              }
            }}
          >
            <Text style={styles.linkText}>
              Pas encore de compte ? <Text style={styles.linkTextBold}>Créer un compte</Text>
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: 16,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 12,
    backgroundColor: 'rgba(0, 128, 255, 0.12)',
  },
  appTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
    marginTop: -20,
    lineHeight: 34,
    letterSpacing: 1,
    backgroundColor: 'rgba(255, 128, 0, 0.12)',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    marginBottom: 32,
  },
  form: {
    width: '100%',
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    marginBottom: 16,
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
  input: {
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    padding: 16,
    fontSize: 16,
    color: COLORS.TEXT,
    marginBottom: 16,
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
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEE2E2',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.ERROR,
  },
  errorText: {
    color: COLORS.ERROR,
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  inputError: {
    borderColor: COLORS.ERROR,
    borderWidth: 1,
    backgroundColor: '#FEE2E2',
  },
  passwordContainerError: {
    borderColor: COLORS.ERROR,
    borderWidth: 1,
    backgroundColor: '#FEE2E2',
  },
  linkButton: {
    marginTop: 16,
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
  legalTextContainer: {
    marginTop: 16,
    marginBottom: 8,
    paddingHorizontal: 8,
  },
  legalText: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    lineHeight: 18,
  },
  legalLink: {
    color: COLORS.PRIMARY,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
});

export default LoginScreen;
