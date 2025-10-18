import requests
import json
import logging
from django.conf import settings
from django.urls import reverse

# Get logger for payments
logger = logging.getLogger('chapa_payment')

class ChapaService:
    def __init__(self):
        self.secret_key = settings.CHAPA_SECRET_KEY
        self.base_url = settings.CHAPA_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        logger.info("ChapaService initialized")
    
    def initiate_payment(self, amount, email, first_name, last_name, tx_ref, 
                       return_url, currency='ETB', custom_title=None, custom_description=None):
        """
        Initiate payment with Chapa API
        """
        url = f"{self.base_url}/transaction/initialize"
        
        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "return_url": return_url,
            "customization": {
                "title": custom_title or "Property Booking Payment",
                "description": custom_description or "Secure payment for your property booking"
            }
        }
        
        # Log payment initiation attempt
        logger.info(f"🔗 Initiating Chapa payment", extra={
            'transaction_id': tx_ref,
            'amount': amount,
            'currency': currency,
            'email': email,
            'action': 'payment_initiation'
        })
        
        logger.debug(f"Chapa API Request Details", extra={
            'url': url,
            'payload': payload,
            'transaction_id': tx_ref
        })
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Log successful initiation
            logger.info(f"✅ Chapa payment initiated successfully", extra={
                'transaction_id': tx_ref,
                'checkout_url': data['data']['checkout_url'],
                'status': data['data']['status'],
                'action': 'payment_initiation_success'
            })
            
            return {
                'success': True,
                'checkout_url': data['data']['checkout_url'],
                'transaction_id': data['data']['tx_ref'],
                'response_data': data
            }
            
        except requests.exceptions.RequestException as e:
            # Log initiation failure
            logger.error(f"❌ Chapa payment initiation failed", extra={
                'transaction_id': tx_ref,
                'error': str(e),
                'response_status': getattr(e.response, 'status_code', None),
                'response_text': getattr(e.response, 'text', ''),
                'action': 'payment_initiation_failed'
            })
            
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to initiate payment'
            }
    
    def verify_payment(self, transaction_id):
        """
        Verify payment status with Chapa API
        """
        url = f"{self.base_url}/transaction/verify/{transaction_id}"
        
        # Log verification attempt
        logger.info(f"🔍 Verifying Chapa payment", extra={
            'transaction_id': transaction_id,
            'action': 'payment_verification'
        })
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Log verification result
            logger.info(f"📊 Chapa payment verification completed", extra={
                'transaction_id': transaction_id,
                'status': data['data']['status'],
                'amount': data['data']['amount'],
                'currency': data['data']['currency'],
                'action': 'payment_verification_success'
            })
            
            logger.debug(f"Chapa verification response", extra={
                'transaction_id': transaction_id,
                'full_response': data,
                'action': 'payment_verification_details'
            })
            
            return {
                'success': True,
                'status': data['data']['status'],
                'payment_data': data['data'],
                'response_data': data
            }
            
        except requests.exceptions.RequestException as e:
            # Log verification failure
            logger.error(f"❌ Chapa payment verification failed", extra={
                'transaction_id': transaction_id,
                'error': str(e),
                'response_status': getattr(e.response, 'status_code', None),
                'action': 'payment_verification_failed'
            })
            
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to verify payment'
            }
