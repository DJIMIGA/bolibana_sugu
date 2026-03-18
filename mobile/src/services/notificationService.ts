import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import * as Sentry from '@sentry/react-native';
import apiClient from './api';
import { API_ENDPOINTS } from '../utils/constants';

// Afficher les notifications même quand l'app est au premier plan
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

type NotificationTapCallback = (data: Record<string, any>) => void;

class NotificationService {
  private expoPushToken: string | null = null;
  private notificationListener: Notifications.EventSubscription | null = null;
  private responseListener: Notifications.EventSubscription | null = null;
  private onTapCallback: NotificationTapCallback | null = null;
  private onReceivedCallback: (() => void) | null = null;

  async registerForPushNotifications(): Promise<string | null> {
    try {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        return null;
      }

      const tokenData = await Notifications.getExpoPushTokenAsync({
        projectId: '408e7748-1d05-460b-92f4-0614d8b2a3c4',
      });
      this.expoPushToken = tokenData.data;

      // Canal Android
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'Notifications',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#008000',
        });
      }

      return this.expoPushToken;
    } catch (error) {
      Sentry.captureException(error);
      if (__DEV__) console.error('[NotificationService] Erreur registration:', error);
      return null;
    }
  }

  async sendTokenToBackend(token: string): Promise<void> {
    try {
      await apiClient.post(API_ENDPOINTS.NOTIFICATIONS.REGISTER_TOKEN, {
        token,
        device_type: Platform.OS,
      });
    } catch (error) {
      if (__DEV__) console.error('[NotificationService] Erreur envoi token:', error);
    }
  }

  async unregisterToken(): Promise<void> {
    if (!this.expoPushToken) return;
    try {
      await apiClient.post(API_ENDPOINTS.NOTIFICATIONS.UNREGISTER_TOKEN, {
        token: this.expoPushToken,
      });
    } catch (error) {
      // Silencieux
    }
    this.expoPushToken = null;
  }

  setOnTapCallback(callback: NotificationTapCallback): void {
    this.onTapCallback = callback;
  }

  setOnReceivedCallback(callback: () => void): void {
    this.onReceivedCallback = callback;
  }

  startListening(): void {
    // Notification reçue en foreground
    this.notificationListener = Notifications.addNotificationReceivedListener(() => {
      if (this.onReceivedCallback) {
        this.onReceivedCallback();
      }
    });

    // Notification tappée (background ou killed)
    this.responseListener = Notifications.addNotificationResponseReceivedListener((response) => {
      const data = response.notification.request.content.data;
      if (this.onTapCallback && data) {
        this.onTapCallback(data as Record<string, any>);
      }
    });
  }

  stopListening(): void {
    if (this.notificationListener) {
      this.notificationListener.remove();
      this.notificationListener = null;
    }
    if (this.responseListener) {
      this.responseListener.remove();
      this.responseListener = null;
    }
  }

  async setBadgeCount(count: number): Promise<void> {
    try {
      await Notifications.setBadgeCountAsync(count);
    } catch {
      // Certains appareils ne supportent pas les badges
    }
  }
}

export const notificationService = new NotificationService();
