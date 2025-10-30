"""
DomusAI - Sistema de Detección de Anomalías en Consumo Energético

Este módulo implementa múltiples métodos de detección de anomalías basados en
los experimentos validados en notebooks/03_anomalias.ipynb.

Autor: DomusAI Team
Fecha: Octubre 2025
Versión: 1.0
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path

# Machine Learning
from sklearn.ensemble import IsolationForest
from scipy import stats

# Configuración de logging
import sys
# Path ya importado arriba en línea 18

# Crear directorio de logs si no existe
Path('logs').mkdir(exist_ok=True)

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    # Para el StreamHandler (consola)
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/anomalies.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    📊 Detector de anomalías en series temporales de consumo energético.
    
    Implementa 5 métodos diferentes de detección:
    1. IQR (Inter-Quartile Range) - Estadístico básico
    2. Z-Score - Desviaciones estándar
    3. Isolation Forest - Machine Learning
    4. Moving Average - Contexto temporal
    5. Prediction-Based - Comparación con forecast
    
    Compatible con Railway MySQL (datos en tiempo real) y CSV legacy.
    
    Attributes:
        method (str): Método principal de detección ('isolation_forest' por defecto)
        params (dict): Parámetros óptimos validados en experimentación
        
    Example:
        >>> # Con Railway MySQL (RECOMENDADO)
        >>> from src.anomalies import AnomalyDetector, load_data
        >>> df = load_data(source='railway')
        >>> detector = AnomalyDetector(method='isolation_forest')
        >>> results = detector.detect(df, consensus_threshold=3)
        >>> print(f"Anomalías detectadas: {len(results['high_confidence_anomalies'])}")
        >>> 
        >>> # Con CSV legacy
        >>> df = load_data(source='csv', csv_path='data/Dataset_clean_test.csv')
        >>> detector = AnomalyDetector(method='isolation_forest')
        >>> results = detector.detect(df, method='all')
    """
    
    # Parámetros óptimos encontrados en experimentación (03_anomalias.ipynb)
    OPTIMAL_PARAMS = {
        'iqr': {
            'multiplier': 1.5
        },
        'zscore': {
            'threshold': 3.0
        },
        'isolation_forest': {
            'contamination': 0.05,
            'n_estimators': 100,
            'random_state': 42
        },
        'moving_average': {
            'window': 60,
            'threshold': 0.30
        },
        'prediction_based': {
            'horizon_days': 7,
            'threshold': 0.30
        }
    }
    
    # Configuración de alertas por tipo
    ALERT_CONFIG = {
        'type_1_high_consumption': {
            'severity': 'critical',
            'description': 'Consumo excesivo detectado',
            'action': 'email_immediate'
        },
        'type_2_low_consumption': {
            'severity': 'medium',
            'description': 'Consumo anormalmente bajo',
            'action': 'email_daily'
        },
        'type_3_temporal': {
            'severity': 'critical',
            'description': 'Consumo alto en horas valle',
            'action': 'email_immediate'
        },
        'type_4_sensor_failure': {
            'severity': 'low',
            'description': 'Posible fallo de sensor',
            'action': 'log_only'
        }
    }
    
    def __init__(
        self, 
        method: str = 'isolation_forest',
        custom_params: Optional[Dict] = None,
        enable_logging: bool = True
    ):
        """
        Inicializa el detector de anomalías.
        
        Args:
            method: Método principal ('isolation_forest', 'zscore', 'iqr', etc.)
            custom_params: Parámetros personalizados (sobrescriben defaults)
            enable_logging: Activar logging de operaciones
        """
        self.method = method
        self.enable_logging = enable_logging
        
        # Cargar parámetros
        self.params = self.OPTIMAL_PARAMS.copy()
        if custom_params:
            self.params.update(custom_params)
        
        # Modelos entrenados
        self.models = {}
        
        if self.enable_logging:
            logger.info(f"🔧 AnomalyDetector inicializado (método: {method})")
    
    
    # ========================================================================
    # MÉTODO 1: IQR (Inter-Quartile Range)
    # ========================================================================
    
    def detect_iqr(
        self, 
        df: pd.DataFrame, 
        column: str = 'Global_active_power'
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Detecta anomalías usando el método IQR (Inter-Quartile Range).
        
        Fórmula:
            Outliers = valores fuera de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
        
        Args:
            df: DataFrame con datos de consumo
            column: Columna a analizar
            
        Returns:
            Tuple con (anomalies_df, stats_dict)
        """
        multiplier = self.params['iqr']['multiplier']
        
        # Calcular cuartiles
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        # Calcular límites
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        # Detectar anomalías
        anomalies = df[(df[column] < lower_bound) | (df[column] > upper_bound)].copy()
        
        # Estadísticas
        stats = {
            'method': 'iqr',
            'Q1': float(Q1),
            'Q3': float(Q3),
            'IQR': float(IQR),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'total_anomalies': len(anomalies),
            'anomaly_rate': len(anomalies) / len(df) * 100,
            'below_lower': int((df[column] < lower_bound).sum()),
            'above_upper': int((df[column] > upper_bound).sum())
        }
        
        if self.enable_logging:
            logger.info(f"📊 IQR: {stats['total_anomalies']:,} anomalías ({stats['anomaly_rate']:.2f}%)")
        
        return anomalies, stats
    
    
    # ========================================================================
    # MÉTODO 2: Z-Score
    # ========================================================================
    
    def detect_zscore(
        self, 
        df: pd.DataFrame, 
        column: str = 'Global_active_power'
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Detecta anomalías usando Z-Score (desviaciones estándar).
        
        Fórmula:
            Z = (X - μ) / σ
            Anomalía si |Z| > threshold (default: 3.0)
        
        Args:
            df: DataFrame con datos de consumo
            column: Columna a analizar
            
        Returns:
            Tuple con (anomalies_df, stats_dict)
        """
        threshold = self.params['zscore']['threshold']
        
        # Calcular media y desviación estándar
        mean = df[column].mean()
        std = df[column].std()
        
        # Calcular Z-Score
        z_scores = np.abs((df[column] - mean) / std)
        
        # Detectar anomalías
        anomalies = df[z_scores > threshold].copy()
        anomalies['z_score'] = z_scores[z_scores > threshold]
        
        # Estadísticas
        stats = {
            'method': 'zscore',
            'mean': float(mean),
            'std': float(std),
            'threshold': float(threshold),
            'total_anomalies': len(anomalies),
            'anomaly_rate': len(anomalies) / len(df) * 100,
            'max_z_score': float(z_scores.max())
        }
        
        if self.enable_logging:
            logger.info(f"📊 Z-Score: {stats['total_anomalies']:,} anomalías ({stats['anomaly_rate']:.2f}%)")
        
        return anomalies, stats
    
    
    # ========================================================================
    # MÉTODO 3: Isolation Forest (PRINCIPAL)
    # ========================================================================
    
    def detect_isolation_forest(
        self, 
        df: pd.DataFrame, 
        columns: List[str] = ['Global_active_power', 'Voltage', 'Global_intensity']
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Detecta anomalías usando Isolation Forest (sklearn).
        
        Este es el método PRINCIPAL recomendado para producción por su balance
        entre precisión, velocidad y configurabilidad.
        
        Args:
            df: DataFrame con datos de consumo
            columns: Lista de columnas a usar como features
            
        Returns:
            Tuple con (anomalies_df, stats_dict)
        """
        params = self.params['isolation_forest']
        
        # Preparar datos
        X = df[columns].values
        
        # Entrenar modelo
        iso_forest = IsolationForest(
            contamination=params['contamination'],
            n_estimators=params['n_estimators'],
            random_state=params['random_state']
        )
        
        if self.enable_logging:
            logger.info(f"🔄 Entrenando Isolation Forest (contamination={params['contamination']})...")
        
        predictions = iso_forest.fit_predict(X)
        
        # Obtener scores de anomalía
        anomaly_scores = iso_forest.score_samples(X)
        
        # Detectar anomalías (predictions == -1)
        anomalies = df[predictions == -1].copy()
        anomalies['anomaly_score'] = anomaly_scores[predictions == -1]
        
        # Guardar modelo entrenado
        self.models['isolation_forest'] = iso_forest
        
        # Estadísticas
        stats = {
            'method': 'isolation_forest',
            'contamination': float(params['contamination']),
            'n_estimators': int(params['n_estimators']),
            'total_anomalies': len(anomalies),
            'anomaly_rate': len(anomalies) / len(df) * 100,
            'mean_anomaly_score': float(anomaly_scores[predictions == -1].mean()),
            'mean_normal_score': float(anomaly_scores[predictions == 1].mean())
        }
        
        if self.enable_logging:
            logger.info(f"📊 Isolation Forest: {stats['total_anomalies']:,} anomalías ({stats['anomaly_rate']:.2f}%)")
        
        return anomalies, stats
    
    
    # ========================================================================
    # MÉTODO 4: Moving Average
    # ========================================================================
    
    def detect_moving_average(
        self, 
        df: pd.DataFrame, 
        column: str = 'Global_active_power'
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Detecta anomalías basadas en desviación respecto a media móvil.
        
        Útil para detectar picos súbitos que métodos estáticos no capturan.
        
        Args:
            df: DataFrame con datos de consumo
            column: Columna a analizar
            
        Returns:
            Tuple con (anomalies_df, stats_dict)
        """
        window = self.params['moving_average']['window']
        threshold = self.params['moving_average']['threshold']
        
        # Calcular media móvil
        df_copy = df.copy()
        df_copy['ma'] = df_copy[column].rolling(window=window, center=False).mean()
        
        # Calcular desviación relativa
        df_copy['deviation'] = np.abs(df_copy[column] - df_copy['ma']) / df_copy['ma']
        
        # Detectar anomalías
        valid_data = df_copy.dropna(subset=['ma', 'deviation'])
        anomalies = valid_data[valid_data['deviation'] > threshold].copy()
        
        # Estadísticas
        stats = {
            'method': 'moving_average',
            'window': int(window),
            'threshold': float(threshold),
            'total_anomalies': len(anomalies),
            'anomaly_rate': len(anomalies) / len(valid_data) * 100 if len(valid_data) > 0 else 0,
            'mean_deviation': float(anomalies['deviation'].mean()) if len(anomalies) > 0 else 0,
            'max_deviation': float(anomalies['deviation'].max()) if len(anomalies) > 0 else 0
        }
        
        if self.enable_logging:
            logger.info(f"📊 Moving Average: {stats['total_anomalies']:,} anomalías ({stats['anomaly_rate']:.2f}%)")
        
        return anomalies, stats
    
    
    # ========================================================================
    # MÉTODO 5: Prediction-Based (requiere predictor)
    # ========================================================================
    
    def detect_prediction_based(
        self, 
        df: pd.DataFrame,
        predictor,
        column: str = 'Global_active_power'
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Detecta anomalías comparando valores reales vs predicciones.
        
        NOTA: Requiere instancia de EnergyPredictor ya entrenada.
        Es el método más costoso computacionalmente (~60s).
        
        Args:
            df: DataFrame con datos reales
            predictor: Instancia de EnergyPredictor con modelo entrenado
            column: Columna a analizar
            
        Returns:
            Tuple con (anomalies_df, stats_dict)
        """
        horizon_days = self.params['prediction_based']['horizon_days']
        threshold = self.params['prediction_based']['threshold']
        
        if self.enable_logging:
            logger.info(f"🔮 Generando predicción para {horizon_days} días...")
        
        # Generar predicción
        prediction = predictor.predict(horizon_days=horizon_days, model='prophet')
        
        # Obtener valores reales del período predicho
        total_hours = horizon_days * 24
        real_values = df[column].iloc[-total_hours:].values
        predicted_values = np.array(prediction['predictions'])
        timestamps = df.index[-total_hours:]
        
        # Calcular desviaciones relativas
        predicted_values_safe = np.where(predicted_values == 0, 0.001, predicted_values)
        deviations = np.abs(real_values - predicted_values) / predicted_values_safe
        
        # Detectar anomalías
        anomaly_mask = deviations > threshold
        anomaly_indices = timestamps[anomaly_mask]
        
        # Crear DataFrame de anomalías
        anomalies = df.loc[anomaly_indices].copy()
        anomalies['predicted_value'] = predicted_values[anomaly_mask]
        anomalies['deviation'] = deviations[anomaly_mask]
        
        # Estadísticas
        stats = {
            'method': 'prediction_based',
            'horizon_days': int(horizon_days),
            'threshold': float(threshold),
            'total_points': len(real_values),
            'total_anomalies': len(anomalies),
            'anomaly_rate': len(anomalies) / len(real_values) * 100,
            'mean_deviation': float(deviations[anomaly_mask].mean()) if len(anomalies) > 0 else 0,
            'max_deviation': float(deviations[anomaly_mask].max()) if len(anomalies) > 0 else 0,
            'prediction_mae': float(np.mean(np.abs(real_values - predicted_values))),
            'prediction_rmse': float(np.sqrt(np.mean((real_values - predicted_values)**2)))
        }
        
        if self.enable_logging:
            logger.info(f"📊 Prediction-Based: {stats['total_anomalies']:,} anomalías ({stats['anomaly_rate']:.2f}%)")
        
        return anomalies, stats
    
    
    # ========================================================================
    # DETECCIÓN CON TODOS LOS MÉTODOS Y CONSENSO
    # ========================================================================
    
    def detect_all_methods(
        self, 
        df: pd.DataFrame,
        column: str = 'Global_active_power',
        predictor = None,
        consensus_threshold: int = 3
    ) -> Dict:
        """
        Detecta anomalías con todos los métodos y calcula consenso.
        
        Esta es la función PRINCIPAL para detección robusta en producción.
        
        Args:
            df: DataFrame con datos de consumo
            column: Columna principal a analizar
            predictor: (Opcional) EnergyPredictor para método prediction-based
            consensus_threshold: Mínimo de métodos para considerar anomalía de alto consenso (default: 3)
            
        Returns:
            Dict con resultados completos:
                - anomalies_by_method: Dict con anomalías de cada método
                - stats_by_method: Dict con estadísticas de cada método
                - consensus_anomalies: Anomalías detectadas por ≥ consensus_threshold métodos
                - classified_anomalies: Anomalías clasificadas por tipo
                - summary: Resumen ejecutivo
        """
        if self.enable_logging:
            logger.info("=" * 80)
            logger.info("🔍 INICIANDO DETECCIÓN MULTI-MÉTODO DE ANOMALÍAS")
            logger.info("=" * 80)
        
        results = {
            'anomalies_by_method': {},
            'stats_by_method': {},
            'consensus_anomalies': pd.DataFrame(),
            'classified_anomalies': {},
            'summary': {}
        }
        
        # 1. IQR
        anomalies_iqr, stats_iqr = self.detect_iqr(df, column)
        results['anomalies_by_method']['iqr'] = anomalies_iqr
        results['stats_by_method']['iqr'] = stats_iqr
        
        # 2. Z-Score
        anomalies_zscore, stats_zscore = self.detect_zscore(df, column)
        results['anomalies_by_method']['zscore'] = anomalies_zscore
        results['stats_by_method']['zscore'] = stats_zscore
        
        # 3. Isolation Forest (PRINCIPAL)
        anomalies_isoforest, stats_isoforest = self.detect_isolation_forest(df)
        results['anomalies_by_method']['isolation_forest'] = anomalies_isoforest
        results['stats_by_method']['isolation_forest'] = stats_isoforest
        
        # 4. Moving Average
        anomalies_ma, stats_ma = self.detect_moving_average(df, column)
        results['anomalies_by_method']['moving_average'] = anomalies_ma
        results['stats_by_method']['moving_average'] = stats_ma
        
        # 5. Prediction-Based (opcional)
        if predictor is not None:
            anomalies_pred, stats_pred = self.detect_prediction_based(df, predictor, column)
            results['anomalies_by_method']['prediction_based'] = anomalies_pred
            results['stats_by_method']['prediction_based'] = stats_pred
        
        # Calcular consenso
        if self.enable_logging:
            logger.info("\n🔍 Calculando consenso entre métodos...")
        
        consensus_anomalies = self._calculate_consensus(
            results['anomalies_by_method'],
            consensus_threshold
        )
        results['consensus_anomalies'] = consensus_anomalies
        
        # Clasificar anomalías por tipo
        if len(consensus_anomalies) > 0:
            classified = self.classify_anomalies(df, consensus_anomalies)
            results['classified_anomalies'] = classified
        
        # Generar resumen
        results['summary'] = self._generate_summary(results, consensus_threshold)
        
        if self.enable_logging:
            logger.info("=" * 80)
            logger.info(f"✅ DETECCIÓN COMPLETADA")
            logger.info(f"🎯 Anomalías de alto consenso (≥{consensus_threshold} métodos): {len(consensus_anomalies):,}")
            logger.info("=" * 80)
        
        return results
    
    
    def _calculate_consensus(
        self, 
        anomalies_by_method: Dict[str, pd.DataFrame],
        threshold: int = 3
    ) -> pd.DataFrame:
        """
        Calcula consenso entre múltiples métodos de detección.
        
        Args:
            anomalies_by_method: Dict con anomalías de cada método
            threshold: Mínimo de métodos para incluir en consenso
            
        Returns:
            DataFrame con anomalías detectadas por ≥ threshold métodos
        """
        from itertools import combinations
        
        # Convertir a sets de índices
        all_sets = [set(anomalies.index) for anomalies in anomalies_by_method.values()]
        
        # Calcular consenso para threshold métodos
        consensus_indices = set()
        
        # Para cada combinación de 'threshold' métodos
        for combo in combinations(range(len(all_sets)), threshold):
            intersection = all_sets[combo[0]]
            for idx in combo[1:]:
                intersection = intersection & all_sets[idx]
            consensus_indices.update(intersection)
        
        # Obtener DataFrame original (usar primer método como referencia)
        reference_df = list(anomalies_by_method.values())[0]
        original_df = reference_df if hasattr(reference_df, 'index') else pd.DataFrame()
        
        # Extraer anomalías de consenso del DataFrame original completo
        # Necesitamos el DataFrame original completo
        if len(consensus_indices) > 0:
            # Asumiendo que tenemos acceso al DataFrame original
            # (esto se puede mejorar pasando df como parámetro)
            consensus_anomalies = reference_df.loc[list(consensus_indices)]
        else:
            consensus_anomalies = pd.DataFrame()
        
        return consensus_anomalies
    
    
    # ========================================================================
    # CLASIFICACIÓN DE TIPOS DE ANOMALÍAS
    # ========================================================================
    
    def classify_anomalies(
        self, 
        df: pd.DataFrame, 
        anomalies: pd.DataFrame,
        column: str = 'Global_active_power'
    ) -> Dict[str, pd.DataFrame]:
        """
        Clasifica anomalías en 4 tipos según su naturaleza.
        
        Tipos:
            - Tipo 1: Consumo Excesivo (> P95)
            - Tipo 2: Consumo Bajo Anormal (< P05)
            - Tipo 3: Anomalía Temporal (consumo alto en horas valle)
            - Tipo 4: Posible Fallo de Sensor (valores constantes)
        
        Args:
            df: DataFrame completo con todos los datos
            anomalies: DataFrame con anomalías detectadas
            column: Columna de consumo a analizar
            
        Returns:
            Dict con anomalías clasificadas por tipo
        """
        if len(anomalies) == 0:
            return {
                'type_1_high_consumption': pd.DataFrame(),
                'type_2_low_consumption': pd.DataFrame(),
                'type_3_temporal': pd.DataFrame(),
                'type_4_sensor_failure': pd.DataFrame()
            }
        
        # Calcular umbrales
        p95 = df[column].quantile(0.95)
        p05 = df[column].quantile(0.05)
        mean = df[column].mean()
        
        if self.enable_logging:
            logger.info(f"\n📊 Umbrales de clasificación:")
            logger.info(f"   P95 (alto): {p95:.3f} kW")
            logger.info(f"   Media: {mean:.3f} kW")
            logger.info(f"   P05 (bajo): {p05:.3f} kW")
        
        # Tipo 1: Consumo excesivo
        type_1 = anomalies[anomalies[column] > p95].copy()
        type_1['anomaly_type'] = 'High Consumption'
        type_1['severity'] = 'critical'
        
        # Tipo 2: Consumo bajo anormal
        type_2 = anomalies[anomalies[column] < p05].copy()
        type_2['anomaly_type'] = 'Low Consumption'
        type_2['severity'] = 'medium'
        
        # Tipo 3: Anomalías temporales
        anomalies_with_hour = anomalies.copy()
        anomalies_with_hour['hour'] = pd.to_datetime(anomalies_with_hour.index).hour
        type_3 = anomalies_with_hour[
            (anomalies_with_hour['hour'] >= 2) & 
            (anomalies_with_hour['hour'] <= 5) &
            (anomalies_with_hour[column] > mean * 1.5)
        ].copy()
        type_3['anomaly_type'] = 'Temporal Anomaly'
        type_3['severity'] = 'critical'
        
        # Tipo 4: Posible fallo de sensor
        df_with_diff = df.copy()
        df_with_diff['power_diff'] = df_with_diff[column].diff().abs()
        constant_mask = df_with_diff['power_diff'] < 0.001
        constant_periods = df_with_diff[constant_mask]
        
        type_4 = anomalies[anomalies.index.isin(constant_periods.index)].copy()
        type_4['anomaly_type'] = 'Sensor Failure'
        type_4['severity'] = 'low'
        
        classified = {
            'type_1_high_consumption': type_1,
            'type_2_low_consumption': type_2,
            'type_3_temporal': type_3,
            'type_4_sensor_failure': type_4
        }
        
        if self.enable_logging:
            logger.info(f"\n📊 DISTRIBUCIÓN POR TIPO:")
            for type_name, anomalies_type in classified.items():
                logger.info(f"   {type_name}: {len(anomalies_type):,}")
        
        return classified
    
    
    # ========================================================================
    # GENERACIÓN DE ALERTAS
    # ========================================================================
    
    def generate_alerts(
        self, 
        classified_anomalies: Dict[str, pd.DataFrame]
    ) -> List[Dict]:
        """
        Genera alertas automáticas según severidad de anomalías.
        
        Args:
            classified_anomalies: Dict con anomalías clasificadas por tipo
            
        Returns:
            Lista de alertas con formato:
                [{
                    'timestamp': datetime,
                    'type': str,
                    'severity': str,
                    'description': str,
                    'action': str,
                    'value': float,
                    'details': dict
                }, ...]
        """
        alerts = []
        
        for type_name, anomalies in classified_anomalies.items():
            if len(anomalies) == 0:
                continue
            
            config = self.ALERT_CONFIG.get(type_name, {})
            
            for idx, row in anomalies.iterrows():
                alert = {
                    'timestamp': idx,
                    'type': type_name,
                    'severity': config.get('severity', 'medium'),
                    'description': config.get('description', 'Anomalía detectada'),
                    'action': config.get('action', 'log_only'),
                    'value': float(row.get('Global_active_power', 0)),
                    'details': row.to_dict()
                }
                alerts.append(alert)
        
        # Ordenar por severidad (critical primero)
        severity_order = {'critical': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: (severity_order.get(x['severity'], 3), x['timestamp']))
        
        if self.enable_logging:
            critical_count = sum(1 for a in alerts if a['severity'] == 'critical')
            logger.info(f"\n🚨 Alertas generadas: {len(alerts)} total ({critical_count} críticas)")
        
        return alerts
    
    
    # ========================================================================
    # EXPORTACIÓN Y PERSISTENCIA
    # ========================================================================
    
    def save_results(
        self, 
        results: Dict,
        output_dir: str = 'data'
    ) -> None:
        """
        Guarda resultados de detección en archivos CSV y JSON.
        
        Args:
            results: Dict con resultados completos de detect_all_methods()
            output_dir: Directorio de salida
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Guardar anomalías de consenso
        if len(results['consensus_anomalies']) > 0:
            filename = output_path / f'anomalies_consensus_{timestamp}.csv'
            results['consensus_anomalies'].to_csv(filename)
            logger.info(f"✅ Guardado: {filename}")
        
        # 2. Guardar anomalías clasificadas
        for type_name, anomalies in results.get('classified_anomalies', {}).items():
            if len(anomalies) > 0:
                filename = output_path / f'anomalies_{type_name}_{timestamp}.csv'
                anomalies.to_csv(filename)
                logger.info(f"✅ Guardado: {filename}")
        
        # 3. Guardar resumen JSON
        summary_file = output_path / f'anomalies_summary_{timestamp}.json'
        with open(summary_file, 'w') as f:
            json.dump(results['summary'], f, indent=2, default=str)
        logger.info(f"✅ Guardado: {summary_file}")
    
    
    def _generate_summary(
        self, 
        results: Dict,
        consensus_threshold: int
    ) -> Dict:
        """
        Genera resumen ejecutivo de detección.
        
        Args:
            results: Dict con resultados completos
            consensus_threshold: Umbral de consenso usado
            
        Returns:
            Dict con resumen estadístico
        """
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'consensus_threshold': consensus_threshold,
            'methods_used': list(results['stats_by_method'].keys()),
            'stats_by_method': results['stats_by_method'],
            'consensus': {
                'total_anomalies': len(results['consensus_anomalies']),
                'anomaly_rate': len(results['consensus_anomalies']) / 
                               results['stats_by_method']['iqr'].get('total_anomalies', 1) * 100
            },
            'classification': {
                type_name: len(anomalies) 
                for type_name, anomalies in results.get('classified_anomalies', {}).items()
            },
            'parameters': self.params
        }
        
        return summary
    
    
    # ========================================================================
    # MÉTODO SIMPLIFICADO PARA PRODUCCIÓN
    # ========================================================================
    
    def detect(
        self, 
        df: pd.DataFrame,
        method: Optional[str] = None,
        consensus_threshold: int = 3,
        classify: bool = True,
        save: bool = False
    ) -> Dict:
        """
        Método simplificado para detección en producción.
        
        Este es el método de alto nivel más conveniente para uso diario.
        
        Args:
            df: DataFrame con datos de consumo
            method: Método a usar ('all', 'isolation_forest', 'zscore', etc.)
                   Si None, usa self.method. Si 'all', ejecuta todos.
            consensus_threshold: Umbral para consenso (solo si method='all')
            classify: Clasificar anomalías por tipo
            save: Guardar resultados automáticamente
            
        Returns:
            Dict con resultados completos
            
        Example:
            >>> detector = AnomalyDetector()
            >>> results = detector.detect(df, method='all', save=True)
            >>> print(f"Anomalías críticas: {len(results['alerts'])}")
        """
        method = method or self.method
        
        if method == 'all':
            # Detección con todos los métodos
            results = self.detect_all_methods(df, consensus_threshold=consensus_threshold)
        else:
            # Detección con método único
            if method == 'iqr':
                anomalies, stats = self.detect_iqr(df)
            elif method == 'zscore':
                anomalies, stats = self.detect_zscore(df)
            elif method == 'isolation_forest':
                anomalies, stats = self.detect_isolation_forest(df)
            elif method == 'moving_average':
                anomalies, stats = self.detect_moving_average(df)
            else:
                raise ValueError(f"Método desconocido: {method}")
            
            results = {
                'anomalies': anomalies,
                'stats': stats,
                'consensus_anomalies': anomalies,
                'classified_anomalies': {},
                'summary': {'method': method, 'stats': stats}
            }
        
        # Clasificar anomalías
        if classify and len(results.get('consensus_anomalies', pd.DataFrame())) > 0:
            classified = self.classify_anomalies(df, results['consensus_anomalies'])
            results['classified_anomalies'] = classified
            
            # Generar alertas
            alerts = self.generate_alerts(classified)
            results['alerts'] = alerts
        
        # Guardar resultados
        if save:
            self.save_results(results)
        
        return results


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def load_data(
    source: str = 'railway',
    csv_path: Optional[str] = None,
    db_reader = None,
    file_path: Optional[str] = None  # Deprecated, mantener para backward compatibility
) -> pd.DataFrame:
    """
    🔄 Carga dataset de consumo desde Railway MySQL o CSV.
    
    Soporta múltiples orígenes de datos:
    - Railway MySQL: Datos en tiempo real desde cloud (RECOMENDADO)
    - CSV: Archivos locales para testing/desarrollo (LEGACY)
    
    Args:
        source: Origen de datos - 'railway' (recomendado) | 'csv' (legacy)
        csv_path: Ruta al archivo CSV si source='csv'
        db_reader: Instancia de RailwayDatabaseReader (opcional)
        file_path: DEPRECATED - usar csv_path
        
    Returns:
        DataFrame con datos indexados por Datetime
        
    Raises:
        ValueError: Si source inválido o parámetros faltantes
        RuntimeError: Si Railway no disponible cuando source='railway'
        
    Example:
        >>> # Railway (RECOMENDADO)
        >>> df = load_data(source='railway')
        >>> 
        >>> # CSV legacy
        >>> df = load_data(source='csv', csv_path='data/Dataset_clean_test.csv')
    """
    # Backward compatibility: file_path → csv_path
    if file_path is not None:
        import warnings
        warnings.warn(
            "Parámetro 'file_path' deprecated. Usar 'csv_path' y 'source' en su lugar.",
            DeprecationWarning,
            stacklevel=2
        )
        csv_path = file_path
        source = 'csv'
    
    # Validar source
    if source not in ['railway', 'csv']:
        raise ValueError(f"source debe ser 'railway' o 'csv', recibido: {source}")
    
    # Cargar según origen
    if source == 'railway':
        logger.info("🔄 Cargando datos desde Railway MySQL...")
        
        try:
            # Importar database module
            from src.database import get_db_reader
            reader = db_reader or get_db_reader()
            
            # Test de conexión
            if not reader.test_connection():
                raise RuntimeError("❌ Railway MySQL no disponible - verificar conexión")
            
            # Obtener todos los datos
            df = reader.get_all_data()
            
            if df is None or len(df) == 0:
                raise ValueError("❌ Railway devolvió DataFrame vacío - verificar datos")
            
            # Validar formato
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            
            logger.info(f"✅ Datos Railway cargados: {len(df):,} registros")
            logger.info(f"📅 Período: {df.index.min()} a {df.index.max()}")
            
        except ImportError as e:
            error_msg = f"❌ Módulo database.py no encontrado: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        except Exception as e:
            error_msg = f"❌ Error cargando datos Railway: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    elif source == 'csv':
        if not csv_path:
            raise ValueError("❌ csv_path requerido cuando source='csv'")
        
        logger.info(f"🔄 Cargando CSV legacy: {csv_path}")
        
        # Cargar CSV con formato DomusAI
        df = pd.read_csv(
            csv_path,
            parse_dates=['Datetime'],
            index_col='Datetime'
        )
        
        logger.info(f"✅ Dataset CSV cargado: {len(df):,} registros")
        logger.info(f"📅 Período: {df.index.min()} a {df.index.max()}")
    
    return df


def quick_detect(
    source: str = 'railway',
    csv_path: Optional[str] = None,
    method: str = 'all',
    save: bool = True,
    file_path: Optional[str] = None  # Deprecated
) -> Dict:
    """
    🚨 Función de conveniencia para detección rápida de anomalías.
    
    Soporta Railway MySQL (datos en tiempo real) y CSV legacy.
    
    Args:
        source: Origen de datos - 'railway' (recomendado) | 'csv' (legacy)
        csv_path: Ruta al archivo CSV si source='csv'
        method: Método de detección ('all', 'isolation_forest', 'zscore', etc.)
        save: Guardar resultados automáticamente en data/
        file_path: DEPRECATED - usar csv_path
        
    Returns:
        Dict con resultados completos de detección:
            - anomalies: DataFrame con anomalías detectadas
            - stats: Estadísticas del método usado
            - consensus_anomalies: Anomalías de alto consenso (si method='all')
            - classified_anomalies: Anomalías clasificadas por tipo
            - alerts: Lista de alertas generadas
            
    Example:
        >>> # Railway (RECOMENDADO)
        >>> results = quick_detect(source='railway', method='all')
        >>> print(f"Anomalías detectadas: {len(results['consensus_anomalies'])}")
        >>> 
        >>> # CSV legacy
        >>> results = quick_detect(
        ...     source='csv',
        ...     csv_path='data/Dataset_clean_test.csv',
        ...     method='isolation_forest'
        ... )
    """
    # Backward compatibility
    if file_path is not None:
        import warnings
        warnings.warn(
            "Parámetro 'file_path' deprecated. Usar 'csv_path' y 'source'.",
            DeprecationWarning,
            stacklevel=2
        )
        csv_path = file_path
        source = 'csv'
    
    # Cargar datos
    df = load_data(source=source, csv_path=csv_path)
    
    # Detectar anomalías
    detector = AnomalyDetector(method='isolation_forest')
    results = detector.detect(df, method=method, save=save)
    
    return results


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Ejemplo de uso del AnomalyDetector con Railway MySQL.
    """
    print("=" * 80)
    print("🚨 DomusAI - Detector de Anomalías en Consumo Energético")
    print("=" * 80)
    
    # Auto-detectar data source disponible
    try:
        from src.database import get_db_reader
        db = get_db_reader()
        if db.test_connection():
            print("✅ Railway MySQL disponible - usando datos en tiempo real")
            test_source = 'railway'
            test_csv_path = None
        else:
            raise RuntimeError("Railway no disponible")
    except Exception as e:
        print(f"⚠️ Railway no disponible ({e}) - usando CSV legacy")
        test_source = 'csv'
        test_csv_path = 'data/Dataset_clean_test.csv'
    
    # Opción 1: Detección rápida con función de conveniencia
    print(f"\n📊 Ejecutando detección rápida desde {test_source.upper()}...")
    
    try:
        results = quick_detect(
            source=test_source,
            csv_path=test_csv_path,
            method='all',
            save=True
        )
        
        print(f"\n✅ Detección completada:")
        print(f"   Data source: {test_source.upper()}")
        print(f"   Anomalías de consenso: {len(results['consensus_anomalies']):,}")
        print(f"   Alertas generadas: {len(results.get('alerts', [])):,}")
        
    except Exception as e:
        print(f"\n❌ Error en detección: {e}")
        import traceback
        traceback.print_exc()
    
    # Opción 2: Uso detallado con control fino (comentado - descomentar si necesitas)
    # df = load_data(source=test_source, csv_path=test_csv_path)
    # detector = AnomalyDetector(method='isolation_forest')
    # results = detector.detect(df, method='all', consensus_threshold=3, save=True)
    
    print("\n" + "=" * 80)
    print("🎉 Análisis completado exitosamente")
    print("=" * 80)
