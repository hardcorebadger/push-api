import asyncio
from uuid import uuid4
from aioapns import APNs, NotificationRequest, PushType

async def send_ios_push(device, message, project):
    try:
        apns_key_id = project['apns_key_id']
        apns_team_id = project['apns_team_id']
        apns_bundle_id = project['apns_bundle_id']
        apns_private_key = project['apns_private_key']
        

        apns_key_client = APNs(
            key=apns_private_key,
            key_id=apns_key_id,
            team_id=apns_team_id,
            topic=apns_bundle_id,  # Bundle ID
            use_sandbox=True,
        )

        

        request = NotificationRequest(
            device_token=device.token,
            message = {
                "aps": {
                    "alert": {
                        "title": message.title,
                        "body": message.body
                    },
                    "badge": "1",
                }, 
                "action_url": message.action_url
            },
            notification_id=str(uuid4()),  # optional
            time_to_live=3,                # optional
            push_type=PushType.ALERT,      # optional
        )

        try:

            result = await apns_key_client.send_notification(request)
            return 'delivered', result.status_code

        except Exception as e:
            print("Failed sending ios push, TODO check for invalid token")
            return 'failed', str(e)

    except Exception as e:
        return 'error', str(e)