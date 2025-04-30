from pywebpush import webpush, WebPushException
import json
from app.db.models import Device, Message
from typing import Dict, Any

def send_web_push(device: Device, message: Message, project: Dict[str, Any]):
    try:
        vapid_private_key = project['vapid_private_key']
        vapid_subject = project['vapid_subject']
        subscription_info = json.loads(device.token)

        # Create notification payload
        payload = {
            'title': message.title,
            'body': message.body,
            'category': message.category,
            'icon': message.icon,
            'action_url': message.action_url
        }
        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        
        # VAPID claims - use the endpoint's origin as the audience
        vapid_claims = {
            "sub": vapid_subject,  
        }

        try:
        
            # Send notification
            response = webpush(
                subscription_info=subscription_info,
                data=payload_json,
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims,
                content_encoding='aes128gcm'
            )

            print(f"Web push sent successfully: {response.status_code}")
            
            return 'delivered', response.status_code
            
        except WebPushException as e:
            print(f"Error sending web push: {str(e)}")
            print(e.response.status_code)
            
            if e.response.status_code == 410:
                return 'invalid', str(e)

            return 'failed', str(e)

    except Exception as e:
        return 'error', str(e)
