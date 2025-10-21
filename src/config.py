"""
🔧 DomusAI - Configuración Centralizada

Este módulo centraliza todos los paths, constantes y configuraciones
del proyecto para facilitar mantenimiento y evitar hardcoding.

Autor: DomusAI Team
Fecha: Octubre 2025
Versión: 1.0
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Final
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Directorio raíz del proyecto
PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent


@dataclass(frozen=True)  # Inmutable para seguridad
class PathConfig:
    """Configuración de rutas del proyecto"""
    
    # Directorios principales
    DATA_DIR: Path = PROJECT_ROOT / "data"
    SRC_DIR: Path = PROJECT_ROOT / "src"
    REPORTS_DIR: Path = PROJECT_ROOT / "reports"
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    NOTEBOOKS_DIR: Path = PROJECT_ROOT / "notebooks"
    
    # Datos - Raw
    RAW_CSV: Path = DATA_DIR / "Dataset_original_test.csv"
    
    # Datos - Procesados
    CLEAN_CSV: Path = DATA_DIR / "Dataset_clean_test.csv"
    REALTIME_DB: Path = DATA_DIR / "real_time" / "energy_readings.db"
    
    # Anomalías
    ANOMALIES_DIR: Path = DATA_DIR
    ANOMALIES_CONSENSUS: Path = DATA_DIR / "anomalies_consensus.csv"
    ANOMALIES_SUMMARY: Path = DATA_DIR / "anomalies_summary.json"
    ANOMALIES_HIGH_CONFIDENCE: Path = DATA_DIR / "anomalies_high_confidence.csv"
    
    # Reportes
    GENERATED_REPORTS: Path = REPORTS_DIR / "generated"
    TEMPLATES_DIR: Path = REPORTS_DIR / "templates"
    EMAIL_TEMPLATES_DIR: Path = REPORTS_DIR / "email_templates"
    
    # Modelos ML
    PROPHET_MODEL: Path = MODELS_DIR / "prophet_production.pkl"
    ARIMA_MODEL: Path = MODELS_DIR / "arima_production.pkl"
    ENSEMBLE_MODEL: Path = MODELS_DIR / "ensemble_production.pkl"
    BACKUP_MODELS: Path = MODELS_DIR / "backups"
    
    # Logs
    SYSTEM_LOG: Path = LOGS_DIR / "domusai_system.log"
    PREDICTION_LOG: Path = LOGS_DIR / "predictions.log"
    ANOMALIES_LOG: Path = LOGS_DIR / "anomalies.log"
    EMAIL_LOG: Path = LOGS_DIR / "email_sender.log"
    MQTT_LOG: Path = LOGS_DIR / "mqtt_ingester.log"
    
    def __post_init__(self):
        """Crear directorios si no existen"""
        for field_name in self.__dataclass_fields__:
            path = getattr(self, field_name)
            if isinstance(path, Path) and not path.suffix:  # Es directorio
                path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class MLConfig:
    """Configuración de modelos de Machine Learning"""
    
    # Prophet
    PROPHET_SEASONALITY_MODE: str = 'multiplicative'
    PROPHET_CHANGEPOINT_PRIOR: float = 0.05
    PROPHET_SEASONALITY_PRIOR: float = 10.0
    PROPHET_UNCERTAINTY_SAMPLES: int = 100  # Reducido para performance
    PROPHET_N_CHANGEPOINTS: int = 25
    
    # Prophet Mejorado (sustituto LSTM)
    ENHANCED_PROPHET_CHANGEPOINT_PRIOR: float = 0.1
    ENHANCED_PROPHET_SEASONALITY_PRIOR: float = 15.0
    ENHANCED_PROPHET_N_CHANGEPOINTS: int = 50
    ENHANCED_PROPHET_MCMC_SAMPLES: int = 100
    
    # ARIMA
    ARIMA_MAX_P: int = 5
    ARIMA_MAX_D: int = 2
    ARIMA_MAX_Q: int = 5
    
    # Anomalías - Isolation Forest
    ISOLATION_FOREST_CONTAMINATION: float = 0.05
    ISOLATION_FOREST_N_ESTIMATORS: int = 100
    ISOLATION_FOREST_MAX_SAMPLES: str = 'auto'
    
    # Anomalías - Z-Score
    Z_SCORE_THRESHOLD: float = 3.0
    
    # Anomalías - IQR
    IQR_MULTIPLIER: float = 1.5
    
    # Anomalías - Moving Average
    MOVING_AVG_WINDOW: int = 10
    MOVING_AVG_THRESHOLD: float = 2.0
    
    # Anomalías - Consensus
    CONSENSUS_MIN_METHODS: int = 2
    HIGH_CONFIDENCE_MIN_METHODS: int = 3
    
    # General ML
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    VALIDATION_SIZE: float = 0.1


@dataclass(frozen=True)
class EmailConfig:
    """Configuración de envío de emails"""
    
    # SMTP Settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    USE_TLS: bool = True
    
    # Límites de seguridad
    MAX_ATTACHMENT_SIZE_MB: int = 25
    MAX_RECIPIENTS: int = 10
    
    # Templates
    MONTHLY_REPORT_TEMPLATE: str = "monthly_report_email.html"
    ANOMALY_ALERT_TEMPLATE: str = "anomaly_alert_email.html"
    
    # Configuración de envío
    TIMEOUT_SECONDS: int = 30
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_SECONDS: int = 5


@dataclass(frozen=True)
class RealtimeConfig:
    """Configuración para Sprint 8 - Datos tiempo real"""
    
    # MQTT Broker
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_TOPIC_PREFIX: str = "domusai"
    MQTT_TOPIC_ENERGY: str = "domusai/energy/consumption"
    MQTT_TOPIC_VOLTAGE: str = "domusai/energy/voltage"
    MQTT_TOPIC_STATUS: str = "domusai/system/status"
    MQTT_QOS: int = 1
    MQTT_KEEPALIVE: int = 60
    
    # ESP32 Configuration
    ESP32_DEVICE_ID: str = "esp32_main_01"
    ESP32_SAMPLE_RATE_SECONDS: int = 60  # 1 minuto
    
    # Database
    DB_BATCH_SIZE: int = 100
    DB_RETENTION_DAYS: int = 90
    DB_BACKUP_INTERVAL_HOURS: int = 24
    
    # Análisis en tiempo real
    ANALYSIS_INTERVAL_MINUTES: int = 60
    BUFFER_SIZE_RECORDS: int = 1440  # 24h con lecturas cada minuto
    ANOMALY_CHECK_INTERVAL_MINUTES: int = 15
    
    # Alertas
    ALERT_COOLDOWN_MINUTES: int = 30  # Evitar spam de alertas


# Constantes de dominio energético
@dataclass(frozen=True)
class EnergyConstants:
    """Constantes específicas del dominio energético"""
    
    # Voltaje estándar europeo (España: 230V ±10%)
    VOLTAGE_MIN: float = 207.0  # 230V - 10%
    VOLTAGE_NOMINAL: float = 230.0
    VOLTAGE_MAX: float = 253.0  # 230V + 10%
    VOLTAGE_CRITICAL_LOW: float = 200.0
    VOLTAGE_CRITICAL_HIGH: float = 260.0
    
    # Umbrales de consumo (kW) - Valores típicos hogar español
    CONSUMPTION_IDLE: float = 0.2  # Consumo en standby
    CONSUMPTION_LOW: float = 0.5   # Uso muy bajo
    CONSUMPTION_NORMAL: float = 3.0  # Uso normal
    CONSUMPTION_HIGH: float = 7.0   # Uso alto (electrodomésticos potentes)
    CONSUMPTION_CRITICAL: float = 10.0  # Límite antes de salto diferencial
    
    # Potencia contratada típica (España)
    CONTRACTED_POWER_STANDARD: float = 5.75  # kW (tarifa 2.0TD más común)
    
    # Resolución de datos
    SAMPLING_RATE_SECONDS: int = 60  # 1 minuto
    SAMPLES_PER_HOUR: int = 60
    SAMPLES_PER_DAY: int = 1440
    
    # Coste energía (España 2025 - aproximado)
    PRICE_PER_KWH_PEAK: float = 0.25  # €/kWh (punta)
    PRICE_PER_KWH_VALLEY: float = 0.12  # €/kWh (valle)
    PRICE_PER_KWH_FLAT: float = 0.18  # €/kWh (llano)


# Configuración de Railway MySQL Database
@dataclass(frozen=True)
class DatabaseConfig:
    """Configuración de Railway MySQL Cloud Database"""
    
    # Railway MySQL credentials (from .env)
    MYSQL_HOST: str = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT: int = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_DATABASE: str = os.getenv('MYSQL_DATABASE', 'railway')
    MYSQL_USER: str = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD: str = os.getenv('MYSQL_PASSWORD', '')
    
    # Connection pool settings
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 3600  # Recycle connections every hour
    
    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    
    # Query settings
    BATCH_INSERT_SIZE: int = 1000
    QUERY_TIMEOUT: int = 30
    
    @property
    def connection_url(self) -> str:
        """Generate SQLAlchemy connection URL"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )
    
    @property
    def connection_params(self) -> dict:
        """Generate mysql-connector-python connection params"""
        return {
            'host': self.MYSQL_HOST,
            'port': self.MYSQL_PORT,
            'database': self.MYSQL_DATABASE,
            'user': self.MYSQL_USER,
            'password': self.MYSQL_PASSWORD,
            'charset': 'utf8mb4',
            'autocommit': False,
            'raise_on_warnings': True
        }


# Instancias globales (singleton pattern)
PATHS: Final[PathConfig] = PathConfig()
ML_CONFIG: Final[MLConfig] = MLConfig()
EMAIL_CONFIG: Final[EmailConfig] = EmailConfig()
REALTIME_CONFIG: Final[RealtimeConfig] = RealtimeConfig()
DB_CONFIG: Final[DatabaseConfig] = DatabaseConfig()
ENERGY: Final[EnergyConstants] = EnergyConstants()


def validate_environment() -> bool:
    """
    Validar que el entorno esté correctamente configurado
    
    Returns:
        True si todo OK, False si hay problemas
    """
    issues = []
    
    print("🔧 Validando configuración DomusAI...\n")
    
    # Verificar paths críticos
    if not PATHS.DATA_DIR.exists():
        issues.append(f"❌ DATA_DIR no existe: {PATHS.DATA_DIR}")
    else:
        print(f"✅ DATA_DIR: {PATHS.DATA_DIR}")
    
    if not PATHS.SRC_DIR.exists():
        issues.append(f"❌ SRC_DIR no existe: {PATHS.SRC_DIR}")
    else:
        print(f"✅ SRC_DIR: {PATHS.SRC_DIR}")
    
    # Verificar archivos críticos (advertencias, no errores)
    if not PATHS.CLEAN_CSV.exists():
        print(f"⚠️  Dataset limpio no encontrado: {PATHS.CLEAN_CSV}")
        print(f"   Ejecuta data_cleaning.py primero")
    else:
        print(f"✅ Dataset limpio: {PATHS.CLEAN_CSV}")
    
    # Verificar directorios se crean automáticamente
    print(f"\n📁 Directorios creados automáticamente:")
    print(f"   - Logs: {PATHS.LOGS_DIR}")
    print(f"   - Reports: {PATHS.GENERATED_REPORTS}")
    print(f"   - Models: {PATHS.MODELS_DIR}")
    
    if issues:
        print("\n❌ Problemas encontrados:")
        print("\n".join(issues))
        return False
    
    print("\n✅ Entorno validado correctamente")
    return True


def print_config_summary():
    """Imprimir resumen de configuración para debugging"""
    print("\n" + "="*70)
    print("🔧 CONFIGURACIÓN DOMUSAI - RESUMEN")
    print("="*70)
    
    print(f"\n📁 PATHS:")
    print(f"   Proyecto: {PROJECT_ROOT}")
    print(f"   Datos: {PATHS.DATA_DIR}")
    print(f"   Reportes: {PATHS.REPORTS_DIR}")
    print(f"   Modelos: {PATHS.MODELS_DIR}")
    
    print(f"\n🤖 MACHINE LEARNING:")
    print(f"   Prophet uncertainty samples: {ML_CONFIG.PROPHET_UNCERTAINTY_SAMPLES}")
    print(f"   Isolation Forest contamination: {ML_CONFIG.ISOLATION_FOREST_CONTAMINATION}")
    print(f"   Z-Score threshold: {ML_CONFIG.Z_SCORE_THRESHOLD}")
    print(f"   Consensus min methods: {ML_CONFIG.CONSENSUS_MIN_METHODS}")
    
    print(f"\n📧 EMAIL:")
    print(f"   SMTP Server: {EMAIL_CONFIG.SMTP_SERVER}:{EMAIL_CONFIG.SMTP_PORT}")
    print(f"   Max attachments: {EMAIL_CONFIG.MAX_ATTACHMENT_SIZE_MB} MB")
    print(f"   Max recipients: {EMAIL_CONFIG.MAX_RECIPIENTS}")
    
    print(f"\n⚡ REALTIME (Sprint 8):")
    print(f"   MQTT Broker: {REALTIME_CONFIG.MQTT_BROKER_HOST}:{REALTIME_CONFIG.MQTT_BROKER_PORT}")
    print(f"   Sample rate: {REALTIME_CONFIG.ESP32_SAMPLE_RATE_SECONDS}s")
    print(f"   Analysis interval: {REALTIME_CONFIG.ANALYSIS_INTERVAL_MINUTES} min")
    
    print(f"\n🔌 ENERGÍA:")
    print(f"   Voltaje nominal: {ENERGY.VOLTAGE_NOMINAL}V")
    print(f"   Rango seguro: {ENERGY.VOLTAGE_MIN}V - {ENERGY.VOLTAGE_MAX}V")
    print(f"   Consumo normal: {ENERGY.CONSUMPTION_NORMAL} kW")
    print(f"   Consumo crítico: {ENERGY.CONSUMPTION_CRITICAL} kW")
    print(f"   Precio punta: {ENERGY.PRICE_PER_KWH_PEAK} €/kWh")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    """Test de configuración"""
    print_config_summary()
    validate_environment()
