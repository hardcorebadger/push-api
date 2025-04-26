from flask import Blueprint, jsonify, request, g
from supabase import create_client, Client
import os
from datetime import datetime

bp = Blueprint('preferences', __name__, url_prefix='/v1/preferences')

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Preferences API is running"})

@bp.route('/<userId>', methods=['GET'])
def get_user_preferences(userId):
    try:
        # Get user preferences
        response = supabase.table('preferences').select('*').eq('user_id', userId).eq('project_id', g.project_id).execute()
        
        if not response.data:
            return jsonify({"error": "User not found"}), 404
            
        prefs = response.data[0]
        
        # Get all user's devices
        devices_response = supabase.table('devices').select('id, device_id, platform').eq('user_id', userId).eq('project_id', g.project_id).execute()
        devices = devices_response.data
        
        # Get device preferences for all devices
        device_ids = [device['id'] for device in devices]
        device_prefs_response = supabase.table('device_preferences').select('*').in_('device_id', device_ids).execute()
        device_prefs_map = {pref['device_id']: pref for pref in device_prefs_response.data}
        
        # Format device preferences
        device_preferences = []
        for device in devices:
            device_prefs = device_prefs_map.get(device['id'], {'enabled': True, 'categories': {}})
            device_preferences.append({
                'deviceIdentifier': device['device_id'],
                'platform': device['platform'],
                'enabled': device_prefs['enabled'],
                'categories': device_prefs['categories']
            })
        
        # Format response
        response_data = {
            'enabled': prefs['enabled'],
            'categories': prefs['categories'],
            'devices': device_preferences
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<userId>', methods=['PUT'])
def update_user_preferences(userId):
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'enabled' not in data:
            return jsonify({"error": "Missing required field: enabled"}), 400
            
        # Prepare update data
        update_data = {
            'enabled': data['enabled'],
            'categories': data.get('categories', []),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Try to update existing preferences
        response = supabase.table('preferences').update(update_data).eq('user_id', userId).eq('project_id', g.project_id).execute()
        
        # If no rows were updated, create new preferences
        if not response.data:
            update_data['user_id'] = userId
            update_data['project_id'] = g.project_id
            response = supabase.table('preferences').insert(update_data).execute()
            
        prefs = response.data[0]
        
        # Format response
        response_data = {
            'enabled': prefs['enabled'],
            'categories': prefs['categories'],
            'updatedAt': prefs['updated_at']
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<userId>/<deviceIdentifier>', methods=['GET'])
def get_device_preferences(userId, deviceIdentifier):
    try:
        # First get the device ID
        device_response = supabase.table('devices').select('id').eq('user_id', userId).eq('device_id', deviceIdentifier).eq('project_id', g.project_id).single().execute()
        
        if not device_response.data:
            return jsonify({"error": "Device not found"}), 404
            
        device_id = device_response.data['id']
        
        # Get device preferences
        prefs_response = supabase.table('device_preferences').select('*').eq('device_id', device_id).execute()
        
        if not prefs_response.data:
            # Return default preferences if none exist
            return jsonify({
                'enabled': True,
                'categories': {}
            }), 200
            
        prefs = prefs_response.data[0]
        
        # Format response
        response_data = {
            'enabled': prefs['enabled'],
            'categories': prefs['categories']
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<userId>/<deviceIdentifier>', methods=['PUT'])
def update_device_preferences(userId, deviceIdentifier):
    try:
        data = request.get_json()
        
        # First get the device ID
        device_response = supabase.table('devices').select('id').eq('user_id', userId).eq('device_id', deviceIdentifier).eq('project_id', g.project_id).single().execute()
        
        if not device_response.data:
            return jsonify({"error": "Device not found"}), 404
            
        device_id = device_response.data['id']
        
        # Prepare update data
        update_data = {
            'enabled': data.get('enabled', True),
            'categories': data.get('categories', {}),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Try to update existing preferences
        response = supabase.table('device_preferences').update(update_data).eq('device_id', device_id).execute()
        
        # If no rows were updated, create new preferences
        if not response.data:
            update_data['device_id'] = device_id
            response = supabase.table('device_preferences').insert(update_data).execute()
            
        prefs = response.data[0]
        
        # Format response
        response_data = {
            'enabled': prefs['enabled'],
            'categories': prefs['categories'],
            'updatedAt': prefs['updated_at']
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 