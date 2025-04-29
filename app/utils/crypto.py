from cryptography.fernet import Fernet
import os
from typing import Optional, Dict, Any

# Get encryption key from environment
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
fernet = Fernet(ENCRYPTION_KEY) if ENCRYPTION_KEY else None

def decrypt_project_credentials(project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely decrypt sensitive project credentials for worker usage.
    
    Args:
        project: Project dictionary containing encrypted credentials
        
    Returns:
        Dict with decrypted credentials. Original project dict is not modified.
        Non-encrypted fields are returned as-is.
    """
    if not fernet:
        raise ValueError("Encryption key not configured")
    
    # Fields that need decryption
    encrypted_fields = [
        'fcm_credentials_json',
        'apns_private_key',
        'vapid_private_key'
    ]
    
    # Create a copy to avoid modifying the original
    decrypted = project.copy()
    
    # Decrypt sensitive fields if they exist and are not None
    for field in encrypted_fields:
        if field in decrypted and decrypted[field] is not None:
            try:
                encrypted_value = decrypted[field]
                decrypted_value = fernet.decrypt(encrypted_value.encode()).decode()
                decrypted[field] = decrypted_value
            except Exception as e:
                raise ValueError(f"Failed to decrypt {field}: {str(e)}")
    
    return decrypted

def get_project_push_credentials(project_id: str) -> Dict[str, Any]:
    """
    Fetch and decrypt project credentials for push notification sending.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Dict containing decrypted credentials needed for push notifications
    """
    from app.database import engine
    from sqlalchemy import select
    from app.db.models import Project
    
    with engine.connect() as conn:
        # Fetch project with credentials
        project = conn.execute(
            select(Project).where(Project.id == project_id)
        ).first()
        
        if not project:
            raise ValueError(f"Project not found: {project_id}")
            
        # Convert to dict for easier handling
        project_dict = dict(project._mapping)
        
        # Decrypt credentials
        return decrypt_project_credentials(project_dict) 