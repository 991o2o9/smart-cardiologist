import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Сервис для шифрования данных пользователя"""
    
    def __init__(self):
        # Генерируем ключ шифрования на основе SECRET_KEY
        self._key = self._generate_key()
        self._cipher_suite = Fernet(self._key)
    
    def _generate_key(self) -> bytes:
        """Генерировать ключ шифрования на основе SECRET_KEY"""
        # Используем SECRET_KEY как соль для генерации ключа
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
        """Зашифровать данные"""
        try:
            if not data:
                return data
            
            encrypted_data = self._cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise ValueError("Ошибка при шифровании данных")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Расшифровать данные"""
        try:
            if not encrypted_data:
                return encrypted_data
            
            # Декодируем из base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            # Расшифровываем
            decrypted_data = self._cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise ValueError("Ошибка при расшифровке данных")
    
    def encrypt_medical_data(self, data: dict) -> dict:
        """Зашифровать медицинские данные"""
        encrypted_data = {}
        
        # Список полей, которые нужно зашифровать
        sensitive_fields = [
            'symptoms', 'ai_response', 'risk', 'risk_prediction',
            'pulse', 'age', 'sex', 'cp', 'trestbps', 'chol',
            'fbs', 'restecg', 'thalach', 'exang', 'oldpeak',
            'slope', 'ca', 'thal', 'probability'
        ]
        
        for key, value in data.items():
            if key in sensitive_fields and value is not None:
                if isinstance(value, (int, float)):
                    # Для числовых значений конвертируем в строку
                    encrypted_data[key] = self.encrypt_data(str(value))
                elif isinstance(value, str):
                    encrypted_data[key] = self.encrypt_data(value)
                else:
                    encrypted_data[key] = value
            else:
                encrypted_data[key] = value
        
        return encrypted_data
    
    def decrypt_medical_data(self, data: dict) -> dict:
        """Расшифровать медицинские данные"""
        decrypted_data = {}
        
        # Список полей, которые нужно расшифровать
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
                    # Пытаемся конвертировать обратно в число, если это возможно
                    try:
                        if '.' in decrypted_value:
                            decrypted_data[key] = float(decrypted_value)
                        else:
                            decrypted_data[key] = int(decrypted_value)
                    except ValueError:
                        decrypted_data[key] = decrypted_value
                except Exception:
                    # Если не удалось расшифровать, оставляем как есть
                    decrypted_data[key] = value
            else:
                decrypted_data[key] = value
        
        return decrypted_data


# Создаем глобальный экземпляр сервиса шифрования
encryption_service = EncryptionService()
