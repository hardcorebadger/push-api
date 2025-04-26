from flask import Flask, request, jsonify, g
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure app
    app.config['SUPABASE_URL'] = os.getenv('SUPABASE_URL')
    app.config['SUPABASE_KEY'] = os.getenv('SUPABASE_KEY')
    app.config['SUPABASE_SERVICE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY')
    
    # Initialize Supabase client
    supabase: Client = create_client(
        app.config['SUPABASE_URL'],
        app.config['SUPABASE_SERVICE_KEY']
    )
    
    # API Key authentication middleware
    @app.before_request
    def authenticate():
        # Skip authentication for health check endpoints
        if request.endpoint and 'health_check' in request.endpoint:
            return
            
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "No API key provided"}), 401
            
        # Check if the Authorization header starts with "Bearer "
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid API key format"}), 401
            
        api_key = auth_header.split(' ')[1]
        
        # Look up project by API key
        try:
            response = supabase.table('projects').select('id').eq('api_key', api_key).execute()
            if not response.data:
                return jsonify({"error": "Invalid API key"}), 403
                
            # Store project_id in Flask's g object for use in routes
            g.project_id = response.data[0]['id']
        except Exception as e:
            return jsonify({"error": "Database error"}), 500
    
    # Register blueprints
    from app.api import devices, messages, preferences
    app.register_blueprint(devices.bp)
    app.register_blueprint(messages.bp)
    app.register_blueprint(preferences.bp)
    
    return app 