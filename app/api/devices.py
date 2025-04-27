from flask import Blueprint, jsonify, request, g
from sqlalchemy import select, and_
from app.database import engine
from app.db.models import Device
from datetime import datetime
import json

bp = Blueprint('devices', __name__, url_prefix='/devices')

@bp.route('/<user_id>', methods=['GET'])
def list_devices(user_id):
    try:
        with engine.connect() as conn:
            devices = conn.execute(
                select(Device).where(
                    and_(
                        Device.user_id == user_id,
                        Device.project_id == g.project_id
                    )
                )
            ).fetchall()
            
            return jsonify([device._asdict() for device in devices]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<user_id>/<device_id>', methods=['PUT'])
def register_device(user_id, device_id):
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
                        Device.user_id == user_id,
                        Device.device_id == device_id,
                        Device.project_id == g.project_id
                    )
                )
            ).first()
            
            if existing_device:
                # Update existing device
                result = conn.execute(
                    Device.__table__.update()
                    .where(
                        and_(
                            Device.user_id == user_id,
                            Device.device_id == device_id,
                            Device.project_id == g.project_id
                        )
                    )
                    .values(
                        platform=data['platform'],
                        token=data['token'],
                        updated_at=datetime.utcnow()
                    )
                )
            else:
                # Insert new device
                device = Device(
                    project_id=g.project_id,
                    user_id=user_id,
                    device_id=device_id,
                    platform=data['platform'],
                    token=data['token']
                )
                result = conn.execute(Device.__table__.insert(), device.__dict__)
            
            conn.commit()
            
            # Get the device to return
            device = conn.execute(
                select(Device).where(
                    and_(
                        Device.user_id == user_id,
                        Device.device_id == device_id,
                        Device.project_id == g.project_id
                    )
                )
            ).first()
            
            if not device:
                return jsonify({"error": "Failed to create/update device"}), 500
            
            # For web push, parse the token back to JSON
            device_dict = device._asdict()
            if device_dict['platform'] == 'web':
                device_dict['token'] = json.loads(device_dict['token'])
            
            return jsonify(device_dict), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<user_id>/<device_id>', methods=['GET'])
def get_device(user_id, device_id):
    try:
        with engine.connect() as conn:
            device = conn.execute(
                select(Device).where(
                    and_(
                        Device.user_id == user_id,
                        Device.device_id == device_id,
                        Device.project_id == g.project_id
                    )
                )
            ).first()
            
            if not device:
                return jsonify({"error": "Device not found"}), 404
                
            return jsonify(device._asdict()), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<user_id>/<device_id>', methods=['DELETE'])
def delete_device(user_id, device_id):
    try:
        with engine.connect() as conn:
            # Check if device exists
            device = conn.execute(
                select(Device).where(
                    and_(
                        Device.user_id == user_id,
                        Device.device_id == device_id,
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
                        Device.user_id == user_id,
                        Device.device_id == device_id,
                        Device.project_id == g.project_id
                    )
                )
            )
            conn.commit()
            
            return '', 204
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500 