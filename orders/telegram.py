# utils/telegram.py
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_telegram_message(message: str):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    if not token or not chat_id:
        logger.error("Telegram credentials missing in settings")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response_data = response.json()
        
        if not response_data.get('ok'):
            error_msg = f"Telegram error ({response.status_code}): {response_data.get('description')}"
            logger.error(error_msg)
            
            # Specific error handling
            if response_data.get('error_code') == 403:
                logger.error("Bot was blocked by user or missing permissions")
            elif response_data.get('error_code') == 400:
                logger.error(f"Invalid chat ID: {chat_id}")
                
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram connection failed: {str(e)}")
        return False