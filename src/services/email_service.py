"""
Сервис для отправки email
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email"""
    
    def __init__(self):
        """Инициализация сервиса email"""
        self.mail_config = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=settings.MAIL_TLS,
            MAIL_SSL_TLS=settings.MAIL_SSL,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fastmail = FastMail(self.mail_config)
    
    async def send_activation_email(self, email: str, activation_code: str) -> bool:
        """Отправить email с кодом активации"""
        try:
            message = MessageSchema(
                subject="Активация аккаунта - Smart Cardiologist",
                recipients=[email],
                body=self._create_activation_email_body(activation_code),
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Activation email sent to: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send activation email to {email}: {e}")
            return False
    
    async def send_welcome_email(self, email: str) -> bool:
        """Отправить приветственный email после активации"""
        try:
            message = MessageSchema(
                subject="Добро пожаловать в Smart Cardiologist!",
                recipients=[email],
                body=self._create_welcome_email_body(),
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Welcome email sent to: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {e}")
            return False
    
    def _create_activation_email_body(self, activation_code: str) -> str:
        """Создать HTML тело email с кодом активации"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Активация аккаунта</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 0 0 5px 5px;
                }}
                .activation-code {{
                    background-color: #3498db;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    padding: 15px;
                    text-align: center;
                    border-radius: 5px;
                    margin: 20px 0;
                    letter-spacing: 3px;
                }}
                .warning {{
                    background-color: #f39c12;
                    color: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #7f8c8d;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Smart Cardiologist</h1>
                <p>Активация аккаунта</p>
            </div>
            
            <div class="content">
                <h2>Здравствуйте!</h2>
                <p>Благодарим за регистрацию в системе Smart Cardiologist!</p>
                
                <p>Для завершения регистрации используйте следующий код активации:</p>
                
                <div class="activation-code">
                    {activation_code}
                </div>
                
                <div class="warning">
                    <strong>Внимание!</strong> Код действителен в течение 10 минут.
                </div>
                
                <p>Если вы не регистрировались в нашей системе, проигнорируйте это письмо.</p>
                
                <p>С уважением,<br>Команда Smart Cardiologist</p>
            </div>
            
            <div class="footer">
                <p>Это автоматическое письмо, не отвечайте на него.</p>
            </div>
        </body>
        </html>
        """
    
    def _create_welcome_email_body(self) -> str:
        """Создать HTML тело приветственного email"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Добро пожаловать!</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background-color: #27ae60;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }
                .content {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 0 0 5px 5px;
                }
                .success {
                    background-color: #27ae60;
                    color: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    text-align: center;
                }
                .features {
                    background-color: #ecf0f1;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }
                .footer {
                    text-align: center;
                    margin-top: 20px;
                    color: #7f8c8d;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Smart Cardiologist</h1>
                <p>Добро пожаловать!</p>
            </div>
            
            <div class="content">
                <div class="success">
                    <h2>🎉 Ваш аккаунт успешно активирован!</h2>
                </div>
                
                <h3>Теперь вы можете:</h3>
                <div class="features">
                    <ul>
                        <li>Получать консультации от AI кардиолога</li>
                        <li>Анализировать риски сердечных заболеваний</li>
                        <li>Сохранять историю анализов</li>
                        <li>Отслеживать изменения в состоянии здоровья</li>
                    </ul>
                </div>
                
                <p>Начните использовать все возможности системы прямо сейчас!</p>
                
                <p>С уважением,<br>Команда Smart Cardiologist</p>
            </div>
            
            <div class="footer">
                <p>Это автоматическое письмо, не отвечайте на него.</p>
            </div>
        </body>
        </html>
        """
    
    async def test_connection(self) -> bool:
        """Проверить подключение к email серверу"""
        try:
            # Простая проверка конфигурации
            if not all([
                settings.MAIL_USERNAME,
                settings.MAIL_PASSWORD,
                settings.MAIL_FROM,
                settings.MAIL_SERVER
            ]):
                logger.warning("Email configuration incomplete")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False
