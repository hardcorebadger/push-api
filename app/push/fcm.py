import json
from firebase_admin import messaging, credentials, initialize_app, get_app

def send_android_push(device, message, project):
    try:
        
        credentials_json = json.loads(project['fcm_credentials_json'])

        # Use a unique app name per credentials to avoid duplicate initialization
        app_name = credentials_json.get('project_id', 'default')
        try:
            cred = credentials.Certificate(credentials_json)
            initialize_app(cred, name=app_name)
        except ValueError:
            # App already initialized
            pass

        # Create notification message
        message = messaging.Message(
            notification=messaging.Notification(
                title=message.title,
                body=message.body
            ),
            data={
                'category': message.category or '',
                'click_action': 'FLUTTER_NOTIFICATION_CLICK'
            },
            token=device.token
        )

        try:
        
            # Send notification
            response = messaging.send(message, app=get_app(app_name))
            
            return 'delivered', response.status_code
        
        except Exception as e:
            print(f"Error sending Android push TODO check for invalid token")
            return 'failed', str(e)
        
    except Exception as e:
        return 'error', str(e)