"""
DomusAI - Sistema de Notificaciones por Email

Este módulo maneja el envío automático de reportes y alertas
de anomalías por correo electrónico usando SMTP.

Soporta:
- Gmail (SMTP: smtp.gmail.com:587)
- Outlook (SMTP: smtp-mail.outlook.com:587)
- SMTP personalizado

Autor: DomusAI Team
Fecha: Octubre 2025
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Dict, cast
from datetime import datetime
import logging
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_sender.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmailReporter:
    """
    📧 Sistema de Envío de Reportes y Alertas por Email
    
    Características:
    - Envío de reportes mensuales con PDF adjunto
    - Alertas de anomalías críticas en tiempo real
    - Templates HTML profesionales con Jinja2
    - Soporte multi-destinatario
    - Configuración SMTP flexible
    - Logs completos de envíos
    
    Example:
        >>> # Configurar
        >>> emailer = EmailReporter(
        ...     smtp_host='smtp.gmail.com',
        ...     smtp_port=587,
        ...     sender_email='domusai@gmail.com',
        ...     sender_password=os.getenv('EMAIL_PASSWORD')
        ... )
        >>> 
        >>> # Enviar reporte mensual
        >>> emailer.send_monthly_report(
        ...     recipients=['usuario@example.com'],
        ...     pdf_path='reports/generated/reporte_2007-06.pdf',
        ...     month=6,
        ...     year=2007,
        ...     summary_stats={
        ...         'consumption_kwh': 594.71,
        ...         'change_percent': -18.9,
        ...         'efficiency_score': 78
        ...     }
        ... )
    """
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None,
        templates_dir: str = 'reports/email_templates'
    ):
        """
        Inicializar sistema de email.
        
        Args:
            smtp_host: Servidor SMTP (ej: smtp.gmail.com)
            smtp_port: Puerto SMTP (ej: 587 para TLS)
            sender_email: Email del remitente
            sender_password: Contraseña o App Password
            templates_dir: Directorio de templates Jinja2
        """
        # Configuración SMTP (desde args o .env)
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = sender_email or os.getenv('SENDER_EMAIL')
        self.sender_password = sender_password or os.getenv('SENDER_PASSWORD')
        
        # Validar credenciales
        if not self.sender_email or not self.sender_password:
            raise ValueError(
                "❌ Credenciales de email no configuradas. "
                "Define SENDER_EMAIL y SENDER_PASSWORD en .env"
            )
        
        # Type narrowing: después de la validación, sabemos que no son None
        assert self.sender_email is not None
        assert self.sender_password is not None
        
        # Configurar Jinja2 para templates
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir))
        )
        
        logger.info("📧 EmailReporter inicializado")
        logger.info(f"   SMTP: {self.smtp_host}:{self.smtp_port}")
        logger.info(f"   From: {self.sender_email}")
    
    
    def _connect_smtp(self) -> smtplib.SMTP:
        """
        🔌 Establecer conexión SMTP con TLS.
        
        Returns:
            Objeto SMTP conectado y autenticado
        """
        try:
            # Crear conexión
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()  # Habilitar TLS
            
            # Autenticar
            server.login(cast(str, self.sender_email), cast(str, self.sender_password))
            
            logger.debug("✅ Conexión SMTP establecida")
            return server
        
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Error de autenticación SMTP")
            raise ValueError(
                "❌ Credenciales incorrectas. "
                "Si usas Gmail, necesitas una App Password: "
                "https://support.google.com/accounts/answer/185833"
            )
        except Exception as e:
            logger.error(f"❌ Error conectando SMTP: {e}")
            raise
    
    
    def _create_message(
        self,
        recipients: List[str],
        subject: str,
        html_body: str,
        attachments: Optional[List[str]] = None
    ) -> MIMEMultipart:
        """
        📝 Crear mensaje MIME con HTML y adjuntos.
        
        Args:
            recipients: Lista de emails destino
            subject: Asunto del email
            html_body: Cuerpo HTML del mensaje
            attachments: Lista de rutas de archivos a adjuntar
            
        Returns:
            Objeto MIMEMultipart listo para enviar
        """
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['From'] = cast(str, self.sender_email)
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Adjuntar cuerpo HTML
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # Adjuntar archivos si existen
        if attachments:
            for file_path in attachments:
                self._attach_file(msg, file_path)
        
        return msg
    
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """
        📎 Adjuntar archivo al mensaje.
        
        Args:
            msg: Mensaje MIME
            file_path: Ruta del archivo a adjuntar
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            logger.warning(f"⚠️ Archivo no encontrado: {file_path_obj}")
            return
        
        try:
            # Leer archivo
            with open(file_path_obj, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            # Codificar en base64
            encoders.encode_base64(part)
            
            # Añadir header
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path_obj.name}'
            )
            
            msg.attach(part)
            logger.debug(f"📎 Adjuntado: {file_path_obj.name}")
        
        except Exception as e:
            logger.error(f"❌ Error adjuntando {file_path_obj}: {e}")
    
    
    def send_email(
        self,
        recipients: List[str],
        subject: str,
        html_body: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        📤 Enviar email genérico.
        
        Args:
            recipients: Lista de emails destino
            subject: Asunto del email
            html_body: Cuerpo HTML del mensaje
            attachments: Lista de archivos adjuntos (opcional)
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        try:
            logger.info(f"📤 Enviando email a {len(recipients)} destinatario(s)...")
            
            # Crear mensaje
            msg = self._create_message(recipients, subject, html_body, attachments)
            
            # Conectar y enviar
            with self._connect_smtp() as server:
                server.send_message(msg)
            
            logger.info(f"✅ Email enviado exitosamente")
            logger.info(f"   Para: {', '.join(recipients)}")
            logger.info(f"   Asunto: {subject}")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")
            return False


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

def quick_send_test_email(
    recipient: str,
    smtp_host: Optional[str] = None,
    sender_email: Optional[str] = None,
    sender_password: Optional[str] = None
) -> bool:
    """
    🧪 Enviar email de prueba para validar configuración SMTP.
    
    Args:
        recipient: Email de prueba
        smtp_host: Servidor SMTP (opcional, usa .env)
        sender_email: Email remitente (opcional, usa .env)
        sender_password: Password (opcional, usa .env)
        
    Returns:
        True si el test pasó
        
    Example:
        >>> from src.email_sender import quick_send_test_email
        >>> quick_send_test_email('usuario@example.com')
        ✅ Email de prueba enviado exitosamente
    """
    emailer = EmailReporter(
        smtp_host=smtp_host,
        sender_email=sender_email,
        sender_password=sender_password
    )
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            h1 {{ color: #2563eb; }}
            .success {{ background: #dcfce7; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 DomusAI - Email Test</h1>
            <div class="success">
                <p><strong>✅ ¡Configuración correcta!</strong></p>
                <p>El sistema de email de DomusAI está funcionando correctamente.</p>
                <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return emailer.send_email(
        recipients=[recipient],
        subject='🧪 DomusAI - Test de Configuración Email',
        html_body=html_body
    )


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Ejemplo de uso del sistema de email.
    """
    print("📧 DomusAI - Sistema de Email")
    print("=" * 80)
    
    # Test de configuración
    test_email = input("Ingresa tu email para test: ")
    
    if quick_send_test_email(test_email):
        print("\n✅ Email de prueba enviado exitosamente")
        print("   Revisa tu bandeja de entrada")
    else:
        print("\n❌ Error enviando email de prueba")
        print("   Verifica tu configuración en .env")
