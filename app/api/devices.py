from flask import Blueprint, jsonify, request, g
from sqlalchemy import select, and_
from app.database import engine
from app.db.models import Device

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
        if not data or 'platform' not in data or 'token' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        with engine.connect() as conn:
            # Check if device already exists
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
                conn.execute(
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
                        token=data['token']
                    )
                )
            else:
                # Create new device
                device = Device(
                    user_id=user_id,
                    device_id=device_id,
                    platform=data['platform'],
                    token=data['token'],
                    project_id=g.project_id
                )
                conn.execute(Device.__table__.insert(), device.__dict__)
            
            conn.commit()
            
            # Get the updated/created device
            device = conn.execute(
                select(Device).where(
                    and_(
                        Device.user_id == user_id,
                        Device.device_id == device_id,
                        Device.project_id == g.project_id
                    )
                )
            ).first()
            
            return jsonify(device._asdict()), 200
            
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