from flask import Blueprint, jsonify, request, g
from sqlalchemy import delete, select, and_
from app.database import engine
from app.db.models import Message, Device, Project
from app.redis import redis_client
from datetime import datetime
import traceback
import json

bp = Blueprint('messages', __name__, url_prefix='/messages')

@bp.route('', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'body']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create message record
        with engine.connect() as conn:
            # Insert message
            message = Message(
                user_id=data.get('userId'),  # Make user_id optional
                platform=data.get('platform'),
                title=data['title'],
                body=data['body'],
                icon=data.get('icon'),
                action_url=data.get('action_url'),
                project_id=g.project_id
            )
            result = conn.execute(Message.__table__.insert().returning(Message), message.__dict__)
            message = result.first()
            conn.commit()
            
            if not message:
                return jsonify({"error": "Failed to create message"}), 500
            
            # Get target devices
            devices_query = select(Device).where(Device.project_id == g.project_id)
            
            # Add user_id filter if specified
            if 'userId' in data:
                devices_query = devices_query.where(Device.user_id == data['userId'])
                
            # Filter by platform if specified
            if 'platform' in data:
                devices_query = devices_query.where(Device.platform == data['platform'])
                
            # Filter by device identifier if specified
            if 'device_id' in data:
                devices_query = devices_query.where(Device.id == data['device_id'])
                
            devices = conn.execute(devices_query).fetchall()
            
            if not devices:
                return jsonify({"error": "No matching devices found"}), 404
            
            # Fetch project credentials
            project_query = conn.execute(
                select(Project).where(Project.id == g.project_id)
            ).first()
            project = project_query._asdict() if project_query else {}
            # project = decrypt_project_credentials(project) #decrypt on th worker

            # Queue tasks for each device
            for device in devices:
                task_data = {
                    'project_id': str(g.project_id),
                    'message_id': str(message.id),
                    'device_id': str(device.id),
                    'platform': device.platform,
                    'token': device.token,
                    'title': message.title,
                    'body': message.body,
                    'action_url': message.action_url,
                    'icon': message.icon
                }

                # Add platform-specific credentials
                if device.platform == 'ios':
                    task_data.update({
                        'apns_key_id': project.get('apns_key_id'),
                        'apns_team_id': project.get('apns_team_id'),
                        'apns_bundle_id': project.get('apns_bundle_id'),
                        'apns_private_key': project.get('apns_private_key')
                    })
                elif device.platform == 'android':
                    task_data.update({
                        'fcm_credentials_json': project.get('fcm_credentials_json')
                    })
                elif device.platform == 'web':
                    task_data.update({
                        'vapid_private_key': project.get('vapid_private_key'),
                        'vapid_subject': project.get('vapid_subject')
                    })

                # Queue the task in Redis
                redis_client.lpush('push_tasks', json.dumps(task_data))
            
            # Format response
            response_data = {
                'id': str(message.id),
                'title': message.title,
                'body': message.body,
                'icon': message.icon,
                'action_url': message.action_url,
                'createdAt': message.created_at,
                'devices': [device._asdict() for device in devices]
            }
            
            # Only include optional fields if they were specified
            if 'userId' in data:
                response_data['userId'] = data['userId']
            if 'platform' in data:
                response_data['platform'] = data['platform']
            if 'device_id' in data:
                response_data['device_id'] = data['device_id']
            
            return jsonify(response_data), 200
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('', methods=['GET'])
def list_messages():
    try:
        with engine.connect() as conn:
            # Start with base query
            query = select(Message).where(Message.project_id == g.project_id)
            
            # Apply filters from query parameters
            if request.args.get('userId'):
                query = query.where(Message.user_id == request.args.get('userId'))
                
            if request.args.get('platform'):
                query = query.where(Message.platform == request.args.get('platform'))
                
            if request.args.get('deviceId'):
                # Join with devices table to filter by device ID
                query = query.where(Message.device_id == request.args.get('deviceId'))
                
            if request.args.get('category'):
                query = query.where(Message.category == request.args.get('category'))
            
            # Apply pagination
            limit = int(request.args.get('limit', 10))
            offset = int(request.args.get('offset', 0))
            query = query.limit(limit).offset(offset)
            
            # Execute query
            messages = conn.execute(query).fetchall()
            
            # Format response
            formatted_messages = []
            for message in messages:
                message_dict = message._asdict()
                formatted_messages.append({
                    'id': str(message_dict['id']),
                    'userId': message_dict['user_id'],
                    'platform': message_dict.get('platform'),
                    'deviceId': str(message_dict['device_id']) if message_dict.get('device_id') else None,
                    'title': message_dict['title'],
                    'body': message_dict['body'],
                    'category': message_dict.get('category'),
                    'createdAt': message_dict['created_at']
                })
            
            # Get total count with same filters
            count_query = select(Message).where(Message.project_id == g.project_id)
            if request.args.get('userId'):
                count_query = count_query.where(Message.user_id == request.args.get('userId'))
            if request.args.get('platform'):
                count_query = count_query.where(Message.platform == request.args.get('platform'))
            if request.args.get('deviceId'):
                count_query = count_query.where(Message.device_id == request.args.get('deviceId'))
            if request.args.get('category'):
                count_query = count_query.where(Message.category == request.args.get('category'))
            
            total = len(conn.execute(count_query).fetchall())
            
            return jsonify({
                'messages': formatted_messages,
                'total': total
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<id>', methods=['GET'])
def get_message(id):
    try:
        with engine.connect() as conn:
            # Get message
            message = conn.execute(
                select(Message).where(
                    and_(
                        Message.id == id,
                        Message.project_id == g.project_id
                    )
                )
            ).first()
            
            if not message:
                return jsonify({"error": "Message not found"}), 404
                
            message_dict = message._asdict()
            
            # Format response
            response_data = {
                'id': str(message_dict['id']),
                'userId': message_dict.get('user_id'),
                'title': message_dict['title'],
                'body': message_dict['body'],
                'createdAt': message_dict['created_at'],
                'devices': []  # Devices will be handled by Redis/worker
            }
            
            return jsonify(response_data), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500 