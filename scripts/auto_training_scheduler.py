"""
🤖 DomusAI - Sistema de Scheduling Automático 24/7

Este módulo implementa el scheduler que ejecuta tareas periódicas de forma automática:
- Detección de anomalías cada hora
- Re-entrenamiento de modelos cada 7 días
- Generación de reportes diarios, semanales y mensuales
- Envío automático de emails

Características:
- Ejecución 24/7 en segundo plano
- Configuración mediante YAML
- Logging exhaustivo
- Error handling robusto
- Reintentos automáticos

Uso:
    python scripts/auto_training_scheduler.py

Para detener:
    Ctrl+C (KeyboardInterrupt)
"""

import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import signal

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

# DomusAI imports
from src.auto_trainer import AutoTrainer
from src.anomalies import AnomalyDetector
from src.database import get_db_reader
from src.reporting import ReportGenerator
import pandas as pd
import json
import joblib
from pathlib import Path
import yaml
import traceback
from functools import wraps
from typing import List, Callable


# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

def retry_with_backoff(max_retries: int = 3, delays: Optional[List[int]] = None):
    """
    Decorador para reintentar funciones con backoff exponencial
    
    Args:
        max_retries: Número máximo de reintentos
        delays: Lista de delays en segundos (ej: [60, 300, 900])
    
    Example:
        @retry_with_backoff(max_retries=3, delays=[60, 300, 900])
        def my_function():
            # Código que puede fallar
            pass
    """
    if delays is None:
        delays = [60, 300, 900]  # 1 min, 5 min, 15 min
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = delays[min(attempt, len(delays) - 1)]  # type: ignore
                        logger = logging.getLogger('Scheduler')
                        logger.warning(f"   ⚠️ Intento {attempt + 1}/{max_retries + 1} falló: {e}")
                        logger.info(f"   ⏳ Esperando {delay} segundos antes de reintentar...")
                        time.sleep(delay)
                    else:
                        logger = logging.getLogger('Scheduler')
                        logger.error(f"   ❌ Todos los reintentos fallaron ({max_retries + 1} intentos)")
                        raise last_exception
            
            # Este código nunca se ejecuta, pero satisface el type checker
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def load_config_from_yaml(config_path: str = 'config/scheduler_config.yaml') -> Dict[str, Any]:
    """
    Cargar configuración desde archivo YAML
    
    Permite overrides con variables de entorno:
    - DOMUSAI_TIMEZONE
    - DOMUSAI_ANOMALY_ENABLED
    - DOMUSAI_ANOMALY_INTERVAL
    - DOMUSAI_RETRAINING_ENABLED
    - DOMUSAI_RETRAINING_MIN_DAYS
    - DOMUSAI_EMAIL_ENABLED
    
    Args:
        config_path: Ruta al archivo YAML de configuración
        
    Returns:
        Dict con configuración completa
    """
    # Cargar configuración base desde YAML
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"⚠️ Archivo de configuración no encontrado: {config_path}")
        print("   Usando configuración por defecto...")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"✅ Configuración cargada desde: {config_path}")
        
        # Aplicar overrides desde variables de entorno
        env_overrides = {
            'DOMUSAI_TIMEZONE': ('general', 'timezone'),
            'DOMUSAI_ANOMALY_ENABLED': ('jobs', 'anomaly_detection', 'enabled'),
            'DOMUSAI_ANOMALY_INTERVAL': ('jobs', 'anomaly_detection', 'interval_minutes'),
            'DOMUSAI_RETRAINING_ENABLED': ('jobs', 'model_retraining', 'enabled'),
            'DOMUSAI_RETRAINING_MIN_DAYS': ('jobs', 'model_retraining', 'min_days_between'),
            'DOMUSAI_EMAIL_ENABLED': ('notifications', 'enabled'),
        }
        
        for env_var, config_path_tuple in env_overrides.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Navegar al path correcto en el dict
                current = config
                for key in config_path_tuple[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Convertir tipo si es necesario
                last_key = config_path_tuple[-1]
                if env_value.lower() in ['true', 'false']:
                    current[last_key] = env_value.lower() == 'true'
                elif env_value.isdigit():
                    current[last_key] = int(env_value)
                else:
                    current[last_key] = env_value
                
                print(f"   ⚙️ Override desde {env_var}: {current[last_key]}")
        
        return config
        
    except yaml.YAMLError as e:
        print(f"❌ Error al parsear YAML: {e}")
        print("   Usando configuración por defecto...")
        return {}
    except Exception as e:
        print(f"❌ Error inesperado al cargar configuración: {e}")
        print("   Usando configuración por defecto...")
        return {}


def setup_scheduler_logging():
    """Configurar sistema de logging para el scheduler"""
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Configurar formato
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Logger principal del scheduler
    logger = logging.getLogger('Scheduler')
    logger.setLevel(logging.INFO)
    
    # Handler para archivo
    file_handler = logging.FileHandler('logs/scheduler.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# CLASE PRINCIPAL: SchedulerManager
# ============================================================================

class SchedulerManager:
    """
    🤖 Gestor del Sistema de Scheduling 24/7
    
    Responsabilidades:
    1. Inicializar APScheduler
    2. Configurar jobs programados
    3. Ejecutar tareas en horarios definidos
    4. Manejar errores y reintentos
    5. Logging exhaustivo
    6. Shutdown graceful
    
    Jobs implementados:
    - hourly_anomaly_detection: Detectar anomalías cada hora
    - daily_retraining_check: Verificar si re-entrenar modelos (3 AM)
    - generate_daily_report: Reporte diario (8 AM)
    - generate_weekly_report: Reporte semanal (Lunes 9 AM)
    - generate_monthly_report: Reporte mensual (Día 1, 10 AM)
    
    Example:
        >>> manager = SchedulerManager()
        >>> manager.start()
        >>> # Scheduler corre 24/7 hasta Ctrl+C
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar SchedulerManager
        
        Args:
            config: Diccionario de configuración (opcional)
                   Si no se provee, carga desde config/scheduler_config.yaml
        """
        self.logger = setup_scheduler_logging()
        
        # Cargar configuración desde YAML si no se provee
        if config is None:
            self.logger.info("📄 Cargando configuración desde YAML...")
            config = load_config_from_yaml()
        
        # Si load_config_from_yaml falló o retornó vacío, usar defaults
        self.config = config if config else self._get_default_config()
        
        self.scheduler: Optional[BackgroundScheduler] = None
        self.db_reader = None
        
        # Contadores de estadísticas
        self.stats = {
            'jobs_executed': 0,
            'jobs_failed': 0,
            'anomalies_detected': 0,
            'models_retrained': 0,
            'reports_generated': 0,
            'emails_sent': 0
        }
        
        self.logger.info("=" * 70)
        self.logger.info("🤖 SchedulerManager DomusAI inicializado")
        self.logger.info("=" * 70)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Obtener configuración por defecto
        
        Returns:
            Dict con configuración por defecto del scheduler
        """
        return {
            'timezone': 'Europe/Madrid',  # Ajustar a tu timezone
            'jobs': {
                'anomaly_detection': {
                    'enabled': True,
                    'interval_minutes': 60  # Cada hora
                },
                'model_retraining': {
                    'enabled': True,
                    'cron': '0 3 * * *',  # 3:00 AM diario
                    'min_days_between': 7
                },
                'daily_report': {
                    'enabled': True,
                    'cron': '0 8 * * *',  # 8:00 AM diario
                },
                'weekly_report': {
                    'enabled': True,
                    'cron': '0 9 * * 1',  # 9:00 AM cada lunes
                },
                'monthly_report': {
                    'enabled': True,
                    'cron': '0 10 1 * *',  # 10:00 AM día 1 de mes
                }
            },
            'notifications': {
                'enabled': True,
                'email_on_error': True,
                'email_on_success': False
            }
        }
    
    def initialize_scheduler(self):
        """
        Inicializar APScheduler con configuración
        """
        self.logger.info("🔧 Inicializando APScheduler...")
        
        # Obtener timezone desde config (YAML o default)
        timezone = self.config.get('general', {}).get('timezone', 'Europe/Madrid')
        
        # Crear scheduler con BackgroundScheduler (no-blocking)
        self.scheduler = BackgroundScheduler(timezone=timezone)
        
        # Agregar listeners para eventos
        self.scheduler.add_listener(
            self._on_job_executed,
            EVENT_JOB_EXECUTED
        )
        
        self.scheduler.add_listener(
            self._on_job_error,
            EVENT_JOB_ERROR
        )
        
        self.logger.info(f"✅ APScheduler inicializado (timezone: {timezone})")
    
    def add_jobs(self):
        """
        Agregar todos los jobs programados al scheduler
        """
        assert self.scheduler is not None, "Scheduler debe estar inicializado antes de agregar jobs"
        
        self.logger.info("📋 Agregando jobs al scheduler...")
        
        jobs_config = self.config.get('jobs', {})
        
        # Job 1: Detección de anomalías (cada hora)
        if jobs_config.get('anomaly_detection', {}).get('enabled', True):
            interval = jobs_config['anomaly_detection'].get('interval_minutes', 60)
            self.scheduler.add_job(
                func=self.hourly_anomaly_detection,
                trigger=IntervalTrigger(minutes=interval),
                id='anomaly_detection',
                name='Detección de Anomalías',
                max_instances=1,  # Solo 1 instancia corriendo a la vez
                replace_existing=True
            )
            self.logger.info(f"   ✅ Job agregado: Detección de Anomalías (cada {interval} min)")
        
        # Job 2: Re-entrenamiento de modelos (3 AM diario)
        if jobs_config.get('model_retraining', {}).get('enabled', True):
            cron = jobs_config['model_retraining'].get('cron', '0 3 * * *')
            self.scheduler.add_job(
                func=self.daily_retraining_check,
                trigger=CronTrigger.from_crontab(cron),
                id='model_retraining',
                name='Re-entrenamiento de Modelos',
                max_instances=1,
                replace_existing=True
            )
            self.logger.info(f"   ✅ Job agregado: Re-entrenamiento de Modelos ({cron})")
        
        # Job 3: Reporte diario (8 AM)
        if jobs_config.get('daily_report', {}).get('enabled', True):
            cron = jobs_config['daily_report'].get('cron', '0 8 * * *')
            self.scheduler.add_job(
                func=self.generate_daily_report,
                trigger=CronTrigger.from_crontab(cron),
                id='daily_report',
                name='Reporte Diario',
                max_instances=1,
                replace_existing=True
            )
            self.logger.info(f"   ✅ Job agregado: Reporte Diario ({cron})")
        
        # Job 4: Reporte semanal (Lunes 9 AM)
        if jobs_config.get('weekly_report', {}).get('enabled', True):
            cron = jobs_config['weekly_report'].get('cron', '0 9 * * 1')
            self.scheduler.add_job(
                func=self.generate_weekly_report,
                trigger=CronTrigger.from_crontab(cron),
                id='weekly_report',
                name='Reporte Semanal',
                max_instances=1,
                replace_existing=True
            )
            self.logger.info(f"   ✅ Job agregado: Reporte Semanal ({cron})")
        
        # Job 5: Reporte mensual (Día 1, 10 AM)
        if jobs_config.get('monthly_report', {}).get('enabled', True):
            cron = jobs_config['monthly_report'].get('cron', '0 10 1 * *')
            self.scheduler.add_job(
                func=self.generate_monthly_report,
                trigger=CronTrigger.from_crontab(cron),
                id='monthly_report',
                name='Reporte Mensual',
                max_instances=1,
                replace_existing=True
            )
            self.logger.info(f"   ✅ Job agregado: Reporte Mensual ({cron})")
        
        self.logger.info(f"✅ Total de jobs agregados: {len(self.scheduler.get_jobs())}")
    
    # ========================================================================
    # EVENT LISTENERS
    # ========================================================================
    
    def _on_job_executed(self, event):
        """Callback cuando un job se ejecuta exitosamente"""
        self.stats['jobs_executed'] += 1
        self.logger.info(f"✅ Job ejecutado: {event.job_id}")
    
    def _on_job_error(self, event):
        """Callback cuando un job falla"""
        self.stats['jobs_failed'] += 1
        self.logger.error(f"❌ Job falló: {event.job_id} - {event.exception}")
    
    # ========================================================================
    # JOB FUNCTIONS (Implementaciones básicas - se completarán en subtareas)
    # ========================================================================
    
    def hourly_anomaly_detection(self):
        """
        🕐 Job: Detección de anomalías cada hora
        
        Flujo:
        1. Obtener últimas 60 lecturas de Railway (última hora)
        2. Cargar modelo Isolation Forest
        3. Detectar anomalías
        4. Si hay anomalías → marcar en Railway
        5. Calcular severidad y enviar email si necesario
        6. Actualizar estadísticas
        """
        self.logger.info("🕐 [HOURLY] Ejecutando detección de anomalías...")
        start_time = time.time()
        
        try:
            # PASO 1: Obtener datos recientes de Railway
            self.logger.info("   📊 Obteniendo últimas 60 lecturas de Railway...")
            
            if self.db_reader is None:
                self.db_reader = get_db_reader()
            
            # Obtener última hora de datos
            df = self.db_reader.get_recent_readings(hours=1)
            
            if df is None or df.empty:
                self.logger.warning("   ⚠️ No hay datos recientes en Railway")
                return
            
            num_readings = len(df)
            self.logger.info(f"   ✅ {num_readings} lecturas obtenidas")
            
            # Validar datos mínimos
            if num_readings < 30:
                self.logger.warning(f"   ⚠️ Datos insuficientes ({num_readings} < 30)")
                self.logger.info("   ℹ️ Se necesitan al menos 30 lecturas para detección confiable")
                return
            
            # PASO 2: Cargar modelo de detección de anomalías
            self.logger.info("   🤖 Cargando modelo de detección...")
            
            model_path = Path('models/best_isolation_forest.pkl')
            if not model_path.exists():
                self.logger.error(f"   ❌ Modelo no encontrado: {model_path}")
                self.logger.info("   ℹ️ Ejecutar AutoTrainer primero para generar el modelo")
                return
            
            # Cargar modelo con joblib
            try:
                anomaly_model = joblib.load(model_path)
                self.logger.info(f"   ✅ Modelo cargado: {model_path}")
            except Exception as e:
                self.logger.error(f"   ❌ Error al cargar modelo: {e}")
                return
            
            # PASO 3: Detectar anomalías
            self.logger.info("   🔍 Detectando anomalías...")
            
            # Preparar features para el modelo
            feature_cols = ['Global_active_power', 'Global_reactive_power', 
                          'Voltage', 'Global_intensity']
            
            # Verificar que tenemos todas las columnas necesarias
            missing_cols = [col for col in feature_cols if col not in df.columns]
            if missing_cols:
                self.logger.error(f"   ❌ Columnas faltantes: {missing_cols}")
                return
            
            X = df[feature_cols].copy()
            
            # Manejar valores nulos si existen
            if X.isnull().any().any():
                self.logger.warning("   ⚠️ Datos con valores nulos, rellenando con media...")
                X = X.fillna(X.mean())
            
            # Predecir anomalías (-1 = anomalía, 1 = normal)
            predictions = anomaly_model.predict(X)
            
            # Convertir a booleano (True = anomalía)
            df['is_anomaly'] = predictions == -1
            
            # PASO 4: Contar anomalías
            num_anomalies = df['is_anomaly'].sum()
            
            if num_anomalies == 0:
                self.logger.info("   ✅ Sin anomalías detectadas en la última hora")
                duration = time.time() - start_time
                self.logger.info(f"   ⏱️ Detección completada en {duration:.1f} segundos")
                return
            
            # Hay anomalías - procesar
            self.logger.warning(f"   ⚠️ {num_anomalies} anomalías detectadas:")
            
            # Obtener detalles de las anomalías
            anomalies_df = df[df['is_anomaly'] == True].copy()
            
            for idx, row in anomalies_df.iterrows():
                timestamp = row.name if isinstance(row.name, pd.Timestamp) else row.get('Datetime', 'Unknown')
                power = row.get('Global_active_power', 0)
                self.logger.warning(f"      • {timestamp} - {power:.2f} kW")
            
            # PASO 5: Calcular severidad
            avg_power = anomalies_df['Global_active_power'].mean()
            max_power = anomalies_df['Global_active_power'].max()
            
            # Criterios de severidad
            if num_anomalies > 5 or max_power > 8:
                severity = 'HIGH'
                emoji = '🔴'
            elif num_anomalies > 2 or max_power > 5:
                severity = 'MEDIUM'
                emoji = '🟡'
            else:
                severity = 'LOW'
                emoji = '🟢'
            
            self.logger.info(f"   {emoji} Severidad: {severity}")
            self.logger.info(f"      Potencia promedio: {avg_power:.2f} kW")
            self.logger.info(f"      Potencia máxima: {max_power:.2f} kW")
            
            # PASO 6: Marcar anomalías en Railway (TODO en próxima versión)
            # Por ahora solo logeamos, en el futuro se hará UPDATE a Railway
            self.logger.info("   📝 Marcado de anomalías en Railway: PENDIENTE")
            self.logger.info("   ℹ️ (Requiere permisos de escritura en Railway)")
            
            # PASO 7: Enviar email si severidad >= MEDIUM (TODO)
            if severity in ['MEDIUM', 'HIGH']:
                self.logger.info(f"   📧 Email de alerta necesario (severidad: {severity})")
                self.logger.info("   ℹ️ Envío de email: PENDIENTE (implementar en siguiente versión)")
                # TODO: Implementar envío de email
                # from src.email_sender import send_anomaly_alert
                # send_anomaly_alert(anomaly_summary)
                # self.stats['emails_sent'] += 1
            
            # PASO 8: Actualizar estadísticas
            self.stats['anomalies_detected'] += num_anomalies
            
            duration = time.time() - start_time
            self.logger.info(f"   ✅ Detección completada en {duration:.1f} segundos")
            
        except Exception as e:
            self.logger.error(f"   ❌ Error en detección de anomalías: {e}")
            import traceback
            self.logger.error(f"   Stack trace:\n{traceback.format_exc()}")
            raise
    
    def daily_retraining_check(self):
        """
        🌙 Job: Verificar si necesita re-entrenamiento (3 AM)
        
        Flujo:
        1. Leer última fecha de entrenamiento
        2. Calcular días transcurridos
        3. Si >= 7 días → ejecutar AutoTrainer
        4. Verificar resultado y actualizar estadísticas
        5. Enviar notificación
        """
        self.logger.info("🌙 [DAILY] Verificando necesidad de re-entrenamiento...")
        start_time = time.time()
        
        try:
            # PASO 1: Verificar última fecha de entrenamiento
            history_path = Path('logs/metrics_history.json')
            
            if not history_path.exists():
                self.logger.warning("   ⚠️ No hay historial de entrenamiento")
                self.logger.info("   🚀 Primera ejecución - iniciando entrenamiento...")
                should_train = True
                days_since = 999  # Valor alto para forzar entrenamiento
            else:
                try:
                    with open(history_path, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                    
                    if not history:
                        self.logger.warning("   ⚠️ Historial vacío")
                        should_train = True
                        days_since = 999
                    else:
                        # Obtener última entrada
                        last_entry = history[-1]
                        last_date_str = last_entry.get('timestamp', '')
                        
                        if not last_date_str:
                            self.logger.warning("   ⚠️ Sin timestamp en historial")
                            should_train = True
                            days_since = 999
                        else:
                            # Parsear fecha
                            last_date = datetime.fromisoformat(last_date_str)
                            days_since = (datetime.now() - last_date).days
                            
                            self.logger.info(f"   📅 Último entrenamiento: {last_date.strftime('%Y-%m-%d %H:%M:%S')}")
                            self.logger.info(f"   ⏱️ Días transcurridos: {days_since}")
                            
                            # Obtener configuración de días mínimos
                            min_days = self.config['jobs']['model_retraining'].get('min_days_between', 7)
                            
                            if days_since < min_days:
                                self.logger.info(f"   ✅ Modelo reciente, próximo entrenamiento en {min_days - days_since} días")
                                return
                            else:
                                self.logger.info(f"   🚀 Necesita re-entrenamiento (>= {min_days} días)")
                                should_train = True
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"   ❌ Error al leer historial: {e}")
                    self.logger.info("   🚀 Continuando con entrenamiento...")
                    should_train = True
                    days_since = 999
            
            if not should_train:
                return
            
            # PASO 2: Verificar datos suficientes en Railway
            self.logger.info("   📊 Verificando datos disponibles en Railway...")
            
            if self.db_reader is None:
                self.db_reader = get_db_reader()
            
            try:
                stats = self.db_reader.get_statistics()
                total_records = stats.get('total_readings', 0)
                self.logger.info(f"   ℹ️ Total de registros: {total_records:,}")
                
                # Mínimo 30 días de datos (30 días × 1440 lecturas/día = 43,200)
                MIN_RECORDS = 43200
                
                if total_records < MIN_RECORDS:
                    self.logger.warning(f"   ⚠️ Datos insuficientes: {total_records:,} < {MIN_RECORDS:,}")
                    self.logger.info("   ℹ️ Se necesitan al menos 30 días de datos")
                    self.logger.info("   ℹ️ Esperando más datos antes de entrenar")
                    return
                
                self.logger.info(f"   ✅ Datos suficientes: {total_records:,} registros")
                
                # Calcular días aproximados de datos
                days_of_data = total_records / 1440
                self.logger.info(f"   ℹ️ Aproximadamente {days_of_data:.1f} días de datos")
                
            except Exception as e:
                self.logger.error(f"   ❌ Error al verificar datos: {e}")
                self.logger.info("   ℹ️ Continuando con entrenamiento de todos modos...")
            
            # PASO 3: Ejecutar AutoTrainer pipeline
            self.logger.info("=" * 70)
            self.logger.info("   🤖 INICIANDO PIPELINE DE RE-ENTRENAMIENTO")
            self.logger.info("=" * 70)
            
            try:
                # Inicializar AutoTrainer
                trainer = AutoTrainer(
                    data_source='railway',
                    training_window_days=90  # Usar últimos 90 días
                )
                
                self.logger.info("   🔧 AutoTrainer inicializado")
                self.logger.info("   📊 Fuente de datos: Railway MySQL")
                self.logger.info("   📅 Ventana de entrenamiento: 90 días")
                
                # Ejecutar pipeline completo (11 pasos)
                self.logger.info("   🚀 Ejecutando pipeline completo...")
                result = trainer.run_full_training_pipeline()
                
                # PASO 4: Verificar resultado
                if result.get('success', False):
                    version_id = result.get('version_id', 'unknown')
                    metrics = result.get('metrics', {})
                    comparison = result.get('comparison', {})
                    
                    self.logger.info("=" * 70)
                    self.logger.info("   ✅ RE-ENTRENAMIENTO EXITOSO")
                    self.logger.info("=" * 70)
                    self.logger.info(f"   🆔 Versión: {version_id}")
                    
                    # Métricas del nuevo modelo
                    if metrics:
                        mae = metrics.get('mae', 0)
                        rmse = metrics.get('rmse', 0)
                        r2 = metrics.get('r2', 0)
                        
                        self.logger.info(f"   📊 Métricas del nuevo modelo:")
                        self.logger.info(f"      MAE:  {mae:.4f}")
                        self.logger.info(f"      RMSE: {rmse:.4f}")
                        self.logger.info(f"      R²:   {r2:.4f}")
                    
                    # Comparación con modelo anterior
                    if comparison:
                        mae_improvement = comparison.get('mae_improvement_pct', 0)
                        decision = comparison.get('decision', 'unknown')
                        
                        self.logger.info(f"   📈 Comparación con anterior:")
                        self.logger.info(f"      Mejora MAE: {mae_improvement:+.1f}%")
                        self.logger.info(f"      Decisión: {decision}")
                    
                    # Actualizar estadísticas
                    self.stats['models_retrained'] += 1
                    
                    duration = time.time() - start_time
                    self.logger.info(f"   ⏱️ Tiempo total: {duration:.1f} segundos ({duration/60:.1f} minutos)")
                    
                    # TODO: Enviar email de éxito
                    self.logger.info("   📧 Email de confirmación: PENDIENTE")
                    # self.stats['emails_sent'] += 1
                    
                else:
                    error = result.get('error', 'Error desconocido')
                    self.logger.error("=" * 70)
                    self.logger.error("   ❌ RE-ENTRENAMIENTO FALLÓ")
                    self.logger.error("=" * 70)
                    self.logger.error(f"   Error: {error}")
                    
                    # TODO: Enviar email de fallo
                    self.logger.error("   📧 Email de alerta crítica: PENDIENTE")
                    
                    duration = time.time() - start_time
                    self.logger.error(f"   ⏱️ Tiempo transcurrido: {duration:.1f} segundos")
            
            except Exception as e:
                self.logger.error("=" * 70)
                self.logger.error("   ❌ EXCEPCIÓN DURANTE RE-ENTRENAMIENTO")
                self.logger.error("=" * 70)
                self.logger.error(f"   Error: {e}")
                import traceback
                self.logger.error(f"   Stack trace:\n{traceback.format_exc()}")
                
                # TODO: Enviar email de fallo crítico
                self.logger.error("   📧 Email de alerta crítica: PENDIENTE")
                
                raise
            
            # PASO 5: Cleanup (liberar memoria)
            self.logger.info("   🧹 Liberando memoria...")
            import gc
            gc.collect()
            self.logger.info("   ✅ Cleanup completado")
            
        except Exception as e:
            self.logger.error(f"   ❌ Error en check de re-entrenamiento: {e}")
            import traceback
            self.logger.error(f"   Stack trace:\n{traceback.format_exc()}")
            raise
    
    def generate_daily_report(self):
        """
        ☀️ Job: Generar reporte diario (8 AM)
        
        Genera reporte HTML de las últimas 24 horas con Railway MySQL
        """
        self.logger.info("☀️ [DAILY] Generando reporte diario...")
        start_time = time.time()
        
        try:
            # PASO 1: Conectar a Railway
            self.logger.info("   📡 Conectando a Railway MySQL...")
            db_reader = get_db_reader()
            
            # PASO 2: Generar reporte
            self.logger.info("   📊 Generando reporte HTML...")
            generator = ReportGenerator()
            
            result = generator.generate_daily_report(
                db_reader=db_reader,
                predictions=None,  # TODO: Integrar con predictor en siguiente versión
                anomalies=None     # TODO: Integrar con detector en siguiente versión
            )
            
            # PASO 3: Validar resultado
            if result.get('status') == 'success':
                self.logger.info(f"   ✅ Reporte diario generado: {result['html_path']}")
                self.logger.info(f"      Registros: {result['summary']['total_records']:,}")
                self.logger.info(f"      Consumo promedio: {result['summary']['avg_consumption']:.3f} kW")
                self.logger.info(f"      Fuente: {result['data_source']}")
                
                # Actualizar estadísticas
                self.stats['reports_generated'] += 1
                
                # TODO: Enviar email con reporte adjunto
                self.logger.info("   📧 Email de reporte: PENDIENTE (siguiente versión)")
                
            else:
                self.logger.error(f"   ❌ Error: {result.get('error')}")
                self.logger.warning("   ℹ️ Puede ser falta de datos recientes en Railway")
            
            duration = time.time() - start_time
            self.logger.info(f"   ⏱️ Completado en {duration:.1f} segundos")
            
        except Exception as e:
            self.logger.error(f"   ❌ Error generando reporte diario: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
    
    def generate_weekly_report(self):
        """
        📅 Job: Generar reporte semanal (Lunes 9 AM)
        
        Genera reporte HTML de los últimos 7 días con Railway MySQL
        """
        self.logger.info("📅 [WEEKLY] Generando reporte semanal...")
        start_time = time.time()
        
        try:
            # PASO 1: Conectar a Railway
            self.logger.info("   📡 Conectando a Railway MySQL...")
            db_reader = get_db_reader()
            
            # PASO 2: Generar reporte
            self.logger.info("   📊 Generando reporte HTML...")
            generator = ReportGenerator()
            
            result = generator.generate_weekly_report(
                db_reader=db_reader,
                predictions=None,  # TODO: Integrar con predictor en siguiente versión
                anomalies=None     # TODO: Integrar con detector en siguiente versión
            )
            
            # PASO 3: Validar resultado
            if result.get('status') == 'success':
                self.logger.info(f"   ✅ Reporte semanal generado: {result['html_path']}")
                self.logger.info(f"      Registros: {result['summary']['total_records']:,}")
                self.logger.info(f"      Consumo diario promedio: {result['summary']['avg_daily_kwh']:.2f} kWh")
                self.logger.info(f"      Total semanal: {result['summary']['total_weekly_kwh']:.2f} kWh")
                self.logger.info(f"      Fuente: {result['data_source']}")
                
                # Actualizar estadísticas
                self.stats['reports_generated'] += 1
                
                # TODO: Enviar email con reporte adjunto
                self.logger.info("   📧 Email de reporte: PENDIENTE (siguiente versión)")
                
            else:
                self.logger.error(f"   ❌ Error: {result.get('error')}")
                self.logger.warning("   ℹ️ Puede ser falta de datos recientes en Railway")
            
            duration = time.time() - start_time
            self.logger.info(f"   ⏱️ Completado en {duration:.1f} segundos")
            
        except Exception as e:
            self.logger.error(f"   ❌ Error generando reporte semanal: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
    
    def generate_monthly_report(self):
        """
        📊 Job: Generar reporte mensual (Día 1, 10 AM)
        
        Genera reporte HTML/PDF del mes anterior con Railway MySQL
        """
        self.logger.info("📊 [MONTHLY] Generando reporte mensual...")
        start_time = time.time()
        
        try:
            # PASO 1: Determinar mes a reportar (mes anterior)
            now = datetime.now()
            if now.month == 1:
                report_month = 12
                report_year = now.year - 1
            else:
                report_month = now.month - 1
                report_year = now.year
            
            self.logger.info(f"   📅 Reporte para: {report_month}/{report_year}")
            
            # PASO 2: Conectar a Railway
            self.logger.info("   📡 Conectando a Railway MySQL...")
            db_reader = get_db_reader()
            
            # PASO 3: Generar reporte
            self.logger.info("   📊 Generando reporte HTML...")
            generator = ReportGenerator()
            
            result = generator.generate_monthly_report(
                db_reader=db_reader,
                predictions=None,  # TODO: Integrar con predictor en siguiente versión
                anomalies=None,    # TODO: Integrar con detector en siguiente versión
                month=report_month,
                year=report_year
            )
            
            # PASO 4: Validar resultado
            if result.get('status') == 'success':
                self.logger.info(f"   ✅ Reporte mensual generado: {result['html_path']}")
                summary = result.get('summary', {})
                self.logger.info(f"      Consumo total: {summary.get('total_consumption', 0):.2f} kWh")
                self.logger.info(f"      Consumo diario promedio: {summary.get('daily_avg', 0):.3f} kW")
                self.logger.info(f"      Cambio vs mes anterior: {summary.get('change_pct', 0):+.1f}%")
                self.logger.info(f"      Score de eficiencia: {summary.get('efficiency_score', 0)}/100")
                self.logger.info(f"      Fuente: {result.get('data_source')}")
                
                # Actualizar estadísticas
                self.stats['reports_generated'] += 1
                
                # TODO: Generar PDF y enviar email
                self.logger.info("   📧 Email con PDF: PENDIENTE (siguiente versión)")
                
            else:
                self.logger.error(f"   ❌ Error: {result.get('error')}")
                self.logger.warning(f"   ℹ️ Puede ser falta de datos para {report_month}/{report_year}")
            
            duration = time.time() - start_time
            self.logger.info(f"   ⏱️ Completado en {duration:.1f} segundos")
            
        except Exception as e:
            self.logger.error(f"   ❌ Error generando reporte mensual: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
    
    # ========================================================================
    # CONTROL DEL SCHEDULER
    # ========================================================================
    
    def start(self):
        """
        Iniciar el scheduler (modo 24/7)
        
        El scheduler corre en segundo plano hasta que se detiene con Ctrl+C
        """
        self.logger.info("=" * 70)
        self.logger.info("🚀 INICIANDO SCHEDULER DOMUSAI")
        self.logger.info("=" * 70)
        
        # Inicializar scheduler
        self.initialize_scheduler()
        
        # Agregar jobs
        self.add_jobs()
        
        # Mostrar próximas ejecuciones
        self._print_next_jobs()
        
        # Iniciar scheduler
        assert self.scheduler is not None, "Scheduler debe estar inicializado antes de iniciar"
        self.scheduler.start()
        self.logger.info("✅ Scheduler iniciado - corriendo 24/7")
        self.logger.info("   Para detener: Ctrl+C")
        self.logger.info("=" * 70)
        
        try:
            # Mantener el programa corriendo
            while True:
                time.sleep(60)  # Check cada minuto
                
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("\n🛑 Deteniendo scheduler...")
            self.shutdown()
    
    def shutdown(self):
        """
        Detener el scheduler de forma graceful
        """
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            self.logger.info("✅ Scheduler detenido correctamente")
            
            # Mostrar estadísticas finales
            self._print_stats()
    
    def _print_next_jobs(self):
        """Mostrar próximas ejecuciones programadas"""
        assert self.scheduler is not None, "Scheduler debe estar inicializado"
        
        self.logger.info("\n📅 Próximas ejecuciones programadas:")
        
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            # En APScheduler 3.x, next_run_time puede no estar disponible antes de start()
            # Por eso solo mostramos el nombre del job
            self.logger.info(f"   • {job.name}")
        
        self.logger.info("")
    
    def _print_stats(self):
        """Mostrar estadísticas de ejecución"""
        self.logger.info("\n📊 Estadísticas de ejecución:")
        self.logger.info(f"   Jobs ejecutados: {self.stats['jobs_executed']}")
        self.logger.info(f"   Jobs fallidos: {self.stats['jobs_failed']}")
        self.logger.info(f"   Anomalías detectadas: {self.stats['anomalies_detected']}")
        self.logger.info(f"   Modelos re-entrenados: {self.stats['models_retrained']}")
        self.logger.info(f"   Reportes generados: {self.stats['reports_generated']}")
        self.logger.info(f"   Emails enviados: {self.stats['emails_sent']}")


# ============================================================================
# FUNCIÓN MAIN
# ============================================================================

def main():
    """
    Función principal para ejecutar el scheduler
    """
    print("=" * 70)
    print("🤖 DomusAI - Sistema de Scheduling Automático")
    print("=" * 70)
    print()
    
    # Crear y ejecutar scheduler
    manager = SchedulerManager()
    
    # Configurar signal handlers para shutdown graceful
    def signal_handler(signum, frame):
        manager.logger.info(f"\n🛑 Señal recibida: {signum}")
        manager.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Iniciar scheduler
    manager.start()


if __name__ == "__main__":
    main()
