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


    def send_monthly_report(
        self,
        recipients: List[str],
        pdf_path: str,
        month: int,
        year: int,
        summary_stats: Dict,
        recommendations: Optional[List[str]] = None,
        anomalies_csv: Optional[str] = None
    ) -> bool:
        """
        📊 Enviar reporte mensual con PDF adjunto.
        
        Args:
            recipients: Lista de emails destino
            pdf_path: Ruta del PDF del reporte
            month: Mes del reporte (1-12)
            year: Año del reporte
            summary_stats: Diccionario con estadísticas:
                - consumption_kwh: float
                - change_percent: float
                - efficiency_score: int
                - critical_anomalies: int
                - total_records: int
            recommendations: Lista de recomendaciones personalizadas
            anomalies_csv: Ruta opcional del CSV de anomalías
            
        Returns:
            True si se envió correctamente
            
        Example:
            >>> emailer = EmailReporter()
            >>> emailer.send_monthly_report(
            ...     recipients=['usuario@example.com'],
            ...     pdf_path='reports/generated/reporte_2007-06.pdf',
            ...     month=6,
            ...     year=2007,
            ...     summary_stats={
            ...         'consumption_kwh': 594.71,
            ...         'change_percent': -18.9,
            ...         'efficiency_score': 78,
            ...         'critical_anomalies': 5,
            ...         'total_records': 30240
            ...     },
            ...     recommendations=[
            ...         'Reducir consumo nocturno entre 02:00-05:00',
            ...         'Optimizar uso de electrodomésticos en horas pico'
            ...     ]
            ... )
        """
        try:
            logger.info(f"📊 Enviando reporte mensual {year}-{month:02d}")
            
            # Nombres de meses en español
            month_names = [
                'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
            ]
            
            # Validar mes
            if not (1 <= month <= 12):
                raise ValueError(f"Mes inválido: {month}. Debe estar entre 1 y 12.")
            
            # Preparar datos para template
            template_data = {
                # Información básica
                'month_name': month_names[month - 1],
                'year': year,
                'period': f"{month_names[month - 1]} {year}",
                'generation_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                
                # Estadísticas principales (con valores por defecto)
                'total_records': summary_stats.get('total_records', 0),
                'consumption_kwh': summary_stats.get('consumption_kwh', 0.0),
                'change_percent': summary_stats.get('change_percent', 0.0),
                'efficiency_score': summary_stats.get('efficiency_score', 0),
                'critical_anomalies': summary_stats.get('critical_anomalies', 0),
                
                # Recomendaciones personalizadas
                'recommendations': recommendations or [
                    'Mantener patrón de consumo actual, está dentro de rangos normales',
                    'Considerar programar electrodomésticos en horarios de menor demanda',
                    'Revisar periódicamente el estado de tus equipos eléctricos',
                    'Monitorear las horas de mayor consumo para identificar oportunidades'
                ],
                
                # Información técnica adicional
                'technical_summary': True,
                'data_quality': summary_stats.get('data_quality', 'Excelente'),
                'peak_hours': summary_stats.get('peak_hours', '07:00-09:00, 19:00-22:00'),
                
                # Archivos adjuntos
                'anomalies_csv': anomalies_csv is not None,
                'predictions_data': summary_stats.get('has_predictions', False)
            }
            
            # Cargar y renderizar template
            try:
                template = self.jinja_env.get_template('monthly_report_email.html')
                html_body = template.render(**template_data)
                logger.debug(f"✅ Template renderizado: {len(html_body):,} caracteres")
            except Exception as e:
                logger.error(f"❌ Error renderizando template: {e}")
                raise ValueError(f"Error en template monthly_report_email.html: {e}")
            
            # Preparar adjuntos
            attachments = []
            
            # PDF del reporte (obligatorio)
            pdf_path_obj = Path(pdf_path)
            if not pdf_path_obj.exists():
                logger.warning(f"⚠️ PDF no encontrado: {pdf_path}")
                # Continuar sin PDF (email informativo)
            else:
                attachments.append(str(pdf_path_obj))
                logger.debug(f"📎 PDF adjunto: {pdf_path_obj.name}")
            
            # CSV de anomalías (opcional)
            if anomalies_csv:
                anomalies_path = Path(anomalies_csv)
                if anomalies_path.exists():
                    attachments.append(str(anomalies_path))
                    logger.debug(f"📎 CSV adjunto: {anomalies_path.name}")
                else:
                    logger.warning(f"⚠️ CSV de anomalías no encontrado: {anomalies_csv}")
            
            # Crear asunto personalizado
            subject = f"📊 Reporte Mensual DomusAI - {month_names[month - 1]} {year}"
            
            # Log de información del envío
            logger.info(f"   Destinatarios: {len(recipients)}")
            logger.info(f"   Adjuntos: {len(attachments)}")
            logger.info(f"   Consumo: {summary_stats.get('consumption_kwh', 0):.1f} kWh")
            logger.info(f"   Cambio: {summary_stats.get('change_percent', 0):+.1f}%")
            
            # Enviar email
            success = self.send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_body,
                attachments=attachments
            )
            
            if success:
                logger.info(f"✅ Reporte mensual {year}-{month:02d} enviado exitosamente")
                logger.info(f"   Total destinatarios: {len(recipients)}")
                logger.info(f"   Total adjuntos: {len(attachments)}")
            else:
                logger.error(f"❌ Error enviando reporte mensual {year}-{month:02d}")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ Error en send_monthly_report: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False


    def send_anomaly_alert(
        self,
        recipients: List[str],
        anomalies: Dict,
        severity: str = 'critical',
        anomalies_csv: Optional[str] = None
    ) -> bool:
        """
        🚨 Enviar alerta de anomalías críticas.
        
        Args:
            recipients: Lista de emails destino
            anomalies: Diccionario con información de anomalías:
                - timestamp: str o datetime de detección
                - consumption_value: float del consumo anómalo
                - normal_average: float del consumo normal
                - deviation_percent: float del porcentaje de desviación
                - anomaly_type: str tipo de anomalía
                - confidence: str nivel de confianza
                - duration: str duración estimada
                - anomaly_list: List[Dict] lista de anomalías múltiples (opcional)
            severity: Severidad general ('critical', 'warning', 'medium')
            anomalies_csv: Ruta del CSV con todas las anomalías
            
        Returns:
            True si se envió correctamente
            
        Example:
            >>> emailer = EmailReporter()
            >>> anomaly_data = {
            ...     'timestamp': '06/06/2007 14:30',
            ...     'consumption_value': 4.567,
            ...     'normal_average': 1.089,
            ...     'deviation_percent': 319.4,
            ...     'anomaly_type': 'tipo_1_consumo_alto',
            ...     'confidence': 'Alta (94.2%)',
            ...     'duration': '45 minutos'
            ... }
            >>> emailer.send_anomaly_alert(
            ...     recipients=['admin@example.com'],
            ...     anomalies=anomaly_data,
            ...     severity='critical'
            ... )
        """
        try:
            logger.info(f"🚨 Enviando alerta de anomalías ({severity})")
            
            # Validar severidad
            valid_severities = ['critical', 'warning', 'medium', 'low']
            if severity not in valid_severities:
                logger.warning(f"⚠️ Severidad '{severity}' no válida, usando 'critical'")
                severity = 'critical'
            
            # Extraer datos de anomalías con valores por defecto
            anomaly_timestamp = anomalies.get('timestamp', 'N/A')
            consumption_value = anomalies.get('consumption_value', 0.0)
            normal_average = anomalies.get('normal_average', 1.089)  # Promedio del dataset
            deviation_percent = anomalies.get('deviation_percent', 0.0)
            anomaly_type = anomalies.get('anomaly_type', 'Consumo anómalo detectado')
            confidence = anomalies.get('confidence', 'Alta')
            duration = anomalies.get('duration', 'En análisis')
            
            # Formatear timestamp si es necesario
            if hasattr(anomaly_timestamp, 'strftime'):
                anomaly_timestamp = anomaly_timestamp.strftime('%d/%m/%Y %H:%M')
            
            # Recomendaciones según tipo de anomalía
            recommendations_map = {
                'tipo_1_consumo_alto': [
                    '🔌 Verificar inmediatamente que no haya electrodomésticos defectuosos',
                    '🕐 Revisar el consumo en las próximas 2 horas',
                    '⚡ Considerar apagar equipos no esenciales temporalmente',
                    '📞 Si persiste por más de 4 horas, contactar a un electricista'
                ],
                'tipo_3_temporal': [
                    '🌙 Anomalía detectada en horario nocturno (valle)',
                    '🔍 Revisar si hay equipos encendidos innecesariamente',
                    '⚙️ Verificar timers de electrodomésticos programables',
                    '💡 Considerar desconectar equipos en standby'
                ],
                'tipo_4_sensor': [
                    '🔧 Posible fallo en el sensor de medición',
                    '📊 Verificar las conexiones del sistema de monitoreo',
                    '🔄 Reiniciar el dispositivo ESP32/Arduino',
                    '📡 Comprobar conectividad MQTT si aplica'
                ],
                'default': [
                    '🔍 Revisar el análisis completo en el archivo adjunto',
                    '📊 Monitorear el consumo en las próximas horas',
                    '⚠️ Si el problema persiste, considerar una inspección profesional',
                    '📞 Contactar soporte técnico si es necesario'
                ]
            }
            
            # Seleccionar recomendaciones según tipo
            recommended_actions = anomalies.get(
                'recommended_actions',
                recommendations_map.get(anomaly_type, recommendations_map['default'])
            )
            
            # Preparar lista de anomalías múltiples
            anomaly_list = anomalies.get('anomaly_list', [])
            
            # Preparar datos para template
            template_data = {
                # Información básica
                'severity': severity,
                'detection_time': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'generation_time': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                
                # Detalles de la anomalía
                'anomaly_timestamp': anomaly_timestamp,
                'anomaly_type': anomaly_type,
                'consumption_value': f"{consumption_value:.3f}",
                'normal_average': f"{normal_average:.3f}",
                'deviation_percent': f"{deviation_percent:+.1f}",
                'duration': duration,
                'confidence': confidence,
                
                # Lista de anomalías múltiples
                'anomalies': anomaly_list,
                
                # Recomendaciones de acción
                'recommended_actions': recommended_actions,
                
                # Información adicional
                'detailed_report': anomalies_csv is not None
            }
            
            # Cargar y renderizar template
            try:
                template = self.jinja_env.get_template('anomaly_alert_email.html')
                html_body = template.render(**template_data)
                logger.debug(f"✅ Template renderizado: {len(html_body):,} caracteres")
            except Exception as e:
                logger.error(f"❌ Error renderizando template: {e}")
                raise ValueError(f"Error en template anomaly_alert_email.html: {e}")
            
            # Preparar adjuntos
            attachments = []
            if anomalies_csv:
                csv_path = Path(anomalies_csv)
                if csv_path.exists():
                    attachments.append(str(csv_path))
                    logger.debug(f"📎 CSV adjunto: {csv_path.name}")
                else:
                    logger.warning(f"⚠️ CSV de anomalías no encontrado: {anomalies_csv}")
            
            # Asunto según severidad
            subject_map = {
                'critical': '🚨 ALERTA CRÍTICA - Anomalía Detectada en Consumo Energético',
                'warning': '⚠️ ALERTA - Consumo Anómalo Detectado',
                'medium': 'ℹ️ Notificación - Anomalía de Prioridad Media',
                'low': '📊 Información - Variación en Consumo Detectada'
            }
            subject = subject_map.get(severity, subject_map['warning'])
            
            # Log de información del envío
            logger.info(f"   Tipo: {anomaly_type}")
            logger.info(f"   Consumo: {consumption_value:.3f} kW")
            logger.info(f"   Desviación: {deviation_percent:+.1f}%")
            logger.info(f"   Destinatarios: {len(recipients)}")
            logger.info(f"   Adjuntos: {len(attachments)}")
            
            # Enviar email
            success = self.send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_body,
                attachments=attachments
            )
            
            if success:
                logger.info(f"✅ Alerta de anomalías ({severity}) enviada exitosamente")
                anomaly_count = len(anomaly_list) if anomaly_list else 1
                logger.info(f"   Total anomalías: {anomaly_count}")
                logger.info(f"   Severidad: {severity}")
            else:
                logger.error(f"❌ Error enviando alerta de anomalías ({severity})")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ Error en send_anomaly_alert: {e}")
            import traceback
            logger.debug(traceback.format_exc())
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

