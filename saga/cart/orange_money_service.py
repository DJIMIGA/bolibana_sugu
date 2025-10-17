"""
Service Orange Money Web Payment API
Gère l'intégration avec l'API Orange Money pour les paiements
"""

import requests
import base64
import json
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class OrangeMoneyService:
    """
    Service pour gérer les paiements Orange Money
    """
    
    def __init__(self):
        self.config = settings.ORANGE_MONEY_CONFIG
        self.webhooks_config = settings.ORANGE_MONEY_WEBHOOKS
        self.session = requests.Session()
        self.session.timeout = self.config['timeout']
    
    def is_enabled(self) -> bool:
        """Vérifie si Orange Money est activé"""
        return self.config['enabled'] and all([
            self.config['merchant_key'],
            self.config['client_id'],
            self.config['client_secret']
        ])
    
    def get_access_token(self) -> Optional[str]:
        """
        Récupère un token d'accès Orange Money
        Retourne le token ou None en cas d'erreur
        """
        if not self.is_enabled():
            logger.error("Orange Money n'est pas configuré correctement")
            return None
        
        # Vérifier le cache d'abord
        cache_key = 'orange_money_access_token'
        cached_token = cache.get(cache_key)
        if cached_token:
            logger.info("Token Orange Money récupéré depuis le cache")
            return cached_token
        
        try:
            # Créer les credentials Basic Auth
            credentials = f"{self.config['client_id']}:{self.config['client_secret']}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            logger.info(f"Demande de token Orange Money vers {self.config['token_url']}")
            response = self.session.post(
                self.config['token_url'],
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                
                # Mettre en cache le token (expire 5 minutes avant la vraie expiration)
                cache_timeout = max(expires_in - 300, 60)
                cache.set(cache_key, access_token, cache_timeout)
                
                logger.info("Token Orange Money obtenu avec succès")
                return access_token
            else:
                logger.error(f"Erreur lors de la récupération du token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception lors de la récupération du token Orange Money: {str(e)}")
            return None
    
    def create_payment_session(self, order_data: Dict) -> Tuple[bool, Dict]:
        """
        Crée une session de paiement Orange Money
        
        Args:
            order_data: Données de la commande contenant:
                - order_id: ID unique de la commande
                - amount: Montant en centimes
                - return_url: URL de retour
                - cancel_url: URL d'annulation
                - notif_url: URL de notification
                - reference: Référence marchand
        
        Returns:
            Tuple (success, response_data)
        """
        if not self.is_enabled():
            return False, {'error': 'Orange Money non configuré'}
        
        access_token = self.get_access_token()
        if not access_token:
            return False, {'error': 'Impossible d\'obtenir le token d\'accès'}
        
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Construire les URLs de callback
            base_url = order_data.get('base_url', '')
            payment_data = {
                'merchant_key': self.config['merchant_key'],
                'currency': self.config['currency'],
                'order_id': order_data['order_id'],
                'amount': order_data['amount'],
                'return_url': f"{base_url}{order_data['return_url']}",
                'cancel_url': f"{base_url}{order_data['cancel_url']}",
                'notif_url': f"{base_url}{order_data['notif_url']}",
                'lang': self.config['language'],
                'reference': order_data.get('reference', 'SagaKore')
            }
            
            logger.info(f"Création de session de paiement pour la commande {order_data['order_id']}")
            response = self.session.post(
                self.config['webpayment_url'],
                headers=headers,
                json=payment_data
            )
            
            if response.status_code == 201:
                response_data = response.json()
                logger.info(f"Session de paiement créée: {response_data.get('pay_token', 'N/A')}")
                return True, response_data
            else:
                error_msg = f"Erreur création session: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, {'error': error_msg}
                
        except Exception as e:
            error_msg = f"Exception lors de la création de session: {str(e)}"
            logger.error(error_msg)
            return False, {'error': error_msg}
    
    def get_payment_url(self, pay_token: str) -> str:
        """
        Construit l'URL de paiement Orange Money
        
        Args:
            pay_token: Token de paiement reçu lors de la création de session
        
        Returns:
            URL complète de paiement
        """
        return f"{self.config['payment_url']}/payment/pay_token/{pay_token}"
    
    def check_transaction_status(self, order_id: str, amount: int, pay_token: str) -> Tuple[bool, Dict]:
        """
        Vérifie le statut d'une transaction Orange Money
        
        Args:
            order_id: ID de la commande
            amount: Montant en centimes
            pay_token: Token de paiement
        
        Returns:
            Tuple (success, status_data)
        """
        if not self.is_enabled():
            return False, {'error': 'Orange Money non configuré'}
        
        access_token = self.get_access_token()
        if not access_token:
            return False, {'error': 'Impossible d\'obtenir le token d\'accès'}
        
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            status_data = {
                'order_id': order_id,
                'amount': amount,
                'pay_token': pay_token
            }
            
            logger.info(f"Vérification du statut pour la commande {order_id}")
            response = self.session.post(
                self.config['status_url'],
                headers=headers,
                json=status_data
            )
            
            if response.status_code == 201:
                response_data = response.json()
                logger.info(f"Statut récupéré: {response_data.get('status', 'N/A')}")
                return True, response_data
            else:
                error_msg = f"Erreur vérification statut: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, {'error': error_msg}
                
        except Exception as e:
            error_msg = f"Exception lors de la vérification du statut: {str(e)}"
            logger.error(error_msg)
            return False, {'error': error_msg}
    
    def validate_webhook_notification(self, notification_data: Dict, notif_token: str) -> bool:
        """
        Valide une notification webhook Orange Money
        
        Args:
            notification_data: Données de la notification
            notif_token: Token de notification reçu
        
        Returns:
            True si la notification est valide
        """
        try:
            # Vérifier que le token de notification correspond
            expected_token = notification_data.get('notif_token')
            if not expected_token or expected_token != notif_token:
                logger.warning(f"Token de notification invalide: {notif_token} != {expected_token}")
                return False
            
            # Vérifier le statut
            status = notification_data.get('status')
            if status not in ['SUCCESS', 'FAILED']:
                logger.warning(f"Statut de notification invalide: {status}")
                return False
            
            logger.info(f"Notification webhook validée pour le statut: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la notification: {str(e)}")
            return False
    
    def format_amount(self, amount: float) -> int:
        """
        Convertit un montant en centimes pour Orange Money
        
        Args:
            amount: Montant en FCFA
        
        Returns:
            Montant en centimes
        """
        return int(amount * 100)
    
    def parse_amount(self, amount_cents: int) -> float:
        """
        Convertit un montant de centimes en FCFA
        
        Args:
            amount_cents: Montant en centimes
        
        Returns:
            Montant en FCFA
        """
        return amount_cents / 100


# Instance globale du service
orange_money_service = OrangeMoneyService()
