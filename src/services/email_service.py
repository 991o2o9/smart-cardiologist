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
                subject="Account Activation - Smart Cardiologist",
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
                subject="Welcome to Smart Cardiologist!",
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
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Activation - Smart Cardiologist</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="heartbeat" x="0" y="0" width="100" height="20" patternUnits="userSpaceOnUse"><path d="M0 10 L20 10 L25 0 L30 20 L35 5 L40 15 L45 10 L100 10" stroke="rgba(255,255,255,0.1)" stroke-width="1" fill="none"/></pattern></defs><rect width="100" height="100" fill="url(%23heartbeat)"/></svg>') repeat;
            opacity: 0.3;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .logo {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        
        .heart-icon {{
            width: 32px;
            height: 32px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: heartbeat 1.5s ease-in-out infinite;
        }}
        
        @keyframes heartbeat {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        
        .subtitle {{
            font-size: 16px;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .content {{
            padding: 40px 30px;
            background: white;
        }}
        
        .greeting {{
            font-size: 24px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        
        .message {{
            font-size: 16px;
            color: #5a6c7d;
            margin-bottom: 30px;
            line-height: 1.8;
        }}
        
        .activation-section {{
            text-align: center;
            margin: 40px 0;
        }}
        
        .activation-label {{
            font-size: 14px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
            font-weight: 500;
        }}
        
        .activation-code {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            font-size: 32px;
            font-weight: 700;
            padding: 25px 40px;
            border-radius: 15px;
            display: inline-block;
            letter-spacing: 8px;
            margin-bottom: 15px;
            box-shadow: 0 10px 25px rgba(52, 152, 219, 0.3);
            font-family: 'Courier New', monospace;
            border: 3px solid #ffffff;
            animation: pulse 2s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ box-shadow: 0 10px 25px rgba(52, 152, 219, 0.3); }}
            50% {{ box-shadow: 0 15px 35px rgba(52, 152, 219, 0.5); }}
        }}
        
        .timer-warning {{
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 30px 0;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .timer-icon {{
            width: 24px;
            height: 24px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        
        .security-notice {{
            background: #f8f9fa;
            border-left: 4px solid #e74c3c;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
        }}
        
        .security-notice h4 {{
            color: #e74c3c;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        
        .security-notice p {{
            color: #5a6c7d;
            font-size: 14px;
            margin: 0;
        }}
        
        .features {{
            background: linear-gradient(135deg, #ecf0f1 0%, #d5dbdb 100%);
            padding: 25px;
            border-radius: 15px;
            margin: 30px 0;
        }}
        
        .features h4 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        
        .features ul {{
            list-style: none;
            padding: 0;
        }}
        
        .features li {{
            padding: 8px 0;
            color: #5a6c7d;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .features li::before {{
            content: '❤️';
            font-size: 16px;
        }}
        
        .signature {{
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #ecf0f1;
        }}
        
        .signature p {{
            color: #5a6c7d;
            font-size: 16px;
        }}
        
        .team-name {{
            font-weight: 600;
            color: #e74c3c;
        }}
        
        .footer {{
            background: #2c3e50;
            color: #bdc3c7;
            padding: 30px;
            text-align: center;
        }}
        
        .footer p {{
            font-size: 12px;
            margin-bottom: 15px;
        }}
        
        .footer-links {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .footer-links a {{
            color: #3498db;
            text-decoration: none;
            font-size: 12px;
        }}
        
        .footer-links a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 600px) {{
            .email-container {{
                margin: 10px;
                border-radius: 15px;
            }}
            
            .header, .content {{
                padding: 30px 20px;
            }}
            
            .activation-code {{
                font-size: 24px;
                padding: 20px 30px;
                letter-spacing: 4px;
            }}
            
            .logo {{
                font-size: 24px;
            }}
            
            .greeting {{
                font-size: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <div class="heart-icon">❤️</div>
                    Smart Cardiologist
                </div>
                <div class="subtitle">Advanced Cardiac Risk Assessment</div>
            </div>
        </div>
        
        <div class="content">
            <div class="greeting">Welcome to Smart Cardiologist!</div>
            
            <div class="message">
                Thank you for joining our advanced cardiac health platform. We're excited to help you monitor and protect your heart health with cutting-edge AI technology.
            </div>
            
            <div class="activation-section">
                <div class="activation-label">Your Activation Code</div>
                <div class="activation-code">{activation_code}</div>
                <p style="color: #7f8c8d; font-size: 14px;">Enter this code to activate your account</p>
            </div>
            
            <div class="timer-warning">
                <div class="timer-icon">⏰</div>
                <div>
                    <strong>Important:</strong> This activation code expires in 10 minutes. Please complete your registration promptly to ensure account security.
                </div>
            </div>
            
            <div class="features">
                <h4>What you'll get access to:</h4>
                <ul>
                    <li>AI-powered cardiac risk assessment</li>
                    <li>Personalized heart health recommendations</li>
                    <li>Real-time health monitoring tools</li>
                    <li>Professional medical insights</li>
                    <li>Secure health data storage</li>
                </ul>
            </div>
            
            <div class="security-notice">
                <h4>🔒 Security Notice</h4>
                <p>If you didn't create an account with Smart Cardiologist, please ignore this email. Your security is our top priority.</p>
            </div>
            
            <div class="signature">
                <p>Best regards,<br>
                <span class="team-name">The Smart Cardiologist Team</span><br>
                <em>Protecting hearts with intelligent technology</em></p>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>© 2025 Smart Cardiologist. All rights reserved.</p>
            <div class="footer-links">
                <a href="#">Privacy Policy</a>
                <a href="#">Terms of Service</a>
                <a href="#">Support</a>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    def _create_welcome_email_body(self) -> str:
        """Создать HTML тело приветственного email"""
        return """
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Smart Cardiologist!</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .header {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="celebration" x="0" y="0" width="50" height="50" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="30" r="1.5" fill="rgba(255,255,255,0.08)"/><circle cx="25" cy="45" r="1" fill="rgba(255,255,255,0.06)"/></pattern></defs><rect width="100" height="100" fill="url(%23celebration)"/></svg>') repeat;
            opacity: 0.4;
        }
        
        .header-content {
            position: relative;
            z-index: 1;
        }
        
        .logo {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .heart-icon {
            width: 32px;
            height: 32px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: heartbeat 1.5s ease-in-out infinite;
        }
        
        @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .subtitle {
            font-size: 16px;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .content {
            padding: 40px 30px;
            background: white;
        }
        
        .success-banner {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(39, 174, 96, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .success-banner::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0%, 100% { transform: translateX(-50%) translateY(-50%) rotate(0deg); }
            50% { transform: translateX(-50%) translateY(-50%) rotate(180deg); }
        }
        
        .success-banner h2 {
            font-size: 24px;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }
        
        .success-banner p {
            font-size: 16px;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        .celebration-emoji {
            font-size: 40px;
            margin-bottom: 15px;
            display: block;
            animation: bounce 2s ease-in-out infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .features-section {
            margin: 40px 0;
        }
        
        .features-title {
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 25px;
            text-align: center;
        }
        
        .features-grid {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 30px;
            border-radius: 15px;
            border: 2px solid #e74c3c;
            position: relative;
        }
        
        .features-grid::before {
            content: '🫀';
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 5px 10px;
            border-radius: 50%;
            font-size: 20px;
        }
        
        .features-list {
            list-style: none;
            padding: 0;
            display: grid;
            gap: 15px;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .feature-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .feature-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }
        
        .feature-text {
            color: #5a6c7d;
            font-size: 15px;
            font-weight: 500;
        }
        
        .cta-section {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin: 30px 0;
            position: relative;
            overflow: hidden;
        }
        
        .cta-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: slide 3s ease-in-out infinite;
        }
        
        @keyframes slide {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .cta-text {
            font-size: 18px;
            font-weight: 600;
            position: relative;
            z-index: 1;
        }
        
        .signature {
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
        }
        
        .signature p {
            color: #5a6c7d;
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        .team-name {
            font-weight: 600;
            color: #e74c3c;
            font-size: 18px;
        }
        
        .team-motto {
            font-style: italic;
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .footer {
            background: #2c3e50;
            color: #bdc3c7;
            padding: 30px;
            text-align: center;
        }
        
        .footer p {
            font-size: 12px;
            margin-bottom: 15px;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }
        
        .footer-links a {
            color: #3498db;
            text-decoration: none;
            font-size: 12px;
        }
        
        .footer-links a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 600px) {
            .email-container {
                margin: 10px;
                border-radius: 15px;
            }
            
            .header, .content {
                padding: 30px 20px;
            }
            
            .success-banner {
                padding: 25px 20px;
            }
            
            .features-grid {
                padding: 20px;
            }
            
            .logo {
                font-size: 24px;
            }
            
            .success-banner h2 {
                font-size: 20px;
            }
            
            .features-title {
                font-size: 18px;
            }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <div class="heart-icon">❤️</div>
                    Smart Cardiologist
                </div>
                <div class="subtitle">Advanced Cardiac Risk Assessment</div>
            </div>
        </div>
        
        <div class="content">
            <div class="success-banner">
                <span class="celebration-emoji">🎉</span>
                <h2>Account Successfully Activated!</h2>
                <p>Welcome to the future of cardiac health monitoring</p>
            </div>
            
            <div class="features-section">
                <h3 class="features-title">You now have access to:</h3>
                <div class="features-grid">
                    <ul class="features-list">
                        <li class="feature-item">
                            <div class="feature-icon">🤖</div>
                            <div class="feature-text">AI-powered cardiac risk assessment and analysis</div>
                        </li>
                        <li class="feature-item">
                            <div class="feature-icon">📊</div>
                            <div class="feature-text">Personalized heart health recommendations</div>
                        </li>
                        <li class="feature-item">
                            <div class="feature-icon">📱</div>
                            <div class="feature-text">Real-time health monitoring and alerts</div>
                        </li>
                        <li class="feature-item">
                            <div class="feature-icon">🩺</div>
                            <div class="feature-text">Professional medical insights and guidance</div>
                        </li>
                        <li class="feature-item">
                            <div class="feature-icon">🔒</div>
                            <div class="feature-text">Secure health data storage and history tracking</div>
                        </li>
                    </ul>
                </div>
            </div>
            
            <div class="cta-section">
                <div class="cta-text">Start protecting your heart health today!</div>
            </div>
            
            <div class="signature">
                <p>Best regards,</p>
                <div class="team-name">The Smart Cardiologist Team</div>
                <div class="team-motto">Protecting hearts with intelligent technology</div>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>© 2025 Smart Cardiologist. All rights reserved.</p>
            <div class="footer-links">
                <a href="#">Privacy Policy</a>
                <a href="#">Terms of Service</a>
                <a href="#">Support Center</a>
            </div>
        </div>
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