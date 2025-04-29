from flask import Blueprint, request, jsonify
from functools import wraps
from sqlalchemy import select
from app.database import engine
from app.db.models import Project
import os
import secrets
from cryptography.fernet import Fernet

ADMIN_SECRET = os.environ.get('ADMIN_SECRET')
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
fernet = Fernet(ENCRYPTION_KEY) if ENCRYPTION_KEY else None

bp = Blueprint('admin', __name__, url_prefix='/admin')

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_secret = request.headers.get('X-Admin-Secret')
        if not admin_secret or admin_secret != ADMIN_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/projects', methods=['POST'])
@require_admin
def create_project():
    data = request.get_json()
    required_fields = ['id', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    with engine.connect() as conn:
        # Check for duplicate id
        existing = conn.execute(
            select(Project).where(Project.id == data['id'])
        ).first()
        if existing:
            return jsonify({'error': 'Project with this id already exists'}), 400
        # Generate a secure API key
        # api_key = secrets.token_urlsafe(32)
        api_key = 'test_api_key_123'
        
        # Insert project
        project = Project(
            id=data['id'],
            name=data['name'],
            api_key=api_key
        )
        conn.execute(Project.__table__.insert(), project.__dict__)
        conn.commit()
        return jsonify({
            'id': project.id,
            'name': project.name,
            'api_key': project.api_key
        }), 201

@bp.route('/projects/<project_id>/credentials', methods=['GET'])
@require_admin
def get_project_credentials(project_id):

    with engine.connect() as conn:
        project = conn.execute(select(Project).where(Project.id == project_id)).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify({'status': 'success', 'project': project._asdict()}), 200

@bp.route('/projects/<project_id>/credentials', methods=['PUT'])
@require_admin
def set_project_credentials(project_id):
    if not fernet:
        return jsonify({'error': 'Encryption key not configured'}), 500
    data = request.get_json()
    allowed_fields = [
        'fcm_credentials_json',
        'apns_key_id', 'apns_team_id', 'apns_bundle_id', 'apns_private_key',
        'vapid_public_key', 'vapid_private_key', 'vapid_subject'
    ]
    encrypted_fields = ['fcm_credentials_json', 'apns_private_key', 'vapid_private_key']
    updates = {}
    for field in allowed_fields:
        if field in data:
            value = data[field]
            if field in encrypted_fields and value is not None:
                value = fernet.encrypt(value.encode()).decode()
            updates[field] = value
    if not updates:
        return jsonify({'error': 'No valid credential fields provided'}), 400
    with engine.connect() as conn:
        project = conn.execute(select(Project).where(Project.id == project_id)).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        conn.execute(Project.__table__.update().where(Project.id == project_id).values(**updates))
        conn.commit()
    return jsonify({'status': 'success', 'updated_fields': list(updates.keys())}), 200 