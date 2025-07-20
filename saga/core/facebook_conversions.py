"""
Service pour l'API Conversions Facebook
"""
import requests
import hashlib
import time
import logging
from django.conf import settings
from .models import SiteConfiguration

logger = logging.getLogger(__name__)

class FacebookConversionsAPI:
    """
    Service pour envoyer des événements de conversion à Facebook
    """
    def __init__(self):
        try:
            config = SiteConfiguration.get_config()
            self.pixel_id = config.facebook_pixel_id
            self.access_token = config.facebook_access_token
        except Exception as e:
            logger.warning(f"Impossible de récupérer la configuration Facebook: {e}")
            self.pixel_id = None
            self.access_token = None
        
        if not self.pixel_id or not self.access_token:
            logger.warning("Facebook Pixel ID ou Access Token non configuré dans SiteConfiguration")
            return
            
        self.api_url = f"https://graph.facebook.com/v18.0/{self.pixel_id}/events"
    
    def send_event(self, event_name, user_data=None, custom_data=None, event_source_url=None):
        """
        Envoie un événement de conversion à Facebook
        """
        if not self.pixel_id or not self.access_token:
            logger.warning("Facebook Conversions API non configurée")
            return None
            
        try:
            event_data = {
                "event_name": event_name,
                "event_time": int(time.time()),
                "action_source": "website",
                "event_source_url": event_source_url or "https://bolibana.com",
            }
            
            if user_data:
                event_data["user_data"] = self._hash_user_data(user_data)
            
            if custom_data:
                event_data["custom_data"] = custom_data
            
            payload = {
                "data": [event_data],
                "access_token": self.access_token
            }
            
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Événement Facebook envoyé: {event_name}")
                return response.json()
            else:
                logger.error(f"Erreur Facebook: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Exception Facebook: {str(e)}")
            return None
    
    def _hash_user_data(self, user_data):
        """Hache les données utilisateur"""
        hashed_data = {}
        
        if user_data.get("email"):
            hashed_data["em"] = hashlib.sha256(
                user_data["email"].lower().encode('utf-8')
            ).hexdigest()
        
        if user_data.get("phone"):
            phone = user_data["phone"].replace(" ", "").replace("-", "").replace("+", "")
            hashed_data["ph"] = hashlib.sha256(phone.encode('utf-8')).hexdigest()
        
        return hashed_data
    
    def send_purchase_event(self, user_data, amount, currency="XOF", content_name=None):
        """Événement d'achat"""
        custom_data = {
            "value": amount,
            "currency": currency,
            "content_type": "service"
        }
        
        if content_name:
            custom_data["content_name"] = content_name
        
        return self.send_event("Purchase", user_data, custom_data)
    
    def send_lead_event(self, user_data, content_name=None):
        """Événement de lead"""
        custom_data = {"content_type": "service"}
        
        if content_name:
            custom_data["content_name"] = content_name
        
        return self.send_event("Lead", user_data, custom_data)
    
    def send_pageview_event(self, user_data=None, content_name=None, content_category=None):
        """Événement de visite de page"""
        custom_data = {"content_type": "website"}
        
        if content_name:
            custom_data["content_name"] = content_name
        
        if content_category:
            custom_data["content_category"] = content_category
        
        return self.send_event("PageView", user_data, custom_data)
    
    def send_view_content_event(self, user_data, content_name=None, content_category=None, value=None, currency="XOF"):
        """Événement de consultation de contenu"""
        custom_data = {"content_type": "product"}
        
        if content_name:
            custom_data["content_name"] = content_name
        
        if content_category:
            custom_data["content_category"] = content_category
        
        if value:
            custom_data["value"] = value
            custom_data["currency"] = currency
        
        return self.send_event("ViewContent", user_data, custom_data)
    
    def send_search_event(self, user_data, search_string, content_category=None):
        """Événement de recherche"""
        custom_data = {
            "search_string": search_string,
            "content_type": "product"
        }
        
        if content_category:
            custom_data["content_category"] = content_category
        
        return self.send_event("Search", user_data, custom_data)
    
    def send_initiate_checkout_event(self, user_data, value=None, currency="XOF", content_name=None, content_category=None):
        """Événement d'initiation de checkout"""
        custom_data = {"content_type": "product"}
        
        if value:
            custom_data["value"] = value
            custom_data["currency"] = currency
        
        if content_name:
            custom_data["content_name"] = content_name
        
        if content_category:
            custom_data["content_category"] = content_category
        
        return self.send_event("InitiateCheckout", user_data, custom_data)
    
    def send_add_to_cart_event(self, user_data, value=None, currency="XOF", content_name=None, content_category=None, content_ids=None):
        """Événement d'ajout au panier"""
        custom_data = {"content_type": "product"}
        
        if value:
            custom_data["value"] = value
            custom_data["currency"] = currency
        
        if content_name:
            custom_data["content_name"] = content_name
        
        if content_category:
            custom_data["content_category"] = content_category
        
        if content_ids:
            custom_data["content_ids"] = content_ids
        
        return self.send_event("AddToCart", user_data, custom_data)

# Instance globale
facebook_conversions = FacebookConversionsAPI() 