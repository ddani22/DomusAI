"""
Script para validar la configuración YAML del scheduler

Uso:
    python scripts/validate_config.py
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
import os

def validate_config():
    """Validar archivo de configuración YAML"""
    
    print("=" * 70)
    print("🔍 Validando configuración del scheduler")
    print("=" * 70)
    print()
    
    config_path = Path('config/scheduler_config.yaml')
    
    if not config_path.exists():
        print(f"❌ Archivo no encontrado: {config_path}")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"✅ Archivo YAML válido: {config_path}")
        print()
        
        # Validar secciones principales
        required_sections = ['general', 'jobs', 'notifications', 'error_handling']
        print("📋 Validando secciones requeridas...")
        for section in required_sections:
            if section in config:
                print(f"   ✅ {section}")
            else:
                print(f"   ❌ {section} - FALTANTE")
                return False
        
        print()
        print("🎯 Configuración actual:")
        print("-" * 70)
        
        # General
        general = config.get('general', {})
        print(f"\n⚙️ GENERAL:")
        print(f"   Timezone: {general.get('timezone', 'N/A')}")
        print(f"   Log level: {general.get('log_level', 'N/A')}")
        
        # Jobs
        jobs = config.get('jobs', {})
        print(f"\n📋 JOBS:")
        
        anomaly = jobs.get('anomaly_detection', {})
        print(f"   Detección de anomalías:")
        print(f"      Habilitado: {anomaly.get('enabled', False)}")
        print(f"      Intervalo: {anomaly.get('interval_minutes', 0)} minutos")
        
        retraining = jobs.get('model_retraining', {})
        print(f"   Re-entrenamiento:")
        print(f"      Habilitado: {retraining.get('enabled', False)}")
        print(f"      Cron: {retraining.get('cron', 'N/A')}")
        print(f"      Días mínimos: {retraining.get('min_days_between', 0)}")
        
        daily = jobs.get('daily_report', {})
        print(f"   Reporte diario:")
        print(f"      Habilitado: {daily.get('enabled', False)}")
        print(f"      Cron: {daily.get('cron', 'N/A')}")
        
        # Notificaciones
        notif = config.get('notifications', {})
        print(f"\n📧 NOTIFICACIONES:")
        print(f"   Habilitadas: {notif.get('enabled', False)}")
        print(f"   Email en éxito: {notif.get('email_on_success', False)}")
        print(f"   Email en error: {notif.get('email_on_error', False)}")
        
        recipients = notif.get('default_recipients', [])
        print(f"   Destinatarios: {len(recipients)}")
        for i, email in enumerate(recipients, 1):
            print(f"      {i}. {email}")
        
        # Error handling
        error = config.get('error_handling', {})
        print(f"\n🔧 ERROR HANDLING:")
        print(f"   Max reintentos: {error.get('max_retries', 0)}")
        print(f"   Delays: {error.get('retry_delays', [])}")
        
        circuit = error.get('circuit_breaker', {})
        print(f"   Circuit breaker:")
        print(f"      Habilitado: {circuit.get('enabled', False)}")
        print(f"      Threshold: {circuit.get('failure_threshold', 0)}")
        
        # Variables de entorno
        print(f"\n🌐 VARIABLES DE ENTORNO:")
        env_vars = [
            'DOMUSAI_TIMEZONE',
            'DOMUSAI_ANOMALY_ENABLED',
            'DOMUSAI_ANOMALY_INTERVAL',
            'DOMUSAI_RETRAINING_ENABLED',
            'DOMUSAI_EMAIL_ENABLED'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"   ✅ {var} = {value}")
            else:
                print(f"   ⚪ {var} = (no definida)")
        
        print()
        print("=" * 70)
        print("✅ Validación completada - Configuración válida")
        print("=" * 70)
        
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ Error al parsear YAML: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = validate_config()
    sys.exit(0 if success else 1)
