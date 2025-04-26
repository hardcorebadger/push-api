from flask import Blueprint, jsonify, request, g
from supabase import create_client, Client
import os
from datetime import datetime
import uuid
import traceback

bp = Blueprint('messages', __name__, url_prefix='/v1/messages')

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Messages API is running"})

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
        message_data = {
            'user_id': data['userId'],
            'title': data['title'],
            'body': data['body'],
            'category': data.get('category'),
            'project_id': g.project_id
        }
        
        message_response = supabase.table('messages').insert(message_data).execute()
        message = message_response.data[0]
        message_id = message['id']
        
        # Get user preferences
        user_prefs_response = supabase.table('preferences').select('*').eq('user_id', data['userId']).eq('project_id', g.project_id).execute()
        user_prefs = user_prefs_response.data[0] if user_prefs_response.data else {'enabled': True, 'categories': []}
        
        # Check user-level preferences
        if not user_prefs['enabled']:
            return jsonify({
                'id': str(message_id),
                'userId': message['user_id'],
                'title': message['title'],
                'body': message['body'],
                'category': message.get('category'),
                'createdAt': message['created_at'],
                'devices': []
            }), 200
            
        # If message has a category, check if user has it enabled
        if message.get('category') and message['category'] not in user_prefs['categories']:
            return jsonify({
                'id': str(message_id),
                'userId': message['user_id'],
                'title': message['title'],
                'body': message['body'],
                'category': message.get('category'),
                'createdAt': message['created_at'],
                'devices': []
            }), 200
        
        # Get target devices
        devices_query = supabase.table('devices').select('*').eq('user_id', data['userId']).eq('project_id', g.project_id)
        
        # Filter by platform if specified
        if 'platform' in data:
            devices_query = devices_query.eq('platform', data['platform'])
            
        # Filter by device identifier if specified
        if 'deviceIdentifier' in data:
            devices_query = devices_query.eq('device_id', data['deviceIdentifier'])
            
        devices_response = devices_query.execute()
        devices = devices_response.data
        
        # Get device preferences for all devices
        device_ids = [device['id'] for device in devices]
        device_prefs_response = supabase.table('device_preferences').select('*').in_('device_id', device_ids).execute()
        device_prefs_map = {pref['device_id']: pref for pref in device_prefs_response.data}
        
        # Create send records for each device that passes preferences check
        sends = []
        for device in devices:
            device_prefs = device_prefs_map.get(device['id'], {'enabled': True, 'categories': []})
            
            # Skip if device preferences are disabled
            if not device_prefs['enabled']:
                continue
                
            # Skip if message has a category and device doesn't have it enabled
            if message.get('category') and message['category'] not in device_prefs['categories']:
                continue
                
            send_data = {
                'message_id': message_id,
                'device_id': device['id'],
                'platform': device['platform'],
                'status': 'pending',  # Initial status
                'created_at': datetime.utcnow().isoformat()
            }
            sends.append(send_data)
            
        if sends:
            sends_response = supabase.table('sends').insert(sends).execute()
            sends = sends_response.data
        
        # Format response
        response_data = {
            'id': str(message_id),
            'userId': message['user_id'],
            'title': message['title'],
            'body': message['body'],
            'platform': data.get('platform'),
            'deviceIdentifier': data.get('deviceIdentifier'),
            'category': message.get('category'),
            'data': data.get('data'),
            'createdAt': message['created_at'],
            'devices': [{
                'deviceIdentifier': device['device_id'],
                'platform': device['platform'],
                'status': 'pending',
                'deliveredAt': None,
                'error': None
            } for device in devices if device['id'] in [send['device_id'] for send in sends]]
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('', methods=['GET'])
def list_messages():
    try:
        # Start with base query
        query = supabase.table('messages').select('*, sends(*)').eq('project_id', g.project_id)
        
        # Apply filters from query parameters
        if request.args.get('userId'):
            query = query.eq('user_id', request.args.get('userId'))
            
        if request.args.get('platform'):
            query = query.eq('sends.platform', request.args.get('platform'))
            
        if request.args.get('deviceIdentifier'):
            # Join with devices to filter by device_id
            query = query.eq('sends.device_id', request.args.get('deviceIdentifier'))
            
        if request.args.get('category'):
            query = query.eq('category', request.args.get('category'))
            
        if request.args.get('status'):
            query = query.eq('sends.status', request.args.get('status'))
        
        # Apply pagination
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        response = query.execute()
        messages = response.data
        
        # Format response
        formatted_messages = []
        for message in messages:
            sends = message.pop('sends', [])
            formatted_messages.append({
                'id': str(message['id']),
                'userId': message['user_id'],
                'title': message['title'],
                'body': message['body'],
                'category': message.get('category'),
                'createdAt': message['created_at'],
                'devices': [{
                    'deviceIdentifier': send.get('device_id'),
                    'platform': send.get('platform'),
                    'status': send.get('status'),
                    'deliveredAt': send.get('delivered_at'),
                    'error': send.get('error')
                } for send in sends]
            })
        
        # Get total count
        count_response = supabase.table('messages').select('id', count='exact').eq('project_id', g.project_id).execute()
        total = count_response.count
        
        return jsonify({
            'messages': formatted_messages,
            'total': total
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<id>', methods=['GET'])
def get_message(id):
    try:
        # Get message with its sends
        response = supabase.table('messages').select('*, sends(*)').eq('id', id).eq('project_id', g.project_id).single().execute()
        
        if not response.data:
            return jsonify({"error": "Message not found"}), 404
            
        message = response.data
        sends = message.pop('sends', [])
        
        # Format response
        response_data = {
            'id': str(message['id']),
            'userId': message['user_id'],
            'title': message['title'],
            'body': message['body'],
            'category': message.get('category'),
            'createdAt': message['created_at'],
            'devices': [{
                'deviceIdentifier': send.get('device_id'),
                'platform': send.get('platform'),
                'status': send.get('status'),
                'deliveredAt': send.get('delivered_at'),
                'error': send.get('error')
            } for send in sends]
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 