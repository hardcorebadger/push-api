from flask import Blueprint, jsonify, request, g
from sqlalchemy import select, and_
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
        required_fields = ['userId', 'title', 'body']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create message record
        with engine.connect() as conn:
            # Insert message
            message = Message(
                user_id=data['userId'],
                title=data['title'],
                body=data['body'],
                category=data.get('category'),
                icon=data.get('icon'),
                action_url=data.get('action_url'),
                project_id=g.project_id
            )
            result = conn.execute(Message.__table__.insert(), message.__dict__)
            conn.commit()
            
            # Get the inserted message to get its ID and timestamps
            message = conn.execute(
                select(Message).where(
                    and_(
                        Message.user_id == data['userId'],
                        Message.title == data['title'],
                        Message.project_id == g.project_id
                    )
                )
            ).first()
            
            if not message:
                return jsonify({"error": "Failed to create message"}), 500
            
            # Get target devices
            devices_query = select(Device).where(
                and_(
                    Device.user_id == data['userId'],
                    Device.project_id == g.project_id
                )
            )
            
            # Filter by platform if specified
            if 'platform' in data:
                devices_query = devices_query.where(Device.platform == data['platform'])
                
            # Filter by device identifier if specified
            if 'deviceIdentifier' in data:
                devices_query = devices_query.where(Device.device_id == data['deviceIdentifier'])
                
            devices = conn.execute(devices_query).fetchall()
            
            # Fetch project VAPID keys once
            project = conn.execute(
                select(Project).where(Project.id == g.project_id)
            ).first()
            project_vapid = project._asdict() if project else {}

            # Store device info in Redis and queue tasks
            for device in devices:
                # Store device info in Redis
                device_key = f"device:{device.device_id}"
                redis_client.hset(device_key, mapping={
                    'token': device.token,
                    'platform': device.platform,
                    'user_id': device.user_id,
                    'project_id': str(device.project_id)
                })
                
                # Queue task, including VAPID keys for web devices, icon, and action_url
                task = {
                    'message_id': str(message.id),
                    'device_id': device.device_id,
                    'user_id': device.user_id,
                    'project_id': str(device.project_id),
                    'title': message.title,
                    'body': message.body,
                    'category': message.category,
                    'icon': message.icon,
                    'action_url': message.action_url
                }
                if device.platform == 'web':
                    task['vapid_public_key'] = project_vapid.get('vapid_public_key')
                    task['vapid_private_key'] = project_vapid.get('vapid_private_key')
                    task['vapid_subject'] = project_vapid.get('vapid_subject')
                redis_client.lpush('push_tasks', json.dumps(task))
            
            # Format response
            response_data = {
                'id': str(message.id),
                'userId': message.user_id,
                'title': message.title,
                'body': message.body,
                'category': message.category,
                'icon': message.icon,
                'action_url': message.action_url,
                'createdAt': message.created_at,
                'devices': [{
                    'deviceIdentifier': device.device_id,
                    'platform': device.platform,
                    'status': 'pending'
                } for device in devices]
            }
            
            # Only include platform and deviceIdentifier if they were specified
            if 'platform' in data:
                response_data['platform'] = data['platform']
            if 'deviceIdentifier' in data:
                response_data['deviceIdentifier'] = data['deviceIdentifier']
            
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
                    'title': message_dict['title'],
                    'body': message_dict['body'],
                    'category': message_dict.get('category'),
                    'createdAt': message_dict['created_at'],
                    'devices': []  # Devices will be handled by Redis/worker
                })
            
            # Get total count
            count_query = select(Message).where(Message.project_id == g.project_id)
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
                'userId': message_dict['user_id'],
                'title': message_dict['title'],
                'body': message_dict['body'],
                'category': message_dict.get('category'),
                'createdAt': message_dict['created_at'],
                'devices': []  # Devices will be handled by Redis/worker
            }
            
            return jsonify(response_data), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500 