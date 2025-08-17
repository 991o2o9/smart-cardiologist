import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting user data"""
    
    def __init__(self):
        # Generate encryption key based on SECRET_KEY
        self._key = self._generate_key()
        self._cipher_suite = Fernet(self._key)
    
    def _generate_key(self) -> bytes:
        """Generate encryption key based on SECRET_KEY"""
        # Use SECRET_KEY as salt for key generation
        salt = settings.SECRET_KEY.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data"""
        try:
            if not data:
                return data
            
            encrypted_data = self._cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise ValueError("Error encrypting data")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        try:
            if not encrypted_data:
                return encrypted_data
            
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            # Decrypt
            decrypted_data = self._cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise ValueError("Error decrypting data")
    
    def encrypt_medical_data(self, data: dict) -> dict:
        """Encrypt medical data"""
        encrypted_data = {}
        
        # List of fields that need to be encrypted
        sensitive_fields = [
            'symptoms', 'ai_response', 'risk', 'risk_prediction',
            'pulse', 'age', 'sex', 'cp', 'trestbps', 'chol',
            'fbs', 'restecg', 'thalach', 'exang', 'oldpeak',
            'slope', 'ca', 'thal', 'probability'
        ]
        
        for key, value in data.items():
            if key in sensitive_fields and value is not None:
                if isinstance(value, (int, float)):
                    # For numeric values convert to string
                    encrypted_data[key] = self.encrypt_data(str(value))
                elif isinstance(value, str):
                    encrypted_data[key] = self.encrypt_data(value)
                else:
                    encrypted_data[key] = value
            else:
                encrypted_data[key] = value
        
        return encrypted_data
    
    def decrypt_medical_data(self, data: dict) -> dict:
        """Decrypt medical data"""
        decrypted_data = {}
        
        # List of fields that need to be decrypted
        sensitive_fields = [
            'symptoms', 'ai_response', 'risk', 'risk_prediction',
            'pulse', 'age', 'sex', 'cp', 'trestbps', 'chol',
            'fbs', 'restecg', 'thalach', 'exang', 'oldpeak',
            'slope', 'ca', 'thal', 'probability'
        ]
        
        for key, value in data.items():
            if key in sensitive_fields and value is not None:
                try:
                    decrypted_value = self.decrypt_data(value)
                    # Try to convert back to number if possible
                    try:
                        if '.' in decrypted_value:
                            decrypted_data[key] = float(decrypted_value)
                        else:
                            decrypted_data[key] = int(decrypted_value)
                    except ValueError:
                        decrypted_data[key] = decrypted_value
                except Exception:
                    # If decryption failed, leave as is
                    decrypted_data[key] = value
            else:
                decrypted_data[key] = value
        
        return decrypted_data


# Create global encryption service instance
encryption_service = EncryptionService()
