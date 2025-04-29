from flask import Flask, g, request, jsonify
from dotenv import load_dotenv
from functools import wraps
from sqlalchemy import select
from app.database import engine
from app.db.models import Project
from flask_cors import CORS
import os
from flask import Blueprint
import secrets
from cryptography.fernet import Fernet

load_dotenv()

ADMIN_SECRET = os.environ.get('ADMIN_SECRET')
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
fernet = Fernet(ENCRYPTION_KEY) if ENCRYPTION_KEY else None

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:8000"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }},
         expose_headers=["Content-Type", "Authorization"])

    # Register blueprints
    from app.api import devices, messages, admin
    app.register_blueprint(devices.bp)
    app.register_blueprint(messages.bp)
    app.register_blueprint(admin.bp)
    
    @app.before_request
    def authenticate():
        # Skip authentication for OPTIONS requests
        if request.method == 'OPTIONS':
            return

        # Skip authentication for admin routes
        if request.path.startswith('/admin'):
            return

        # Get API key from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        api_key = auth_header.split(' ')[1]

        # Look up project by API key
        with engine.connect() as conn:
            project = conn.execute(
                select(Project).where(Project.api_key == api_key)
            ).first()

            if not project:
                return jsonify({"error": "Invalid API key"}), 401

            # Store project ID in g for use in routes
            g.project_id = project.id
    
    def require_admin(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            admin_secret = request.headers.get('X-Admin-Secret')
            if not admin_secret or admin_secret != ADMIN_SECRET:
                return jsonify({'error': 'Unauthorized'}), 401
            return f(*args, **kwargs)
        return decorated_function
    
  
    
    return app 