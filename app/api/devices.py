import traceback
from flask import Blueprint, jsonify, request, g
from sqlalchemy import select, and_
from app.database import engine
from app.db.models import Device
from datetime import datetime
import json

bp = Blueprint('devices', __name__, url_prefix='/devices')

@bp.route('/<id>', methods=['GET'])
def list_devices(id):
    try:
        with engine.connect() as conn:
            device = conn.execute(
                select(Device).where(
                    Device.id == id,
                )
            ).first()
            
            return jsonify(device._asdict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp.route('/', methods=['PUT'])
def register_device():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['platform', 'token']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # For web push, ensure token is stored as JSON string
        if data['platform'] == 'web':
            data['token'] = json.dumps(data['token'])
        
        # Create device record
        with engine.connect() as conn:
            # Check if device exists
            existing_device = conn.execute(
                select(Device).where(
                    and_(
                        Device.token == data['token'],
                        Device.platform == data['platform'],
                        Device.project_id == g.project_id
                    )
                )
            ).first()
            
            if existing_device:
                # If device exists, update user_id if provided
                if data.get('user_id') and data['user_id'] != existing_device.user_id:
                    result = conn.execute(
                        Device.__table__.update()
                        .where(
                            and_(
                                Device.token == data['token'],
                                Device.platform == data['platform'],
                                Device.project_id == g.project_id
                            )
                        )
                        .values(
                            user_id=data['user_id']
                        )
                        .returning(Device)
                    )
                    device = result.first()
                else:
                    device = existing_device
            else:
                # Insert new device
                device = Device(
                    project_id=g.project_id,
                    user_id=data.get('user_id'),
                    platform=data['platform'],
                    token=data['token']
                )
                result = conn.execute(Device.__table__.insert().returning(Device), device.__dict__)
                device = result.first()
            
            conn.commit()
            
            if not device:
                return jsonify({"error": "Failed to create/update device"}), 500
            
            # For web push, parse the token back to JSON
            device_dict = device._asdict()
            if device_dict['platform'] == 'web':
                device_dict['token'] = json.loads(device_dict['token'])
            
            return jsonify(device_dict), 200
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('/', methods=['GET'])
def get_devices():
    try:
        with engine.connect() as conn:
            # Build query with optional filters
            query = select(Device).where(Device.project_id == g.project_id)
            
            # Add user_id filter if provided
            user_id = request.args.get('user_id')
            if user_id:
                query = query.where(Device.user_id == user_id)
            
            # Add platform filter if provided
            platform = request.args.get('platform')
            if platform:
                query = query.where(Device.platform == platform)
            
            # Execute query
            devices = conn.execute(query).fetchall()
            
            # Convert to dict and handle web push tokens
            device_list = []
            for device in devices:
                device_dict = device._asdict()
                if device_dict['platform'] == 'web':
                    device_dict['token'] = json.loads(device_dict['token'])
                device_list.append(device_dict)
            
            return jsonify(device_list), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    try:
        with engine.connect() as conn:
            # Check if device exists
            device = conn.execute(
                select(Device).where(
                    and_(
                        Device.id == device_id,
                        Device.project_id == g.project_id
                    )
                )
            ).first()
            
            if not device:
                return jsonify({"error": "Device not found"}), 404
            
            # Delete device
            conn.execute(
                Device.__table__.delete().where(
                    and_(
                        Device.id == device_id,
                        Device.project_id == g.project_id
                    )
                )
            )
            conn.commit()
            
            return '', 204
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500 