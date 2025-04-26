from flask import Blueprint, jsonify, request, g
from supabase import create_client, Client
import os

bp = Blueprint('devices', __name__, url_prefix='/v1/devices')

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Devices API is running"})

@bp.route('/<user_id>', methods=['GET'])
def list_devices(user_id):
    try:
        response = supabase.table('devices').select('*').eq('user_id', user_id).eq('project_id', g.project_id).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<user_id>/<device_id>', methods=['PUT'])
def register_device(user_id, device_id):
    try:
        data = request.get_json()
        if not data or 'platform' not in data or 'token' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        # Check if device already exists
        response = supabase.table('devices').select('*').eq('user_id', user_id).eq('device_id', device_id).eq('project_id', g.project_id).execute()
        
        if response.data:
            # Update existing device
            response = supabase.table('devices').update({
                'platform': data['platform'],
                'token': data['token']
            }).eq('user_id', user_id).eq('device_id', device_id).eq('project_id', g.project_id).execute()
        else:
            # Create new device
            response = supabase.table('devices').insert({
                'user_id': user_id,
                'device_id': device_id,
                'platform': data['platform'],
                'token': data['token'],
                'project_id': g.project_id
            }).execute()

        return jsonify(response.data[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<user_id>/<device_id>', methods=['GET'])
def get_device(user_id, device_id):
    try:
        response = supabase.table('devices').select('*').eq('user_id', user_id).eq('device_id', device_id).eq('project_id', g.project_id).execute()
        
        if not response.data:
            return jsonify({"error": "Device not found"}), 404
            
        return jsonify(response.data[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<user_id>/<device_id>', methods=['DELETE'])
def delete_device(user_id, device_id):
    try:
        response = supabase.table('devices').delete().eq('user_id', user_id).eq('device_id', device_id).eq('project_id', g.project_id).execute()
        
        if not response.data:
            return jsonify({"error": "Device not found"}), 404
            
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500 