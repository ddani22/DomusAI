"""
DomusAI - Validación de Configuración de Email

Este script valida que la configuración de email esté correcta
y permite enviar emails de prueba.

Uso:
    python scripts/validate_email_config.py
    python scripts/validate_email_config.py --test-email tu_email@gmail.com

Autor: DomusAI Team
Fecha: Octubre 2025
"""

import sys
import os
from pathlib import Path
import argparse

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Cargar variables de entorno
load_dotenv()


def print_header(title: str):
    """Imprime un header visual."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def check_env_variables():
    """Verifica que todas las variables de entorno estén configuradas."""
    print_header("📋 VERIFICACIÓN DE VARIABLES DE ENTORNO")
    
    required_vars = {
        'SMTP_HOST': os.getenv('SMTP_HOST'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SENDER_EMAIL': os.getenv('SENDER_EMAIL'),
        'SENDER_PASSWORD': os.getenv('SENDER_PASSWORD'),
    }
    
    optional_vars = {
        'DEFAULT_EMAIL_RECIPIENTS': os.getenv('DEFAULT_EMAIL_RECIPIENTS'),
        'ENABLE_ANOMALY_ALERTS': os.getenv('ENABLE_ANOMALY_ALERTS'),
        'SCHEDULER_ENABLED': os.getenv('SCHEDULER_ENABLED'),
    }
    
    all_ok = True
    
    # Verificar variables obligatorias
    print("\n✅ Variables OBLIGATORIAS:")
    for var, value in required_vars.items():
        if value:
            # Ocultar contraseña parcialmente
            if var == 'SENDER_PASSWORD':
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
                print(f"   ✅ {var:25} = {masked}")
            else:
                print(f"   ✅ {var:25} = {value}")
        else:
            print(f"   ❌ {var:25} = [NO CONFIGURADA]")
            all_ok = False
    
    # Verificar variables opcionales
    print("\n🔧 Variables OPCIONALES:")
    for var, value in optional_vars.items():
        if value:
            print(f"   ✅ {var:25} = {value}")
        else:
            print(f"   ⚠️  {var:25} = [No definida - usando defaults]")
    
    return all_ok, required_vars


def test_smtp_connection(smtp_host, smtp_port, sender_email, sender_password):
    """Prueba la conexión SMTP."""
    print_header("🔌 PRUEBA DE CONEXIÓN SMTP")
    
    try:
        print(f"\n📡 Conectando a {smtp_host}:{smtp_port}...")
        
        # Crear conexión
        server = smtplib.SMTP(smtp_host, int(smtp_port), timeout=10)
        print("   ✅ Conexión establecida")
        
        # Iniciar TLS
        print("   🔐 Iniciando TLS...")
        server.starttls()
        print("   ✅ TLS activado")
        
        # Autenticar
        print(f"   🔑 Autenticando como {sender_email}...")
        server.login(sender_email, sender_password)
        print("   ✅ Autenticación exitosa")
        
        # Cerrar conexión
        server.quit()
        print("\n✅ CONEXIÓN SMTP EXITOSA")
        return True
    
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ ERROR DE AUTENTICACIÓN:")
        print(f"   {e}")
        print("\n💡 POSIBLES SOLUCIONES:")
        print("   1. Verifica que SENDER_EMAIL sea correcto")
        print("   2. Si usas Gmail, genera un App Password:")
        print("      → https://myaccount.google.com/apppasswords")
        print("   3. NO uses tu contraseña normal de Gmail")
        print("   4. Verifica que la autenticación de 2 pasos esté activada en Gmail")
        return False
    
    except smtplib.SMTPConnectError as e:
        print(f"\n❌ ERROR DE CONEXIÓN:")
        print(f"   {e}")
        print("\n💡 POSIBLES SOLUCIONES:")
        print("   1. Verifica SMTP_HOST (ej: smtp.gmail.com)")
        print("   2. Verifica SMTP_PORT (587 para TLS, 465 para SSL)")
        print("   3. Revisa tu firewall/antivirus")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO:")
        print(f"   {e}")
        return False


def send_test_email(smtp_host, smtp_port, sender_email, sender_password, recipient):
    """Envía un email de prueba."""
    print_header(f"📧 ENVIANDO EMAIL DE PRUEBA A {recipient}")
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = "🧪 DomusAI - Test de Configuración de Email"
        
        # Cuerpo HTML
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #3b82f6;
                    margin-top: 0;
                }}
                .success {{
                    background: #dcfce7;
                    border: 2px solid #10b981;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .info {{
                    background: #f3f4f6;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 ¡Configuración de Email Exitosa!</h1>
                
                <div class="success">
                    <p><strong>✅ El sistema de email de DomusAI está funcionando correctamente.</strong></p>
                </div>
                
                <div class="info">
                    <h3>📋 Detalles de la Prueba:</h3>
                    <ul>
                        <li><strong>Servidor SMTP:</strong> {smtp_host}:{smtp_port}</li>
                        <li><strong>Remitente:</strong> {sender_email}</li>
                        <li><strong>Destinatario:</strong> {recipient}</li>
                        <li><strong>Fecha:</strong> {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</li>
                    </ul>
                </div>
                
                <h3>🚀 Próximos Pasos:</h3>
                <ol>
                    <li>✅ La configuración de email está completa</li>
                    <li>🔄 El scheduler puede enviar reportes automáticos</li>
                    <li>🚨 Las alertas de anomalías se enviarán en tiempo real</li>
                    <li>📊 Los reportes diarios/semanales/mensuales llegarán según configuración</li>
                </ol>
                
                <div class="footer">
                    <p><strong>DomusAI</strong> - Sistema de Monitoreo Energético</p>
                    <p>Este es un email automático generado por el sistema de validación.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # Enviar
        print("\n📤 Enviando mensaje...")
        server = smtplib.SMTP(smtp_host, int(smtp_port), timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print("✅ EMAIL ENVIADO EXITOSAMENTE")
        print(f"\n📬 Revisa la bandeja de entrada de: {recipient}")
        print("   (Puede tardar algunos segundos en llegar)")
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR ENVIANDO EMAIL:")
        print(f"   {e}")
        return False


def check_email_templates():
    """Verifica que los templates de email existan."""
    print_header("📄 VERIFICACIÓN DE TEMPLATES HTML")
    
    templates_dir = project_root / 'reports' / 'email_templates'
    
    required_templates = [
        'monthly_report_email.html',
        'anomaly_alert_email.html',
        'email_daily_report.html',
        'email_weekly_report.html',
        'email_model_retrained.html'
    ]
    
    all_ok = True
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            size = template_path.stat().st_size
            print(f"   ✅ {template:35} ({size:,} bytes)")
        else:
            print(f"   ❌ {template:35} [NO ENCONTRADO]")
            all_ok = False
    
    return all_ok


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Validar configuración de email de DomusAI'
    )
    parser.add_argument(
        '--test-email',
        type=str,
        help='Email para enviar prueba (opcional)',
        default=None
    )
    parser.add_argument(
        '--skip-send',
        action='store_true',
        help='Solo validar configuración, no enviar email'
    )
    
    args = parser.parse_args()
    
    print("\n")
    print("📧 DomusAI - Validación de Configuración de Email")
    print("=" * 80)
    
    # 1. Verificar variables de entorno
    vars_ok, required_vars = check_env_variables()
    
    if not vars_ok:
        print("\n❌ CONFIGURACIÓN INCOMPLETA")
        print("   Edita el archivo .env y completa las variables faltantes")
        return 1
    
    # 2. Verificar templates
    templates_ok = check_email_templates()
    
    if not templates_ok:
        print("\n⚠️  ADVERTENCIA: Algunos templates faltan")
        print("   El sistema funcionará, pero algunos reportes no se generarán")
    
    # 3. Probar conexión SMTP
    smtp_ok = test_smtp_connection(
        required_vars['SMTP_HOST'],
        required_vars['SMTP_PORT'],
        required_vars['SENDER_EMAIL'],
        required_vars['SENDER_PASSWORD']
    )
    
    if not smtp_ok:
        print("\n❌ CONFIGURACIÓN DE SMTP INCORRECTA")
        return 1
    
    # 4. Enviar email de prueba (opcional)
    if not args.skip_send:
        # Determinar destinatario
        if args.test_email:
            recipient = args.test_email
        else:
            default_recipients = os.getenv('DEFAULT_EMAIL_RECIPIENTS', '')
            if default_recipients:
                recipient = default_recipients.split(',')[0].strip()
            else:
                recipient = required_vars['SENDER_EMAIL']
        
        email_ok = send_test_email(
            required_vars['SMTP_HOST'],
            required_vars['SMTP_PORT'],
            required_vars['SENDER_EMAIL'],
            required_vars['SENDER_PASSWORD'],
            recipient
        )
        
        if not email_ok:
            print("\n⚠️  Error enviando email de prueba")
            print("   La conexión funciona pero hubo un problema al enviar")
            return 1
    
    # Resumen final
    print_header("📊 RESUMEN DE VALIDACIÓN")
    print("\n✅ Variables de entorno: CORRECTO")
    print(f"{'✅' if templates_ok else '⚠️ '} Templates HTML: {'COMPLETO' if templates_ok else 'INCOMPLETO'}")
    print("✅ Conexión SMTP: EXITOSA")
    if not args.skip_send:
        print("✅ Envío de email: FUNCIONAL")
    
    print("\n" + "=" * 80)
    print("🎉 ¡CONFIGURACIÓN DE EMAIL COMPLETA Y FUNCIONAL!")
    print("=" * 80)
    print("\n🚀 El sistema DomusAI está listo para enviar emails automáticos:")
    print("   • Reportes diarios (8:00 AM)")
    print("   • Reportes semanales (Lunes 9:00 AM)")
    print("   • Reportes mensuales (día 1, 10:00 AM)")
    print("   • Alertas de anomalías (tiempo real)")
    print("   • Notificaciones de modelo re-entrenado")
    print("\n💡 Para ejecutar el scheduler:")
    print("   python scripts/auto_training_scheduler.py")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
