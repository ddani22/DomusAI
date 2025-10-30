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
import traceback
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
        
        # Agregar filtros personalizados
        def format_number(value):
            """Formatear número con comas (ej: 1000 → 1,000)"""
            try:
                return f"{int(value):,}"
            except:
                return str(value)
        
        self.jinja_env.filters['format_number'] = format_number
        
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
            logger.debug(traceback.format_exc())
            return False


    def send_daily_report(
        self,
        recipients: List[str],
        report_date: datetime,
        daily_stats: Dict,
        hourly_data: Optional[List[Dict]] = None,
        insights: Optional[List[str]] = None,
        pdf_path: Optional[str] = None
    ) -> bool:
        """
        ☀️ Enviar reporte diario de consumo.
        
        Args:
            recipients: Lista de emails destino
            report_date: Fecha del reporte
            daily_stats: Diccionario con estadísticas diarias:
                - total_consumption: float (kWh del día)
                - today_vs_avg: float (% comparado con promedio)
                - peak_hour: str (hora de mayor consumo)
                - yesterday_consumption: float (kWh de ayer)
                - total_records: int (registros procesados)
            hourly_data: Lista de consumo por hora [{'hour': '08:00', 'consumption': 0.8}, ...]
            insights: Lista de recomendaciones personalizadas
            pdf_path: Ruta opcional del PDF del reporte
            
        Returns:
            True si se envió correctamente
            
        Example:
            >>> emailer = EmailReporter()
            >>> emailer.send_daily_report(
            ...     recipients=['usuario@example.com'],
            ...     report_date=datetime(2025, 10, 28),
            ...     daily_stats={
            ...         'total_consumption': 18.5,
            ...         'today_vs_avg': 104.2,
            ...         'peak_hour': '19:00',
            ...         'yesterday_consumption': 17.8,
            ...         'total_records': 1440
            ...     },
            ...     insights=['Consumo ligeramente alto en horario nocturno']
            ... )
        """
        try:
            logger.info(f"☀️ Enviando reporte diario {report_date.strftime('%Y-%m-%d')}")
            
            # Preparar datos para template
            template_data = {
                # Información básica
                'report_date': report_date.strftime('%d/%m/%Y'),
                'report_day_name': report_date.strftime('%A'),
                'generation_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                
                # Estadísticas principales
                'total_consumption': daily_stats.get('total_consumption', 0.0),
                'today_vs_avg': daily_stats.get('today_vs_avg', 100.0),
                'peak_hour': daily_stats.get('peak_hour', 'N/A'),
                'yesterday_consumption': daily_stats.get('yesterday_consumption', 0.0),
                'total_records': daily_stats.get('total_records', 0),
                
                # Datos horarios
                'hourly_data': hourly_data or [],
                
                # Recomendaciones personalizadas
                'insights': insights or [
                    'Tu consumo del día está dentro de rangos normales',
                    'Considera usar electrodomésticos en horarios valle (23:00-07:00)',
                    'Revisa el consumo en standby durante la noche'
                ]
            }
            
            # Cargar y renderizar template
            try:
                template = self.jinja_env.get_template('email_daily_report.html')
                html_body = template.render(**template_data)
                logger.debug(f"✅ Template diario renderizado: {len(html_body):,} caracteres")
            except Exception as e:
                logger.error(f"❌ Error renderizando template diario: {e}")
                raise ValueError(f"Error en template email_daily_report.html: {e}")
            
            # Preparar adjuntos
            attachments = []
            if pdf_path:
                pdf_path_obj = Path(pdf_path)
                if pdf_path_obj.exists():
                    attachments.append(str(pdf_path_obj))
                    logger.debug(f"📎 PDF adjunto: {pdf_path_obj.name}")
            
            # Crear asunto
            subject = f"☀️ Reporte Diario DomusAI - {report_date.strftime('%d/%m/%Y')}"
            
            # Log de información
            logger.info(f"   Consumo: {daily_stats.get('total_consumption', 0):.1f} kWh")
            logger.info(f"   vs Promedio: {daily_stats.get('today_vs_avg', 100):+.1f}%")
            logger.info(f"   Pico: {daily_stats.get('peak_hour', 'N/A')}")
            
            # Enviar email
            success = self.send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_body,
                attachments=attachments
            )
            
            if success:
                logger.info(f"✅ Reporte diario {report_date.strftime('%Y-%m-%d')} enviado")
            else:
                logger.error(f"❌ Error enviando reporte diario")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ Error en send_daily_report: {e}")
            logger.debug(traceback.format_exc())
            return False


    def send_weekly_report(
        self,
        recipients: List[str],
        week_start: datetime,
        week_end: datetime,
        weekly_stats: Dict,
        daily_consumption: Optional[List[float]] = None,
        recommendations: Optional[List[str]] = None,
        pdf_path: Optional[str] = None
    ) -> bool:
        """
        📅 Enviar reporte semanal de consumo.
        
        Args:
            recipients: Lista de emails destino
            week_start: Fecha inicio de la semana
            week_end: Fecha fin de la semana
            weekly_stats: Diccionario con estadísticas semanales:
                - total_weekly_kwh: float (consumo total de la semana)
                - avg_daily_kwh: float (promedio diario)
                - change_vs_last_week: float (% cambio vs semana anterior)
                - efficiency_score: int (0-100)
                - best_day: str (mejor día)
                - best_day_kwh: float
                - worst_day: str (peor día)
                - worst_day_kwh: float
                - max_power_kw: float (pico de potencia)
                - anomalies_count: int
                - total_records: int
            daily_consumption: Lista de 7 valores [Lun, Mar, Mié, Jue, Vie, Sáb, Dom]
            recommendations: Lista de recomendaciones personalizadas
            pdf_path: Ruta opcional del PDF
            
        Returns:
            True si se envió correctamente
            
        Example:
            >>> emailer = EmailReporter()
            >>> emailer.send_weekly_report(
            ...     recipients=['usuario@example.com'],
            ...     week_start=datetime(2025, 10, 21),
            ...     week_end=datetime(2025, 10, 27),
            ...     weekly_stats={
            ...         'total_weekly_kwh': 124.5,
            ...         'avg_daily_kwh': 17.8,
            ...         'change_vs_last_week': -3.2,
            ...         'efficiency_score': 87,
            ...         'best_day': 'Miércoles',
            ...         'best_day_kwh': 15.2,
            ...         'worst_day': 'Sábado',
            ...         'worst_day_kwh': 21.3
            ...     },
            ...     daily_consumption=[18.2, 16.9, 15.2, 17.5, 18.8, 21.3, 16.6]
            ... )
        """
        try:
            logger.info(f"📅 Enviando reporte semanal {week_start.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}")
            
            # Preparar datos para template
            template_data = {
                # Información básica
                'week_start': week_start.strftime('%d %b'),
                'week_end': week_end.strftime('%d %b, %Y'),
                'week_start_full': week_start.strftime('%d/%m/%Y'),
                'week_end_full': week_end.strftime('%d/%m/%Y'),
                'generation_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                
                # Estadísticas semanales
                'total_weekly_kwh': weekly_stats.get('total_weekly_kwh', 0.0),
                'avg_daily_kwh': weekly_stats.get('avg_daily_kwh', 0.0),
                'change_vs_last_week': weekly_stats.get('change_vs_last_week', 0.0),
                'efficiency_score': weekly_stats.get('efficiency_score', 0),
                'avg_power_kw': weekly_stats.get('avg_power_kw', 0.0),
                'max_power_kw': weekly_stats.get('max_power_kw', 0.0),
                'anomalies_count': weekly_stats.get('anomalies_count', 0),
                'total_records': weekly_stats.get('total_records', 0),
                
                # Mejor y peor día
                'best_day': weekly_stats.get('best_day', 'N/A'),
                'best_day_kwh': weekly_stats.get('best_day_kwh', 0.0),
                'worst_day': weekly_stats.get('worst_day', 'N/A'),
                'worst_day_kwh': weekly_stats.get('worst_day_kwh', 0.0),
                
                # Consumo diario (7 días)
                'daily_consumption': daily_consumption or [0.0] * 7,
                
                # Comparación con semana anterior
                'last_week_kwh': weekly_stats.get('last_week_kwh', 0.0),
                'last_week_avg_daily': weekly_stats.get('last_week_avg_daily', 0.0),
                'last_week_max': weekly_stats.get('last_week_max', 0.0),
                'last_week_anomalies': weekly_stats.get('last_week_anomalies', 0),
                
                # Recomendaciones personalizadas
                'recommendations': recommendations or [
                    f"El {weekly_stats.get('worst_day', 'Sábado')} tuvo el mayor consumo. Analiza actividades de ese día.",
                    f"El {weekly_stats.get('best_day', 'Miércoles')} fue tu día más eficiente. Intenta replicar esos hábitos.",
                    'Considera programar electrodomésticos en horarios valle (23:00-07:00)',
                    'Revisa el consumo en standby durante la noche'
                ]
            }
            
            # Cargar y renderizar template
            try:
                template = self.jinja_env.get_template('email_weekly_report.html')
                html_body = template.render(**template_data)
                logger.debug(f"✅ Template semanal renderizado: {len(html_body):,} caracteres")
            except Exception as e:
                logger.error(f"❌ Error renderizando template semanal: {e}")
                raise ValueError(f"Error en template email_weekly_report.html: {e}")
            
            # Preparar adjuntos
            attachments = []
            if pdf_path:
                pdf_path_obj = Path(pdf_path)
                if pdf_path_obj.exists():
                    attachments.append(str(pdf_path_obj))
                    logger.debug(f"📎 PDF adjunto: {pdf_path_obj.name}")
            
            # Crear asunto
            subject = f"📅 Reporte Semanal DomusAI - {week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')}"
            
            # Log de información
            logger.info(f"   Consumo: {weekly_stats.get('total_weekly_kwh', 0):.1f} kWh")
            logger.info(f"   Promedio diario: {weekly_stats.get('avg_daily_kwh', 0):.1f} kWh")
            logger.info(f"   Cambio: {weekly_stats.get('change_vs_last_week', 0):+.1f}%")
            
            # Enviar email
            success = self.send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_body,
                attachments=attachments
            )
            
            if success:
                logger.info(f"✅ Reporte semanal enviado exitosamente")
            else:
                logger.error(f"❌ Error enviando reporte semanal")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ Error en send_weekly_report: {e}")
            logger.debug(traceback.format_exc())
            return False


    def send_model_retrained_notification(
        self,
        recipients: List[str],
        training_data: Dict,
        old_metrics: Dict,
        new_metrics: Dict,
        improvements: Optional[Dict[str, float]] = None
    ) -> bool:
        """
        🎯 Enviar notificación de modelo re-entrenado.
        
        Args:
            recipients: Lista de emails destino
            training_data: Diccionario con información del entrenamiento:
                - training_date: datetime
                - model_name: str
                - algorithm: str (ej: 'LSTM', 'Prophet', 'SARIMA')
                - dataset_size: int (número de samples)
                - training_duration_seconds: int
                - features_used: List[str]
                - data_quality: str (ej: 'Excelente', 'Buena')
            old_metrics: Diccionario con métricas del modelo anterior:
                - mae: float
                - rmse: float
                - r2: float
                - mape: float
                - training_time: int (segundos)
            new_metrics: Diccionario con métricas del nuevo modelo (misma estructura)
            improvements: Diccionario opcional con % de mejora {'mae': -12.5, 'rmse': -8.3, ...}
            
        Returns:
            True si se envió correctamente
            
        Example:
            >>> emailer = EmailReporter()
            >>> emailer.send_model_retrained_notification(
            ...     recipients=['admin@example.com'],
            ...     training_data={
            ...         'training_date': datetime.now(),
            ...         'model_name': 'LSTM_v2.1',
            ...         'algorithm': 'LSTM',
            ...         'dataset_size': 50000,
            ...         'training_duration_seconds': 3600,
            ...         'features_used': ['hour', 'day_of_week', 'month'],
            ...         'data_quality': 'Excelente'
            ...     },
            ...     old_metrics={'mae': 0.145, 'rmse': 0.234, 'r2': 0.89, 'mape': 12.5},
            ...     new_metrics={'mae': 0.127, 'rmse': 0.215, 'r2': 0.92, 'mape': 10.8}
            ... )
        """
        try:
            logger.info(f"🎯 Enviando notificación de modelo re-entrenado")
            
            # Calcular mejoras si no se proporcionaron
            if improvements is None:
                improvements = {}
                for metric in ['mae', 'rmse', 'r2', 'mape']:
                    if metric in old_metrics and metric in new_metrics:
                        old_val = old_metrics[metric]
                        new_val = new_metrics[metric]
                        
                        # Para R², mayor es mejor; para otros, menor es mejor
                        if metric == 'r2':
                            improvement = ((new_val - old_val) / old_val) * 100 if old_val != 0 else 0
                        else:
                            improvement = ((old_val - new_val) / old_val) * 100 if old_val != 0 else 0
                        
                        improvements[metric] = improvement
            
            # Formatear duración
            duration_secs = training_data.get('training_duration_seconds', 0)
            if duration_secs < 60:
                duration_str = f"{duration_secs} segundos"
            elif duration_secs < 3600:
                duration_str = f"{duration_secs // 60} minutos"
            else:
                hours = duration_secs // 3600
                minutes = (duration_secs % 3600) // 60
                duration_str = f"{hours}h {minutes}m"
            
            # Preparar datos para template
            template_data = {
                # Información básica
                'training_date': training_data.get('training_date', datetime.now()).strftime('%d/%m/%Y %H:%M:%S'),
                'model_name': training_data.get('model_name', 'Modelo Predictor'),
                'generation_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                
                # Detalles del entrenamiento
                'algorithm': training_data.get('algorithm', 'LSTM'),
                'dataset_size': training_data.get('dataset_size', 0),
                'training_duration': duration_str,
                'training_duration_seconds': duration_secs,
                'features_used': ', '.join(training_data.get('features_used', [])),
                'data_quality': training_data.get('data_quality', 'Buena'),
                
                # Métricas antiguas
                'old_metrics': {
                    'mae': old_metrics.get('mae', 0.0),
                    'rmse': old_metrics.get('rmse', 0.0),
                    'r2': old_metrics.get('r2', 0.0),
                    'mape': old_metrics.get('mape', 0.0),
                    'training_time': old_metrics.get('training_time', 0)
                },
                
                # Métricas nuevas
                'new_metrics': {
                    'mae': new_metrics.get('mae', 0.0),
                    'rmse': new_metrics.get('rmse', 0.0),
                    'r2': new_metrics.get('r2', 0.0),
                    'mape': new_metrics.get('mape', 0.0),
                    'training_time': duration_secs
                },
                
                # Mejoras
                'improvement_percent': improvements,
                
                # Determinar si hay regresión
                'has_regression': any(imp < -5 for imp in improvements.values()),
                'has_significant_improvement': any(imp > 10 for imp in improvements.values())
            }
            
            # Cargar y renderizar template
            try:
                template = self.jinja_env.get_template('email_model_retrained.html')
                html_body = template.render(**template_data)
                logger.debug(f"✅ Template de modelo re-entrenado renderizado: {len(html_body):,} caracteres")
            except Exception as e:
                logger.error(f"❌ Error renderizando template modelo: {e}")
                raise ValueError(f"Error en template email_model_retrained.html: {e}")
            
            # Crear asunto
            improvement_avg = sum(improvements.values()) / len(improvements) if improvements else 0
            if improvement_avg > 10:
                subject = "🎯 ¡Modelo Mejorado! - Re-entrenamiento Completado con Éxito"
            elif improvement_avg > 0:
                subject = "✅ Modelo Re-entrenado - DomusAI"
            else:
                subject = "ℹ️ Modelo Re-entrenado - Revisar Métricas"
            
            # Log de información
            logger.info(f"   Modelo: {training_data.get('model_name', 'N/A')}")
            logger.info(f"   Duración: {duration_str}")
            logger.info(f"   Mejora promedio: {improvement_avg:+.1f}%")
            logger.info(f"   MAE: {old_metrics.get('mae', 0):.4f} → {new_metrics.get('mae', 0):.4f}")
            
            # Enviar email
            success = self.send_email(
                recipients=recipients,
                subject=subject,
                html_body=html_body,
                attachments=[]
            )
            
            if success:
                logger.info(f"✅ Notificación de modelo re-entrenado enviada exitosamente")
            else:
                logger.error(f"❌ Error enviando notificación de modelo")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ Error en send_model_retrained_notification: {e}")
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

