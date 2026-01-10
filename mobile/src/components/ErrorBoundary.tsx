import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { errorService } from '../services/errorService';
import { COLORS } from '../utils/constants';
import Logo from './Logo';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Logger l'erreur
    errorService.log({
      message: error.message,
      type: 'unknown' as any,
      severity: 'critical' as any,
      timestamp: Date.now(),
      details: {
        stack: error.stack,
        componentStack: errorInfo.componentStack,
      },
    });

    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.container}>
          <View style={styles.logoContainer}>
            <Logo size="large" showText={false} />
            <View style={styles.brandContainer}>
              <Text style={styles.brandMain}>BOLIBANA</Text>
              <Text style={styles.brandSub}>SUGU</Text>
            </View>
          </View>
          
          <View style={styles.errorCard}>
            <Text style={styles.title}>Oups ! Une erreur est survenue</Text>
            <Text style={styles.message}>
              {this.state.error?.message || 'Une erreur inattendue s\'est produite'}
            </Text>
            <TouchableOpacity style={styles.button} onPress={this.handleReset}>
              <Text style={styles.buttonText}>Réessayer</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>Si le problème persiste, veuillez redémarrer l'application.</Text>
          </View>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#FFFFFF',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  brandContainer: {
    alignItems: 'center',
    marginTop: 16,
  },
  brandMain: {
    fontSize: 10,
    fontWeight: '600',
    color: COLORS.TEXT_SECONDARY,
    letterSpacing: 4,
    marginBottom: 2,
  },
  brandSub: {
    fontSize: 32,
    fontWeight: '900',
    color: COLORS.PRIMARY,
    letterSpacing: 1,
  },
  errorCard: {
    width: '100%',
    backgroundColor: '#F9FAFB',
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.TEXT,
    marginBottom: 12,
    textAlign: 'center',
  },
  message: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: 24,
    textAlign: 'center',
    lineHeight: 20,
  },
  button: {
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
    shadowColor: COLORS.PRIMARY,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  footer: {
    position: 'absolute',
    bottom: 40,
    paddingHorizontal: 40,
  },
  footerText: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    lineHeight: 18,
  },
});
