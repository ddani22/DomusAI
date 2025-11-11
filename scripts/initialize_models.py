"""
🎯 DomusAI - Inicialización de Modelos Base

Este script crea los modelos iniciales usando datos sintéticos o CSV histórico.
Debe ejecutarse UNA VEZ antes de activar el scheduler automático.

Uso:
    # Opción 1: Usar CSV sintético pre-generado
    python scripts/initialize_models.py --data-source synthetic-csv
    
    # Opción 2: CSV sintético con días específicos
    python scripts/initialize_models.py --data-source synthetic-csv --days 180
    
    # Opción 3: CSV sintético específico
    python scripts/initialize_models.py --data-source synthetic-csv --synthetic-file synthetic_data_generator/output/synthetic_1460days_20251102_123456.csv
    
    # Opción 4: Generar datos sintéticos en memoria (90 días)
    python scripts/initialize_models.py --data-source synthetic --days 90
    
    # Opción 5: CSV histórico UCI
    python scripts/initialize_models.py --data-source csv --file data/Dataset_clean_test.csv
    
    # Opción 6: Railway MySQL (producción)
    python scripts/initialize_models.py --data-source railway
"""

import argparse
import sys
import json
import glob
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

# Añadir src/ al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auto_trainer import AutoTrainer
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/model_initialization.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def find_synthetic_csv() -> str:
    """
    🔍 Buscar CSV sintético pre-generado en synthetic_data_generator/output/
    
    Busca archivos con patrón: synthetic_*days_*.csv
    Prioriza el archivo con más días (más datos)
    
    Returns:
        str: Ruta al CSV encontrado
        
    Raises:
        FileNotFoundError: Si no encuentra ningún CSV sintético
    """
    logger.info("🔍 Buscando CSV sintético pre-generado...")
    
    output_dir = Path('synthetic_data_generator/output')
    
    if not output_dir.exists():
        raise FileNotFoundError(
            f"❌ Directorio no encontrado: {output_dir}\n"
            "   Verifica que synthetic_data_generator/output/ existe"
        )
    
    # Buscar archivos con patrón synthetic_*days_*.csv
    pattern = str(output_dir / 'synthetic_*days_*.csv')
    csv_files = glob.glob(pattern)
    
    if not csv_files:
        raise FileNotFoundError(
            f"❌ No se encontraron archivos CSV en: {output_dir}\n"
            "   Patrón esperado: synthetic_*days_*.csv\n"
            "   Genera datos con: python synthetic_data_generator/generate_consumption_data.py"
        )
    
    # Ordenar por tamaño de archivo (más grande = más datos)
    csv_files_sorted = sorted(
        csv_files,
        key=lambda x: Path(x).stat().st_size,
        reverse=True
    )
    
    selected_csv = csv_files_sorted[0]
    
    # Extraer número de días del nombre del archivo
    filename = Path(selected_csv).name
    days: int | None = None
    try:
        # synthetic_1460days_20251102_123456.csv
        days_str = filename.split('_')[1].replace('days', '')
        days = int(days_str)
    except (IndexError, ValueError):
        days = None
    
    logger.info(f"✅ CSV sintético encontrado: {Path(selected_csv).name}")
    if days:
        logger.info(f"   📅 Días de datos: {days:,}")
    logger.info(f"   📦 Tamaño: {Path(selected_csv).stat().st_size / 1e6:.1f} MB")
    logger.info(f"   📂 Ruta completa: {selected_csv}")
    
    return selected_csv


def load_synthetic_csv_training_data(csv_path: str | None = None, training_days: int = 90) -> pd.DataFrame:
    """
    📂 Cargar datos desde CSV sintético pre-generado
    
    Args:
        csv_path: Ruta al CSV sintético (si None, busca automáticamente)
        training_days: Días de datos a usar para entrenamiento (default: 90, 0 = todos)
        
    Returns:
        DataFrame con últimos N días de datos sintéticos
    """
    # Buscar CSV si no se especifica
    if csv_path is None:
        csv_path = find_synthetic_csv()
    
    logger.info(f"📂 Cargando datos desde CSV sintético...")
    logger.info(f"   📄 Archivo: {Path(csv_path).name}")
    
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"❌ Archivo no encontrado: {csv_path}")
    
    # Cargar CSV
    logger.info(f"⏳ Cargando datos (puede tardar 10-30 segundos)...")
    df = pd.read_csv(csv_path)
    
    logger.info(f"✅ CSV cargado: {len(df):,} registros totales")
    
    # Convertir timestamp a datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
    else:
        # Asumir primera columna es timestamp
        first_col = df.iloc[:, 0]
        df = df.iloc[:, 1:]  # Eliminar columna duplicada
        df.index = pd.DatetimeIndex(pd.to_datetime(first_col))
        df.index.name = 'timestamp'
    
    # Ordenar por timestamp (importante!)
    df = df.sort_index()
    
    # Extraer últimos N días para entrenamiento (si training_days > 0)
    if training_days > 0:
        cutoff_date = df.index.max() - timedelta(days=training_days)
        df = df[df.index >= cutoff_date].copy()
        
        logger.info(f"📅 Usando últimos {training_days} días para entrenamiento")
        logger.info(f"   📅 Rango seleccionado: {df.index.min()} → {df.index.max()}")
    else:
        logger.info(f"📅 Usando TODOS los datos disponibles")
        logger.info(f"   📅 Rango completo: {df.index.min()} → {df.index.max()}")
    
    # Validar columnas requeridas
    required_cols = ['Global_active_power', 'Voltage', 'Global_intensity']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise ValueError(
            f"❌ Columnas faltantes en CSV: {missing_cols}\n"
            f"   Columnas disponibles: {df.columns.tolist()}"
        )
    
    logger.info(f"✅ Datos sintéticos cargados:")
    logger.info(f"   📊 Registros finales: {len(df):,}")
    logger.info(f"   📅 Rango: {df.index.min().strftime('%Y-%m-%d')} → {df.index.max().strftime('%Y-%m-%d')}")
    logger.info(f"   📈 Consumo promedio: {df['Global_active_power'].mean():.3f} kW")
    logger.info(f"   🔥 Consumo máximo: {df['Global_active_power'].max():.3f} kW")
    logger.info(f"   📉 Consumo mínimo: {df['Global_active_power'].min():.3f} kW")
    
    return df


def generate_synthetic_training_data(days: int = 90) -> pd.DataFrame:
    """
    🔄 Generar datos sintéticos realistas para entrenamiento inicial
    
    ⚠️ DEPRECADO: Mejor usar --data-source synthetic-csv con archivos pre-generados
    
    Genera datos con patrones españoles (IDAE):
    - Consumo promedio: 0.40-0.52 kW (hogar mediano 3-4 personas)
    - Patrones horarios: Picos 8h, 14h, 21h
    - Estacionalidad: HVAC invierno/verano
    - Anomalías: 3% de datos anómalos
    
    Args:
        days: Días de datos a generar (default: 90)
        
    Returns:
        DataFrame con datos sintéticos en formato DomusAI
    """
    logger.info(f"🔄 Generando {days} días de datos sintéticos...")
    logger.warning("⚠️ Generando en memoria - Considera usar --data-source synthetic-csv")
    
    # Crear timestamps (resolución: 1 minuto)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    timestamps = pd.date_range(start=start_date, end=end_date, freq='1min')
    
    logger.info(f"   📅 Rango: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"   📊 Registros: {len(timestamps):,}")
    
    # Baseline consumption (hogar mediano español: 0.45 kW promedio)
    baseline = 0.45
    
    # Componentes temporales
    hours = timestamps.hour.to_numpy()
    days_of_week = timestamps.dayofweek.to_numpy()
    
    # Patrón horario (estilo español)
    hourly_pattern = np.array([
        0.30, 0.28, 0.27, 0.26, 0.26, 0.28,  # 00:00-05:59 (valle nocturno)
        0.40, 0.65, 0.90, 0.75, 0.60, 0.55,  # 06:00-11:59 (despertar + mañana)
        0.70, 0.90, 1.20, 0.80, 0.65, 0.60,  # 12:00-17:59 (comida + tarde)
        0.75, 0.95, 1.10, 1.30, 1.00, 0.70   # 18:00-23:59 (cena + noche)
    ])
    
    # Aplicar patrón horario
    hourly_multiplier = hourly_pattern[hours]
    
    # Patrón semanal (fin de semana +20%)
    weekly_multiplier = np.where(days_of_week >= 5, 1.2, 1.0)
    
    # Estacionalidad mensual (HVAC: frío invierno, calor verano)
    months = timestamps.month.to_numpy()
    seasonal_multiplier = 1.0 + 0.15 * np.sin((months - 1) * np.pi / 6)
    
    # Generar consumo base
    consumption = (baseline * 
                   hourly_multiplier * 
                   weekly_multiplier * 
                   seasonal_multiplier)
    
    # Añadir ruido realista (±5%)
    noise = np.random.normal(0, 0.05 * consumption, len(consumption))
    consumption = consumption + noise
    
    # Añadir anomalías (3% de datos)
    n_anomalies = int(len(consumption) * 0.03)
    anomaly_indices = np.random.choice(len(consumption), n_anomalies, replace=False)
    
    # Tipos de anomalías
    for idx in anomaly_indices:
        anomaly_type = np.random.choice(['spike', 'drop', 'constant'])
        
        if anomaly_type == 'spike':
            # Pico anormal (3-5x consumo normal)
            consumption[idx] *= np.random.uniform(3, 5)
        elif anomaly_type == 'drop':
            # Caída anormal (10-30% del normal)
            consumption[idx] *= np.random.uniform(0.1, 0.3)
        else:
            # Valor constante prolongado (10 minutos)
            constant_value = consumption[idx]
            for j in range(min(10, len(consumption) - idx)):
                consumption[idx + j] = constant_value
    
    # Asegurar valores positivos y rangos realistas
    consumption = np.clip(consumption, 0.05, 7.0)
    
    # Calcular variables derivadas (estilo Dataset original)
    voltage = np.random.normal(235, 2, len(consumption))  # 230V ±10%
    global_intensity = (consumption * 1000) / voltage     # Ley de Ohm
    
    # Sub-metering (cocina, lavandería, HVAC)
    sub1 = consumption * np.random.uniform(0.20, 0.30, len(consumption))  # Cocina 25%
    sub2 = consumption * np.random.uniform(0.05, 0.12, len(consumption))  # Lavandería 8%
    sub3 = consumption * np.random.uniform(0.25, 0.35, len(consumption))  # HVAC 30%
    
    # Crear DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'Global_active_power': consumption,
        'Global_reactive_power': consumption * 0.15,  # Factor de potencia típico
        'Voltage': voltage,
        'Global_intensity': global_intensity,
        'Sub_metering_1': sub1,
        'Sub_metering_2': sub2,
        'Sub_metering_3': sub3
    })
    
    df = df.set_index('timestamp')
    
    # Estadísticas
    logger.info(f"✅ Datos sintéticos generados:")
    logger.info(f"   📊 Registros: {len(df):,}")
    logger.info(f"   📈 Consumo promedio: {df['Global_active_power'].mean():.3f} kW")
    logger.info(f"   🔥 Consumo máximo: {df['Global_active_power'].max():.3f} kW")
    logger.info(f"   📉 Consumo mínimo: {df['Global_active_power'].min():.3f} kW")
    logger.info(f"   ⚠️ Anomalías inyectadas: {n_anomalies:,} ({(n_anomalies/len(df)*100):.1f}%)")
    
    return df


def load_csv_training_data(csv_path: str) -> pd.DataFrame:
    """
    📂 Cargar datos desde CSV histórico (Dataset UCI original)
    
    Args:
        csv_path: Ruta al CSV limpio
        
    Returns:
        DataFrame con datos históricos
    """
    logger.info(f"📂 Cargando datos desde CSV: {csv_path}")
    
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"❌ Archivo no encontrado: {csv_path}")
    
    # Cargar CSV
    df = pd.read_csv(csv_path)
    
    # Convertir timestamp a datetime si no lo es
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
    elif df.index.name is None:
        # Asumir primera columna es timestamp
        df.index = pd.to_datetime(df.index)
        df.index.name = 'timestamp'
    
    logger.info(f"✅ Datos CSV cargados:")
    logger.info(f"   📊 Registros: {len(df):,}")
    logger.info(f"   📅 Rango: {df.index.min()} → {df.index.max()}")
    logger.info(f"   📈 Consumo promedio: {df['Global_active_power'].mean():.3f} kW")
    
    return df


def load_railway_training_data(days: int = 90) -> pd.DataFrame:
    """
    🚂 Cargar datos desde Railway MySQL
    
    Args:
        days: Días de histórico a cargar
        
    Returns:
        DataFrame con datos de Railway
    """
    logger.info(f"🚂 Cargando datos de Railway MySQL (últimos {days} días)...")
    
    try:
        from src.database import get_db_reader
        
        db = get_db_reader()
        
        # Test conexión
        if not db.test_connection():
            raise ConnectionError("❌ Railway MySQL no disponible")
        
        logger.info("✅ Conexión Railway establecida")
        
        # Obtener datos
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = db.get_data_by_date_range(start_date, end_date)
        
        if df is None or len(df) == 0:
            raise ValueError("❌ Railway devolvió DataFrame vacío")
        
        logger.info(f"✅ Datos Railway cargados:")
        logger.info(f"   📊 Registros: {len(df):,}")
        logger.info(f"   📅 Rango: {df.index.min()} → {df.index.max()}")
        logger.info(f"   📈 Consumo promedio: {df['Global_active_power'].mean():.3f} kW")
        
        return df
        
    except ImportError:
        logger.error("❌ Módulo database.py no encontrado")
        raise
    except Exception as e:
        logger.error(f"❌ Error conectando a Railway: {e}")
        raise


def initialize_models_from_data(
    df: pd.DataFrame,
    models_dir: str = 'models'
) -> dict:
    """
    🚀 Crear modelos iniciales desde DataFrame
    
    Proceso:
    1. Validar calidad de datos
    2. Preprocesar datos
    3. Entrenar Prophet
    4. Entrenar Isolation Forest
    5. Evaluar modelos
    6. Guardar como modelos base
    
    Args:
        df: DataFrame con datos de entrenamiento
        models_dir: Directorio de modelos (default: 'models')
        
    Returns:
        dict: Resultado del entrenamiento
            - success: bool
            - version_id: str (si exitoso)
            - metrics: dict (si exitoso)
            - error: str (si falló)
    """
    logger.info("=" * 70)
    logger.info("🚀 INICIALIZANDO MODELOS BASE")
    logger.info("=" * 70)
    
    try:
        # Crear directorio de modelos si no existe
        Path(models_dir).mkdir(parents=True, exist_ok=True)
        
        # Crear AutoTrainer en modo local
        logger.info("🔧 Configurando AutoTrainer...")
        
        trainer = AutoTrainer(
            data_source='local',  # Bypass Railway
            training_window_days=len(df) // 1440,  # Días disponibles
            models_dir=models_dir,
            enable_notifications=False  # Sin emails para inicialización
        )
        
        # Inyectar datos directamente
        trainer.training_df = df
        
        logger.info(f"✅ AutoTrainer configurado (modo: local)")
        logger.info(f"   📂 Directorio modelos: {models_dir}")
        logger.info(f"   📊 Datos disponibles: {len(df):,} registros")
        
        # Paso 1: Validar calidad de datos
        logger.info("\n" + "─" * 70)
        logger.info("📋 PASO 1/5: Validando calidad de datos")
        logger.info("─" * 70)
        
        quality = trainer.validate_data_quality(df)
        
        if not quality['is_valid']:
            logger.error("❌ Datos no válidos para entrenamiento")
            logger.error(f"   Razones: {quality.get('issues', [])}")
            return {
                'success': False,
                'error': 'Datos no válidos',
                'quality_report': quality
            }
        
        logger.info("✅ Validación de calidad pasada")
        logger.info(f"   📊 Registros válidos: {quality.get('data_points', len(df)):,}")
        logger.info(f"   ⚠️ Nulos: {quality.get('null_percentage', 0):.2f}%")
        logger.info(f"   📉 Outliers: {quality.get('outlier_percentage', 0):.2f}%")
        
        # Paso 2: Preprocesar datos
        logger.info("\n" + "─" * 70)
        logger.info("🧹 PASO 2/5: Preprocesando datos")
        logger.info("─" * 70)
        
        df_clean = trainer.preprocess_data(df)
        
        logger.info("✅ Datos preprocesados")
        logger.info(f"   📊 Registros finales: {len(df_clean):,}")
        
        # Paso 3: Entrenar Prophet
        logger.info("\n" + "─" * 70)
        logger.info("🔮 PASO 3/5: Entrenando modelo Prophet")
        logger.info("─" * 70)
        
        prophet_model = trainer.train_prophet(df_clean)
        
        logger.info("✅ Modelo Prophet entrenado exitosamente")
        
        # Paso 4: Entrenar Isolation Forest
        logger.info("\n" + "─" * 70)
        logger.info("🚨 PASO 4/5: Entrenando Isolation Forest")
        logger.info("─" * 70)
        
        anomaly_model = trainer.train_anomaly_detector(df_clean)
        
        logger.info("✅ Isolation Forest entrenado exitosamente")
        
        # Paso 5: Evaluar modelos
        logger.info("\n" + "─" * 70)
        logger.info("📊 PASO 5/5: Evaluando modelos")
        logger.info("─" * 70)
        
        metrics = trainer.evaluate_models(
            prophet_model, 
            df_clean, 
            test_days=7  # 7 días para test set
        )
        
        logger.info("✅ Evaluación completada:")
        logger.info(f"   📈 MAE:  {metrics['mae']:.3f} kW")
        logger.info(f"   📈 RMSE: {metrics['rmse']:.3f} kW")
        logger.info(f"   📈 MAPE: {metrics['mape']:.2f}%")
        logger.info(f"   📈 R²:   {metrics['r2_score']:.4f}")
        
        # Guardar como modelos base (primera versión = best)
        logger.info("\n" + "─" * 70)
        logger.info("💾 Guardando modelos como versión base")
        logger.info("─" * 70)
        
        version_id = trainer.save_models(
            prophet_model,
            anomaly_model,
            metrics,
            save_as_best=True  # Primera versión = best model
        )
        
        logger.info(f"✅ Modelos guardados:")
        logger.info(f"   📦 Versión: {version_id}")
        logger.info(f"   📂 Producción: best_prophet.pkl, best_isolation_forest.pkl")
        logger.info(f"   📂 Backup: prophet_{version_id}.pkl, isolation_forest_{version_id}.pkl")
        
        # Log historial de entrenamiento
        trainer.log_training_metrics(metrics, version_id)
        
        logger.info("=" * 70)
        logger.info("🎉 MODELOS BASE CREADOS EXITOSAMENTE")
        logger.info("=" * 70)
        logger.info(f"📦 Versión: {version_id}")
        logger.info(f"📈 MAE: {metrics['mae']:.3f} kW")
        logger.info(f"📈 RMSE: {metrics['rmse']:.3f} kW")
        logger.info(f"📈 MAPE: {metrics['mape']:.2f}%")
        logger.info(f"📈 R²: {metrics['r2_score']:.4f}")
        logger.info("=" * 70)
        
        return {
            'success': True,
            'version_id': version_id,
            'metrics': metrics,
            'model_paths': {
                'prophet_production': f"{models_dir}/best_prophet.pkl",
                'anomaly_production': f"{models_dir}/best_isolation_forest.pkl",
                'prophet_backup': f"{models_dir}/prophet_{version_id}.pkl",
                'anomaly_backup': f"{models_dir}/isolation_forest_{version_id}.pkl"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error crítico creando modelos base: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def main():
    """
    🎯 Main: Inicializar modelos según data source
    """
    parser = argparse.ArgumentParser(
        description='🤖 DomusAI - Inicialización de Modelos Base',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
  # CSV sintético pre-generado (RECOMENDADO - usa tu archivo de 4 años)
  python scripts/initialize_models.py
  python scripts/initialize_models.py --data-source synthetic-csv
  
  # CSV sintético con días específicos
  python scripts/initialize_models.py --data-source synthetic-csv --days 180
  
  # CSV sintético con todos los datos (4 años completos)
  python scripts/initialize_models.py --data-source synthetic-csv --days 0
  
  # CSV sintético específico
  python scripts/initialize_models.py --data-source synthetic-csv --synthetic-file synthetic_data_generator/output/synthetic_1460days_20251102_123456.csv
  
  # Generar datos sintéticos en memoria (no recomendado)
  python scripts/initialize_models.py --data-source synthetic --days 90
  
  # CSV histórico UCI
  python scripts/initialize_models.py --data-source csv --file data/Dataset_clean_test.csv
  
  # Railway MySQL (producción)
  python scripts/initialize_models.py --data-source railway --days 90
        """
    )
    
    parser.add_argument(
        '--data-source',
        type=str,
        choices=['synthetic-csv', 'synthetic', 'csv', 'railway'],
        default='synthetic-csv',  # ← NUEVO DEFAULT: usar CSV pre-generado
        help='Fuente de datos (default: synthetic-csv)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=90,
        help='Días de datos a usar para entrenamiento (default: 90, 0 = todos los datos)'
    )
    
    parser.add_argument(
        '--synthetic-file',
        type=str,
        default=None,
        help='Ruta específica al CSV sintético (si None, busca automáticamente en synthetic_data_generator/output/)'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        default='data/Dataset_clean_test.csv',
        help='Ruta CSV si data-source=csv (default: data/Dataset_clean_test.csv)'
    )
    
    parser.add_argument(
        '--models-dir',
        type=str,
        default='models',
        help='Directorio de modelos (default: models)'
    )
    
    args = parser.parse_args()
    
    # Header
    print("\n" + "=" * 70)
    print("🤖 DomusAI - Inicialización de Modelos Base")
    print("=" * 70)
    print(f"📊 Data source: {args.data_source.upper()}")
    print(f"📂 Models dir: {args.models_dir}")
    if args.data_source in ['synthetic-csv', 'synthetic', 'railway']:
        if args.days == 0:
            print(f"📅 Training days: TODOS LOS DATOS DISPONIBLES")
        else:
            print(f"📅 Training days: {args.days}")
    if args.data_source == 'csv':
        print(f"📄 CSV file: {args.file}")
    if args.data_source == 'synthetic-csv' and args.synthetic_file:
        print(f"📄 Synthetic CSV: {args.synthetic_file}")
    print("=" * 70)
    print()
    
    # Obtener datos según fuente
    try:
        if args.data_source == 'synthetic-csv':
            # ⭐ NUEVO: Usar CSV sintético pre-generado (tu archivo de 4 años)
            df = load_synthetic_csv_training_data(
                csv_path=args.synthetic_file,
                training_days=args.days
            )
        
        elif args.data_source == 'synthetic':
            # Generar datos sintéticos en memoria (legacy)
            logger.warning("⚠️ Generando datos en memoria - Considera usar --data-source synthetic-csv")
            df = generate_synthetic_training_data(days=args.days)
        
        elif args.data_source == 'csv':
            # CSV histórico UCI
            df = load_csv_training_data(args.file)
        
        elif args.data_source == 'railway':
            # Railway MySQL
            df = load_railway_training_data(days=args.days)
        
        else:
            logger.error(f"❌ Data source no válido: {args.data_source}")
            return 1
    
    except Exception as e:
        logger.error(f"❌ Error cargando datos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    
    # Inicializar modelos
    result = initialize_models_from_data(df, models_dir=args.models_dir)
    
    # Resultado final
    print("\n" + "=" * 70)
    if result['success']:
        print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"📦 Versión: {result['version_id']}")
        print(f"📈 MAE: {result['metrics']['mae']:.3f} kW")
        print(f"📈 RMSE: {result['metrics']['rmse']:.3f} kW")
        print(f"📈 MAPE: {result['metrics']['mape']:.2f}%")
        print(f"📈 R²: {result['metrics']['r2_score']:.4f}")
        print(f"\n📂 Modelos guardados en: {args.models_dir}/")
        print(f"   ⭐ {result['model_paths']['prophet_production']}")
        print(f"   ⭐ {result['model_paths']['anomaly_production']}")
        print(f"   💾 {result['model_paths']['prophet_backup']}")
        print(f"   💾 {result['model_paths']['anomaly_backup']}")
        print("\n🚀 SIGUIENTE PASO:")
        print("   Ejecuta: python scripts/auto_training_scheduler.py --test")
        print("=" * 70)
        return 0
    else:
        print("❌ INICIALIZACIÓN FALLÓ")
        print("=" * 70)
        print(f"Error: {result.get('error', 'Unknown')}")
        print("\n📋 TROUBLESHOOTING:")
        print("   1. Verificar que datos tienen formato correcto")
        print("   2. Verificar columna 'Global_active_power' existe")
        print("   3. Verificar datos tienen al menos 30 días")
        print("   4. Revisar logs/model_initialization.log")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
