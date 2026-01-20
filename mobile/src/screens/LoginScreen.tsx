import React, { useState, useEffect, useRef } from 'react';
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
  Keyboard,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { loginAsync } from '../store/slices/authSlice';
import { useErrorHandler } from '../hooks/useErrorHandler';
import { CommonActions, useNavigation, useRoute } from '@react-navigation/native';
import { COLORS } from '../utils/constants';
import Logo from '../components/Logo';
import { Ionicons } from '@expo/vector-icons';
import { LoadingScreen } from '../components/LoadingScreen';

const LoginScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigation = useNavigation();
  const route = useRoute<any>();
  const { isLoggingIn, error, sessionExpired, isAuthenticated, user, token } = useAppSelector((state) => state.auth);
  const { handleError, getUserMessage } = useErrorHandler();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [isHandlingLogin, setIsHandlingLogin] = useState(false); // Flag pour indiquer qu'on est en train de gérer la connexion
  const passwordInputRef = useRef<TextInput>(null);
  const redirectTo = route?.params?.redirectTo;

  const redirectAfterLogin = () => {
    const nav = navigation as any;
    const parentNav = nav.getParent?.();

    if (redirectTo === 'Checkout') {
      if (parentNav?.navigate) {
        parentNav.navigate('CartTab', { screen: 'Checkout' });
      }
    } else if (parentNav?.navigate) {
      parentNav.navigate('Home');
    }

    // Nettoyer la stack du profil pour éviter de revenir sur Login
    if (nav.popToTop) {
      nav.popToTop();
    } else if (nav.dispatch) {
      nav.dispatch(
        CommonActions.reset({
          index: 0,
          routes: [{ name: 'ProfileMain' }],
        })
      );
    } else if (nav.goBack) {
      nav.goBack();
    }
  };

  // Log à l'affichage de l'écran de connexion
  useEffect(() => {
    console.log('[LoginScreen] 🟢 ECRAN DE CONNEXION AFFICHE - État:', {
      isLoggingIn,
      isAuthenticated,
      hasUser: !!user,
      hasToken: !!token,
      sessionExpired,
      hasError: !!error
    });
  }, []);

  useEffect(() => {
    if (sessionExpired) {
      Alert.alert(
        'Session expirée',
        'Votre session a expiré. Veuillez vous reconnecter.',
        [{ text: 'OK' }]
      );
    }
  }, [sessionExpired]);

  // Rediriger automatiquement si l'utilisateur est déjà connecté
  // Mais seulement si on n'est pas en train de gérer la connexion manuellement
  // Cela évite la double navigation pendant handleLogin
  useEffect(() => {
    // Ne pas naviguer si on est en train de se connecter ou si handleLogin gère la navigation
    if (isLoggingIn || isHandlingLogin) {
      return;
    }
    
    if (isAuthenticated && user && token) {
      console.log('[LoginScreen] Utilisateur déjà connecté (useEffect), redirection après login...');
      redirectAfterLogin();
    }
  }, [isAuthenticated, user, token, navigation, isHandlingLogin, isLoggingIn, redirectTo]);

  const handleLogin = async () => {
    console.log('[LoginScreen] handleLogin appelé');
    setLoginError(null);
    setIsHandlingLogin(true); // Marquer qu'on gère la connexion manuellement
    
    if (!email || !password) {
      setLoginError('Veuillez remplir tous les champs');
      setIsHandlingLogin(false);
      return;
    }

    try {
      console.log('[LoginScreen] Début de la connexion...');
      setLoginError(null);
      
      const result = await dispatch(loginAsync({ email, password })).unwrap();
      console.log('[LoginScreen] Connexion réussie, result:', {
        hasUser: !!result?.user,
        hasAccess: !!result?.access,
        userEmail: result?.user?.email
      });
      
      // Vérifier explicitement que la connexion a réussi avec tous les éléments nécessaires
      if (result && result.user && result.access) {
        console.log('[LoginScreen] Tous les éléments présents, navigation immédiate...');
        setLoginError(null);
        
        // Navigation immédiate sans délai pour éviter l'affichage du profil
        // Le state Redux est déjà mis à jour par loginAsync.fulfilled
        redirectAfterLogin();
        console.log('[LoginScreen] Navigation effectuée');
        // Ne pas réinitialiser ici : l'écran va se démonter après la navigation
      } else {
        console.warn('[LoginScreen] Connexion réussie mais éléments manquants:', {
          hasResult: !!result,
          hasUser: !!result?.user,
          hasAccess: !!result?.access
        });
      }
    } catch (err: any) {
      console.error('[LoginScreen] Erreur de connexion:', err);
      setIsHandlingLogin(false); // Réinitialiser le flag en cas d'erreur
      // En cas d'erreur avec unwrap(), err est directement le message d'erreur (string)
      // renvoyé par rejectWithValue dans authSlice.ts
      const errorMessage = typeof err === 'string' ? err : getUserMessage(err);
      
      setLoginError(errorMessage);
      // Afficher aussi une alerte pour attirer l'attention
      Alert.alert('Erreur', errorMessage);
      
      // L'utilisateur reste sur l'écran de connexion pour voir l'erreur
    }
  };

  // Log à chaque render
  console.log('[LoginScreen] RENDER - isLoggingIn:', isLoggingIn, 'isAuthenticated:', isAuthenticated, 'hasUser:', !!user, 'hasToken:', !!token);

  // Si l'utilisateur est déjà connecté, ne pas afficher le formulaire
  // (la redirection sera gérée par le useEffect ci-dessus)
  if (isAuthenticated && user && token) {
    console.log('[LoginScreen] Utilisateur connecté, affichage LoadingScreen en attendant redirection');
    return <LoadingScreen />;
  }

  if (isLoggingIn) {
    console.log('[LoginScreen] Affichage LoadingScreen (isLoggingIn)');
    return <LoadingScreen />;
  }

  console.log('[LoginScreen] Affichage formulaire de connexion');
  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      enabled={Platform.OS === 'ios'}
    >
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.logoContainer}>
          <Logo size="medium" dimension={110} showText={false} />
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
            returnKeyType="next"
            onSubmitEditing={() => passwordInputRef.current?.focus()}
          />

          <View style={[
            styles.passwordContainer,
            (loginError || error) && styles.passwordContainerError
          ]}>
            <TextInput
              ref={passwordInputRef}
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
              returnKeyType="done"
              blurOnSubmit={true}
              onSubmitEditing={Keyboard.dismiss}
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
      </ScrollView>
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
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'center',
    gap: 8,
    marginBottom: 8,
  },
  appTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: COLORS.PRIMARY,
    letterSpacing: 0.5,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: COLORS.PRIMARY,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 15,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    marginBottom: 24,
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
