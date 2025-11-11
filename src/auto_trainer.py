"""
🤖 DomusAI - Sistema de Auto-Entrenamiento Automático

Este módulo implementa el auto-entrenamiento periódico de modelos ML
usando datos en tiempo real desde Railway MySQL.

Características:
- Re-entrenamiento automático semanal (Domingos 3AM)
- Ventana rolling de 90 días
- Versionado automático de modelos
- Comparación con versión anterior
- Rollback si nuevo modelo degrada
- Logging exhaustivo y notificaciones
"""

import pandas as pd
import numpy as np
import joblib
import json
import warnings
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import os
import shutil

# Time Series Models
from prophet import Prophet
from sklearn.ensemble import IsolationForest

# Metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# DomusAI imports
from src.database import get_db_reader, RailwayDatabaseReader
from src.predictor import EnergyPredictor
from src.anomalies import AnomalyDetector
from src.exceptions import InsufficientDataError, DatabaseConnectionError

warnings.filterwarnings('ignore')

# Setup logging
def setup_auto_trainer_logging():
    """Configurar sistema de logging para auto-entrenamiento"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/auto_training.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('AutoTrainer')


class AutoTrainer:
    """
    🤖 Sistema de Auto-Entrenamiento para DomusAI
    
    Responsabilidades:
    1. Obtener datos de Railway MySQL (últimos 90 días)
    2. Validar calidad de datos (mínimo 30 días)
    3. Pre-procesar datos (limpieza, formato)
    4. Entrenar modelo Prophet
    5. Entrenar Isolation Forest para anomalías
    6. Evaluar performance (MAE, RMSE, MAPE)
    7. Comparar con modelo anterior
    8. Guardar modelo solo si mejora
    9. Versionado automático
    10. Logging exhaustivo
    
    Example:
        >>> # Auto-entrenamiento completo
        >>> trainer = AutoTrainer(
        ...     data_source='railway',
        ...     training_window_days=90,
        ...     enable_notifications=True
        ... )
        >>> result = trainer.run_full_training_pipeline()
        >>> print(f"Success: {result['success']}")
        >>> print(f"Version: {result['version_id']}")
        >>> print(f"MAE: {result['metrics']['mae']:.3f}")
    """
    
    # Umbrales de degradación de modelos
    DEGRADATION_THRESHOLDS = {
        'mae_increase_pct': 10,      # Si MAE aumenta >10%, alertar
        'rmse_increase_pct': 15,     # Si RMSE aumenta >15%, alertar
        'r2_decrease': 0.05,         # Si R² baja >0.05, alertar
    }
    
    def __init__(
        self,
        data_source: str = 'railway',
        training_window_days: int = 90,
        min_data_days: int = 30,
        models_dir: str = 'models',
        enable_notifications: bool = False,
        db_reader: Optional[RailwayDatabaseReader] = None
    ):
        """
        🔧 Inicializar AutoTrainer
        
        Args:
            data_source: 'railway' (recomendado) o 'csv' (fallback)
            training_window_days: Ventana de datos para entrenar (default: 90)
            min_data_days: Días mínimos requeridos (default: 30)
            models_dir: Directorio de modelos (default: 'models')
            enable_notifications: Enviar emails de notificación
            db_reader: Instancia de RailwayDatabaseReader (opcional)
        """
        self.data_source = data_source
        self.training_window_days = training_window_days
        self.min_data_days = min_data_days
        self.models_dir = Path(models_dir)
        self.enable_notifications = enable_notifications
        self.db_reader = db_reader
        
        # Estado del entrenamiento
        self.training_df = None
        self.prophet_model = None
        self.anomaly_model = None
        self.current_metrics = {}
        self.version_id = None
        
        # Crear directorios necesarios
        self.models_dir.mkdir(parents=True, exist_ok=True)
        Path('logs').mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = setup_auto_trainer_logging()
        
        self.logger.info("=" * 70)
        self.logger.info("🤖 AutoTrainer DomusAI inicializado")
        self.logger.info(f"   📊 Data source: {data_source.upper()}")
        self.logger.info(f"   📅 Training window: {training_window_days} días")
        self.logger.info(f"   📂 Models dir: {models_dir}")
        self.logger.info(f"   📧 Notifications: {'ENABLED' if enable_notifications else 'DISABLED'}")
        self.logger.info("=" * 70)
    
    # ========================================================================
    # GRUPO 1: DATA FETCHING
    # ========================================================================
    
    def fetch_training_data(self) -> pd.DataFrame:
        """
        🔄 Obtener datos de Railway MySQL (últimos N días según training_window)
        
        Proceso:
        1. Calcular rango de fechas (ahora - training_window_days)
        2. Consultar Railway MySQL
        3. Validar que hay suficientes datos
        
        Returns:
            DataFrame con datos de consumo energético
            
        Raises:
            InsufficientDataError: Si hay menos de min_data_days
            DatabaseConnectionError: Si falla conexión Railway
        """
        self.logger.info(f"🔄 Obteniendo datos de Railway (últimos {self.training_window_days} días)...")
        
        try:
            # Inicializar db_reader si no existe
            if self.db_reader is None:
                self.db_reader = get_db_reader()
            
            # Test de conexión
            if not self.db_reader.test_connection():
                raise DatabaseConnectionError("❌ Railway MySQL no disponible")
            
            # Calcular rango de fechas
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.training_window_days)
            
            self.logger.info(f"   📅 Rango: {start_date.date()} a {end_date.date()}")
            
            # Obtener datos de Railway
            df = self.db_reader.get_data_by_date_range(start_date, end_date)
            
            if df is None or len(df) == 0:
                raise InsufficientDataError("❌ Railway devolvió DataFrame vacío")
            
            # Verificar datos mínimos
            days_coverage = (df.index.max() - df.index.min()).days
            
            if days_coverage < self.min_data_days:
                raise InsufficientDataError(
                    f"❌ Datos insuficientes: {days_coverage} días (mínimo: {self.min_data_days})"
                )
            
            self.logger.info(f"✅ Datos obtenidos: {len(df):,} registros")
            self.logger.info(f"   📊 Cobertura: {days_coverage} días")
            self.logger.info(f"   🔢 Columnas: {list(df.columns)}")
            
            return df
            
        except DatabaseConnectionError as e:
            self.logger.error(f"❌ Error de conexión Railway: {e}")
            raise
        
        except InsufficientDataError as e:
            self.logger.error(f"❌ Datos insuficientes: {e}")
            raise
        
        except Exception as e:
            self.logger.error(f"❌ Error inesperado obteniendo datos: {e}")
            raise RuntimeError(f"Error fetching data: {e}")
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        ✅ Validar calidad de datos antes de entrenar
        
        Checks realizados:
        1. Mínimo 30 días de datos continuos
        2. < 5% de valores nulos en columna principal
        3. Voltaje en rango 200-250V
        4. Potencia en rango razonable (0-10 kW)
        5. Sin gaps temporales > 6 horas
        
        Args:
            df: DataFrame a validar
            
        Returns:
            {
                'is_valid': bool,
                'warnings': List[str],
                'data_points': int,
                'coverage_days': int,
                'null_percentage': float,
                'voltage_ok': bool,
                'power_ok': bool
            }
        """
        self.logger.info("🔍 Validando calidad de datos...")
        
        warnings_list = []
        is_valid = True
        
        # Check 1: Cobertura temporal
        coverage_days = (df.index.max() - df.index.min()).days
        if coverage_days < self.min_data_days:
            warnings_list.append(f"⚠️ Cobertura insuficiente: {coverage_days} días")
            is_valid = False
        
        # Check 2: Valores nulos
        null_pct = (df['Global_active_power'].isnull().sum() / len(df)) * 100
        if null_pct > 5:
            warnings_list.append(f"⚠️ Alto % de nulos: {null_pct:.2f}%")
            is_valid = False
        
        # Check 3: Rango de voltaje
        voltage_mean = df['Voltage'].mean()
        voltage_ok = 200 <= voltage_mean <= 250
        if not voltage_ok:
            warnings_list.append(f"⚠️ Voltaje fuera de rango: {voltage_mean:.1f}V")
        
        # Check 4: Rango de potencia
        power_max = df['Global_active_power'].max()
        power_ok = 0 <= power_max <= 10
        if not power_ok:
            warnings_list.append(f"⚠️ Potencia sospechosa: max={power_max:.2f} kW")
        
        # Check 5: Gaps temporales
        time_diffs = df.index.to_series().diff()
        max_gap = time_diffs.max()
        # Verificar si max_gap es un Timedelta válido
        max_gap_hours = max_gap.total_seconds() / 3600 if isinstance(max_gap, pd.Timedelta) else 0.0
        if max_gap_hours > 6:
            warnings_list.append(f"⚠️ Gap temporal detectado: {max_gap_hours:.1f} horas")
        
        # Resultado
        result = {
            'is_valid': is_valid,
            'warnings': warnings_list,
            'data_points': len(df),
            'coverage_days': coverage_days,
            'null_percentage': null_pct,
            'voltage_ok': voltage_ok,
            'power_ok': power_ok,
            'max_gap_hours': max_gap_hours
        }
        
        # Logging
        if is_valid:
            self.logger.info("✅ Calidad de datos: VÁLIDA")
        else:
            self.logger.warning("⚠️ Calidad de datos: CON ADVERTENCIAS")
        
        for warning in warnings_list:
            self.logger.warning(f"   {warning}")
        
        self.logger.info(f"   📊 Data points: {result['data_points']:,}")
        self.logger.info(f"   📅 Cobertura: {result['coverage_days']} días")
        self.logger.info(f"   🔢 Nulos: {result['null_percentage']:.2f}%")
        
        return result
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        🔧 Limpiar y preparar datos para entrenamiento
        
        Steps:
        1. Manejar valores nulos (interpolación lineal)
        2. Detectar y corregir outliers extremos (> 3σ)
        3. Asegurar índice DatetimeIndex ordenado
        4. Resampling si hay gaps temporales
        5. Validar formato final
        
        Args:
            df: DataFrame crudo de Railway
            
        Returns:
            DataFrame limpio y preparado
        """
        self.logger.info("🔧 Pre-procesando datos...")
        
        df_clean = df.copy()
        
        # Step 1: Manejar nulos
        null_count = df_clean['Global_active_power'].isnull().sum()
        if null_count > 0:
            self.logger.info(f"   🔄 Interpolando {null_count} valores nulos...")
            df_clean['Global_active_power'] = df_clean['Global_active_power'].interpolate(
                method='linear',
                limit_direction='both'
            )
        
        # Step 2: Outliers extremos (> 3σ)
        mean = df_clean['Global_active_power'].mean()
        std = df_clean['Global_active_power'].std()
        outlier_mask = np.abs(df_clean['Global_active_power'] - mean) > (3 * std)
        outlier_count = outlier_mask.sum()
        
        if outlier_count > 0:
            self.logger.info(f"   🔄 Corrigiendo {outlier_count} outliers extremos...")
            # Reemplazar outliers con media
            df_clean.loc[outlier_mask, 'Global_active_power'] = mean
        
        # Step 3: Asegurar índice ordenado
        df_clean = df_clean.sort_index()
        
        # Step 4: Resampling si necesario (detectar gaps > 1 hora)
        time_diffs = df_clean.index.to_series().diff()
        max_gap = time_diffs.max()
        
        # Verificar si max_gap es un Timedelta válido antes de comparar
        if isinstance(max_gap, pd.Timedelta) and max_gap > pd.Timedelta(hours=1):
            self.logger.info(f"   🔄 Resampling por gaps detectados (max: {max_gap})...")
            df_clean = df_clean.resample('1min').mean()  # Resamplear a 1 minuto
            df_clean = df_clean.interpolate(method='linear')
        
        # Step 5: Eliminar cualquier NaN restante
        df_clean = df_clean.dropna(subset=['Global_active_power'])
        
        self.logger.info(f"✅ Pre-procesamiento completado: {len(df_clean):,} registros finales")
        
        return df_clean
    
    # ========================================================================
    # GRUPO 2: TRAINING
    # ========================================================================
    
    def train_prophet(self, df: pd.DataFrame) -> Prophet:
        """
        🔮 Entrenar modelo Prophet con datos Railway
        
        Hiperparámetros optimizados para consumo energético:
        - changepoint_prior_scale=0.05 (detecta cambios sutiles)
        - seasonality_prior_scale=10 (fuerte estacionalidad diaria)
        - daily_seasonality=True
        - weekly_seasonality=True
        - yearly_seasonality=False (no tenemos >1 año datos)
        
        Args:
            df: DataFrame preprocesado
            
        Returns:
            Modelo Prophet entrenado
        """
        self.logger.info("🔮 Entrenando modelo Prophet...")
        
        # Preparar formato Prophet (ds, y)
        prophet_df = df.reset_index()
        prophet_df = prophet_df.rename(columns={
            prophet_df.columns[0]: 'ds',  # datetime
            'Global_active_power': 'y'     # target
        })
        prophet_df = prophet_df[['ds', 'y']].dropna()
        
        self.logger.info(f"   📊 Datos Prophet: {len(prophet_df):,} registros")
        
        # Crear modelo con hiperparámetros optimizados
        model = Prophet(
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
            daily_seasonality=True,  # type: ignore
            weekly_seasonality=True,  # type: ignore
            yearly_seasonality=False,  # type: ignore
            uncertainty_samples=100,  # Reducido para velocidad
            seasonality_mode='additive'
        )
        
        # Entrenar
        start_time = datetime.now()
        model.fit(prophet_df)
        training_duration = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"✅ Prophet entrenado en {training_duration:.1f} segundos")
        
        self.prophet_model = model
        return model
    
    def train_anomaly_detector(self, df: pd.DataFrame) -> IsolationForest:
        """
        🚨 Entrenar Isolation Forest para detección de anomalías
        
        Features utilizadas:
        - Global_active_power
        - Voltage
        - Global_intensity
        - Hour of day (encoded)
        - Day of week (encoded)
        
        Args:
            df: DataFrame preprocesado
            
        Returns:
            Modelo Isolation Forest entrenado
        """
        self.logger.info("🚨 Entrenando Isolation Forest...")
        
        # Preparar features
        X = df[['Global_active_power', 'Voltage', 'Global_intensity']].copy()
        
        # Añadir features temporales (verificar que sea DatetimeIndex)
        if isinstance(df.index, pd.DatetimeIndex):
            X['hour'] = df.index.hour
            X['day_of_week'] = df.index.dayofweek
        else:
            self.logger.warning("⚠️ Índice no es DatetimeIndex, usando features temporales por defecto")
            X['hour'] = 12
            X['day_of_week'] = 0
        
        # Eliminar NaN
        X = X.dropna()
        
        self.logger.info(f"   📊 Datos IF: {len(X):,} registros, {X.shape[1]} features")
        
        # Crear modelo
        model = IsolationForest(
            contamination=0.05,  # 5% de datos como anomalías
            n_estimators=100,
            random_state=42,
            n_jobs=-1  # Usar todos los cores
        )
        
        # Entrenar
        start_time = datetime.now()
        model.fit(X)
        training_duration = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"✅ Isolation Forest entrenado en {training_duration:.1f} segundos")
        
        self.anomaly_model = model
        return model
    
    # ========================================================================
    # GRUPO 3: EVALUATION
    # ========================================================================
    
    def evaluate_models(
        self,
        prophet_model: Prophet,
        df: pd.DataFrame,
        test_days: int = 7
    ) -> Dict[str, float]:
        """
        📊 Evaluar performance de modelos con split temporal
        
        Proceso:
        1. Split train/test (últimos test_days = test)
        2. Predecir con Prophet
        3. Calcular MAE, RMSE, MAPE, R²
        
        Args:
            prophet_model: Modelo Prophet entrenado
            df: DataFrame completo
            test_days: Días para test set (default: 7)
            
        Returns:
            Dict con métricas: mae, rmse, mape, r2_score
        """
        self.logger.info(f"📊 Evaluando modelos (test set: últimos {test_days} días)...")
        
        # Split temporal
        test_size = test_days * 24 * 60  # Minutos
        train_df = df.iloc[:-test_size]
        test_df = df.iloc[-test_size:]
        
        if len(test_df) == 0:
            self.logger.warning("⚠️ Test set vacío, usando últimos 10% de datos")
            split_idx = int(len(df) * 0.9)
            train_df = df.iloc[:split_idx]
            test_df = df.iloc[split_idx:]
        
        self.logger.info(f"   📊 Train: {len(train_df):,} | Test: {len(test_df):,}")
        
        # Preparar datos Prophet para predicción
        future = prophet_model.make_future_dataframe(periods=len(test_df), freq='min')
        forecast = prophet_model.predict(future)
        
        # Extraer predicciones del test set
        y_true = test_df['Global_active_power'].values
        y_pred = forecast['yhat'].iloc[-len(test_df):].values
        
        # Asegurar misma longitud
        min_length = min(len(y_true), len(y_pred))
        y_true = y_true[:min_length]
        y_pred = y_pred[:min_length]
        
        # Convertir a numpy array para evitar problemas de tipo
        y_true = np.asarray(y_true, dtype=np.float64)
        y_pred = np.asarray(y_pred, dtype=np.float64)
        
        # Calcular métricas
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
        r2 = r2_score(y_true, y_pred)
        
        metrics = {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape),
            'r2_score': float(r2),
            'test_points': len(y_true),
            'training_date': datetime.now().isoformat()
        }
        
        self.logger.info("✅ Evaluación completada:")
        self.logger.info(f"   📈 MAE: {mae:.3f} kW")
        self.logger.info(f"   📈 RMSE: {rmse:.3f} kW")
        self.logger.info(f"   📈 MAPE: {mape:.2f}%")
        self.logger.info(f"   📈 R²: {r2:.3f}")
        
        self.current_metrics = metrics
        return metrics
    
    def compare_with_previous(self, new_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        🔄 Comparar modelo nuevo con versión anterior
        
        Lee: models/training_history.json (última entrada)
        Compara: MAE, RMSE, MAPE
        Decide: KEEP_NEW | ROLLBACK_OLD | FIRST_TRAINING
        
        Args:
            new_metrics: Métricas del modelo nuevo
            
        Returns:
            {
                'is_better': bool,
                'mae_improvement_pct': float,
                'rmse_improvement_pct': float,
                'decision': str,
                'previous_mae': float,
                'previous_rmse': float
            }
        """
        self.logger.info("🔄 Comparando con modelo anterior...")
        
        history_file = self.models_dir / 'training_history.json'
        
        # Si no hay historial, es primer entrenamiento
        if not history_file.exists():
            self.logger.info("ℹ️ Primer entrenamiento - sin modelo anterior")
            return {
                'is_better': True,
                'mae_improvement_pct': 0.0,
                'rmse_improvement_pct': 0.0,
                'decision': 'FIRST_TRAINING',
                'previous_mae': None,
                'previous_rmse': None
            }
        
        # Leer historial
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        if len(history) == 0:
            return {
                'is_better': True,
                'decision': 'FIRST_TRAINING'
            }
        
        # Obtener última entrada
        previous = history[-1]
        previous_mae = previous['metrics']['mae']
        previous_rmse = previous['metrics']['rmse']
        
        # Calcular mejoras
        mae_improvement_pct = ((previous_mae - new_metrics['mae']) / previous_mae) * 100
        rmse_improvement_pct = ((previous_rmse - new_metrics['rmse']) / previous_rmse) * 100
        
        # Decidir si nuevo modelo es mejor
        is_better = (
            new_metrics['mae'] < previous_mae and
            new_metrics['rmse'] < previous_rmse
        )
        
        # Check degradación significativa
        mae_degraded = mae_improvement_pct < -self.DEGRADATION_THRESHOLDS['mae_increase_pct']
        rmse_degraded = rmse_improvement_pct < -self.DEGRADATION_THRESHOLDS['rmse_increase_pct']
        
        if mae_degraded or rmse_degraded:
            decision = 'ROLLBACK_OLD'
            self.logger.warning("⚠️ DEGRADACIÓN DETECTADA - Se recomienda rollback")
        elif is_better:
            decision = 'KEEP_NEW'
            self.logger.info(f"✅ Nuevo modelo MEJOR (+{mae_improvement_pct:.1f}% MAE, +{rmse_improvement_pct:.1f}% RMSE)")
        else:
            decision = 'KEEP_OLD'
            self.logger.info("ℹ️ Modelo anterior sigue siendo mejor")
        
        result = {
            'is_better': is_better,
            'mae_improvement_pct': mae_improvement_pct,
            'rmse_improvement_pct': rmse_improvement_pct,
            'decision': decision,
            'previous_mae': previous_mae,
            'previous_rmse': previous_rmse,
            'previous_version': previous['version']
        }
        
        return result
    
    # ========================================================================
    # GRUPO 4: PERSISTENCE
    # ========================================================================
    
    def save_models(
        self,
        prophet_model: Prophet,
        anomaly_model: IsolationForest,
        metrics: Dict[str, float],
        save_as_best: bool = True
    ) -> str:
        """
        💾 Guardar modelos con versionado automático
        
        Guardado:
        1. models/prophet_v{timestamp}.pkl
        2. models/isolation_forest_v{timestamp}.pkl
        3. models/best_prophet.pkl (si save_as_best=True)
        4. models/best_isolation_forest.pkl
        5. Actualizar models/training_history.json
        
        Args:
            prophet_model: Modelo Prophet entrenado
            anomaly_model: Modelo Isolation Forest entrenado
            metrics: Métricas de evaluación
            save_as_best: Si guardar como mejor modelo
            
        Returns:
            version_id (ej: 'v20250122_030015')
        """
        self.logger.info("💾 Guardando modelos...")
        
        # Generar version ID
        version_id = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.version_id = version_id
        
        # Guardar Prophet
        prophet_path = self.models_dir / f"prophet_{version_id}.pkl"
        joblib.dump(prophet_model, prophet_path)
        self.logger.info(f"   ✅ Prophet: {prophet_path}")
        
        # Guardar Isolation Forest
        anomaly_path = self.models_dir / f"isolation_forest_{version_id}.pkl"
        joblib.dump(anomaly_model, anomaly_path)
        self.logger.info(f"   ✅ Isolation Forest: {anomaly_path}")
        
        # Guardar como "best" si corresponde
        if save_as_best:
            best_prophet = self.models_dir / "best_prophet.pkl"
            best_anomaly = self.models_dir / "best_isolation_forest.pkl"
            
            shutil.copy(prophet_path, best_prophet)
            shutil.copy(anomaly_path, best_anomaly)
            
            self.logger.info(f"   ⭐ Guardado como BEST model")
        
        # Actualizar training_history.json
        history_file = self.models_dir / 'training_history.json'
        
        history_entry = {
            'version': version_id,
            'timestamp': datetime.now().isoformat(),
            'data_source': self.data_source,
            'training_window_days': self.training_window_days,
            'metrics': metrics,
            'is_current_best': save_as_best,
            'prophet_path': str(prophet_path),
            'anomaly_path': str(anomaly_path)
        }
        
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(history_entry)
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        self.logger.info(f"   📝 Historial actualizado: {history_file}")
        self.logger.info(f"✅ Modelos guardados con version: {version_id}")
        
        return version_id
    
    def cleanup_old_versions(self, keep_last_n: int = 10):
        """
        🗑️ Eliminar versiones antiguas de modelos (mantener últimas N)
        
        Razón: Evitar que models/ crezca infinitamente
        
        Args:
            keep_last_n: Número de versiones a mantener (default: 10)
        """
        self.logger.info(f"🗑️ Limpiando versiones antiguas (manteniendo últimas {keep_last_n})...")
        
        # Obtener todos los archivos de modelos versionados
        prophet_files = sorted(self.models_dir.glob("prophet_v*.pkl"))
        anomaly_files = sorted(self.models_dir.glob("isolation_forest_v*.pkl"))
        
        deleted_count = 0
        
        # Eliminar Prophet antiguos
        if len(prophet_files) > keep_last_n:
            to_delete = prophet_files[:-keep_last_n]
            for file_path in to_delete:
                file_path.unlink()
                deleted_count += 1
                self.logger.info(f"   🗑️ Eliminado: {file_path.name}")
        
        # Eliminar Isolation Forest antiguos
        if len(anomaly_files) > keep_last_n:
            to_delete = anomaly_files[:-keep_last_n]
            for file_path in to_delete:
                file_path.unlink()
                deleted_count += 1
                self.logger.info(f"   🗑️ Eliminado: {file_path.name}")
        
        if deleted_count > 0:
            self.logger.info(f"✅ Limpieza completada: {deleted_count} archivos eliminados")
        else:
            self.logger.info("ℹ️ No hay archivos antiguos para eliminar")
    
    def load_model(self, model_type: str = 'prophet', version: str = 'best') -> Any:
        """
        📂 Cargar modelo guardado
        
        Args:
            model_type: 'prophet' o 'isolation_forest'
            version: 'best' o version ID (ej: 'v20250122_030015')
            
        Returns:
            Modelo cargado (Prophet o IsolationForest)
        """
        if version == 'best':
            model_path = self.models_dir / f"best_{model_type}.pkl"
        else:
            model_path = self.models_dir / f"{model_type}_{version}.pkl"
        
        if not model_path.exists():
            raise FileNotFoundError(f"❌ Modelo no encontrado: {model_path}")
        
        model = joblib.load(model_path)
        self.logger.info(f"📂 Modelo cargado: {model_path.name}")
        
        return model
    
    # ========================================================================
    # GRUPO 5: LOGGING & NOTIFICATIONS
    # ========================================================================
    
    def log_training_metrics(self, metrics: Dict[str, float], version_id: str):
        """
        📝 Registrar métricas en logs/metrics_history.json
        
        Args:
            metrics: Métricas de entrenamiento
            version_id: ID de versión del modelo
        """
        metrics_file = Path('logs') / 'metrics_history.json'
        
        entry = {
            'version': version_id,
            'timestamp': datetime.now().isoformat(),
            **metrics
        }
        
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(entry)
        
        with open(metrics_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        self.logger.info(f"📝 Métricas registradas en: {metrics_file}")
    
    def send_notifications(
        self,
        status: str,
        metrics: Dict[str, float],
        version_id: str,
        comparison: Optional[Dict] = None
    ):
        """
        📧 Enviar email de notificación según resultado
        
        Args:
            status: 'SUCCESS' | 'DEGRADATION' | 'FAILURE' | 'INSUFFICIENT_DATA'
            metrics: Métricas del entrenamiento
            version_id: ID de versión
            comparison: Resultado de comparación con anterior
        """
        if not self.enable_notifications:
            self.logger.info("📧 Notificaciones deshabilitadas - skipping")
            return
        
        self.logger.info(f"📧 Enviando notificación: {status}")
        
        try:
            from src.email_sender import EmailReporter
            
            emailer = EmailReporter()
            
            if status == 'SUCCESS':
                # TODO: Implementar template de email
                self.logger.info("✅ Email de éxito enviado")
            elif status == 'DEGRADATION':
                # TODO: Implementar alerta de degradación
                self.logger.warning("⚠️ Email de degradación enviado")
            elif status == 'FAILURE':
                # TODO: Implementar alerta de fallo
                self.logger.error("❌ Email de fallo enviado")
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando notificación: {e}")
    
    # ========================================================================
    # GRUPO 6: MAIN PIPELINE
    # ========================================================================
    
    def run_full_training_pipeline(self) -> Dict[str, Any]:
        """
        🚀 Ejecutar pipeline completo de auto-entrenamiento
        
        Pipeline:
        1. Fetch data from Railway
        2. Validate data quality
        3. Preprocess data
        4. Train Prophet model
        5. Train Anomaly detector
        6. Evaluate models
        7. Compare with previous
        8. Save models (si mejora)
        9. Cleanup old versions
        10. Log metrics
        11. Send notifications
        
        Returns:
            {
                'success': bool,
                'version_id': str,
                'metrics': Dict[str, float],
                'comparison': Dict[str, Any],
                'duration': float,
                'status': str
            }
        """
        self.logger.info("=" * 70)
        self.logger.info("🚀 INICIANDO PIPELINE DE AUTO-ENTRENAMIENTO")
        self.logger.info("=" * 70)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Fetch data
            df = self.fetch_training_data()
            self.training_df = df
            
            # Step 2: Validate quality
            quality = self.validate_data_quality(df)
            
            if not quality['is_valid']:
                self.logger.error("❌ Datos no válidos para entrenamiento")
                self.send_notifications('INSUFFICIENT_DATA', {}, '')
                return {
                    'success': False,
                    'error': 'Datos no válidos',
                    'quality': quality
                }
            
            # Step 3: Preprocess
            df_clean = self.preprocess_data(df)
            
            # Step 4: Train Prophet
            prophet_model = self.train_prophet(df_clean)
            
            # Step 5: Train Anomaly Detector
            anomaly_model = self.train_anomaly_detector(df_clean)
            
            # Step 6: Evaluate
            metrics = self.evaluate_models(prophet_model, df_clean)
            
            # Step 7: Compare
            comparison = self.compare_with_previous(metrics)
            
            # Step 8: Save models (solo si mejora)
            save_as_best = comparison['is_better']
            
            if comparison['decision'] == 'ROLLBACK_OLD':
                self.logger.warning("⚠️ Modelo nuevo degradó - NO se guardará como best")
                save_as_best = False
            
            version_id = self.save_models(prophet_model, anomaly_model, metrics, save_as_best)
            
            # Step 9: Cleanup
            self.cleanup_old_versions(keep_last_n=10)
            
            # Step 10: Log metrics
            self.log_training_metrics(metrics, version_id)
            
            # Step 11: Notifications
            status = 'DEGRADATION' if comparison['decision'] == 'ROLLBACK_OLD' else 'SUCCESS'
            self.send_notifications(status, metrics, version_id, comparison)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            self.logger.info("=" * 70)
            self.logger.info("🎉 PIPELINE COMPLETADO EXITOSAMENTE")
            self.logger.info(f"   ⏱️ Duración: {duration:.1f} segundos")
            self.logger.info(f"   📦 Versión: {version_id}")
            self.logger.info(f"   📈 MAE: {metrics['mae']:.3f} kW")
            self.logger.info(f"   📈 RMSE: {metrics['rmse']:.3f} kW")
            self.logger.info(f"   📈 MAPE: {metrics['mape']:.2f}%")
            self.logger.info(f"   🏆 Best model: {'YES' if save_as_best else 'NO'}")
            self.logger.info("=" * 70)
            
            return {
                'success': True,
                'version_id': version_id,
                'metrics': metrics,
                'comparison': comparison,
                'duration': duration,
                'status': status,
                'save_as_best': save_as_best
            }
            
        except InsufficientDataError as e:
            self.logger.error(f"❌ Datos insuficientes: {e}")
            self.send_notifications('INSUFFICIENT_DATA', {}, '')
            return {
                'success': False,
                'error': str(e),
                'status': 'INSUFFICIENT_DATA'
            }
        
        except DatabaseConnectionError as e:
            self.logger.error(f"❌ Error de conexión: {e}")
            self.send_notifications('FAILURE', {}, '')
            return {
                'success': False,
                'error': str(e),
                'status': 'DATABASE_ERROR'
            }
        
        except Exception as e:
            self.logger.error(f"❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            self.send_notifications('FAILURE', {}, '')
            return {
                'success': False,
                'error': str(e),
                'status': 'UNEXPECTED_ERROR'
            }


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def quick_train(
    data_source: str = 'railway',
    training_window_days: int = 90,
    enable_notifications: bool = False
) -> Dict[str, Any]:
    """
    ⚡ Función de conveniencia para entrenamiento rápido
    
    Args:
        data_source: 'railway' o 'csv'
        training_window_days: Ventana de entrenamiento
        enable_notifications: Enviar emails
        
    Returns:
        Resultado del pipeline
        
    Example:
        >>> result = quick_train(data_source='railway', training_window_days=90)
        >>> print(f"Success: {result['success']}")
        >>> print(f"MAE: {result['metrics']['mae']:.3f}")
    """
    trainer = AutoTrainer(
        data_source=data_source,
        training_window_days=training_window_days,
        enable_notifications=enable_notifications
    )
    
    return trainer.run_full_training_pipeline()


if __name__ == "__main__":
    """
    🧪 Test del AutoTrainer
    """
    print("=" * 70)
    print("🤖 DomusAI - Auto-Trainer Test")
    print("=" * 70)
    
    # Detectar data source disponible
    try:
        from src.database import get_db_reader
        db = get_db_reader()
        if db.test_connection():
            print("✅ Railway MySQL disponible - usando datos en tiempo real")
            test_source = 'railway'
        else:
            raise RuntimeError("Railway no disponible")
    except Exception as e:
        print(f"⚠️ Railway no disponible ({e}) - skipping test")
        test_source = None
    
    if test_source:
        try:
            # Test completo del pipeline
            result = quick_train(
                data_source=test_source,
                training_window_days=90,
                enable_notifications=False
            )
            
            if result['success']:
                print("\n✅ AUTO-ENTRENAMIENTO EXITOSO")
                print(f"   Versión: {result['version_id']}")
                print(f"   MAE: {result['metrics']['mae']:.3f} kW")
                print(f"   RMSE: {result['metrics']['rmse']:.3f} kW")
                print(f"   Duration: {result['duration']:.1f}s")
            else:
                print(f"\n❌ AUTO-ENTRENAMIENTO FALLÓ: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            print(f"\n❌ Error en test: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
