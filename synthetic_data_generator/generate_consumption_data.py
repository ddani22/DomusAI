"""
📊 GENERADOR DE DATOS SINTÉTICOS DE CONSUMO ENERGÉTICO
======================================================

Genera datos sintéticos altamente realistas que imitan patrones de consumo
doméstico real. Incluye estacionalidad diaria/semanal, ruido aleatorio,
y anomalías controladas.

Autor: DomusAI Team
Fecha: 2025-10-29
Versión: 1.0.0

Uso:
    python generate_consumption_data.py --days 30
    python generate_consumption_data.py --days 90 --profile large
    python generate_consumption_data.py --days 30 --upload-railway
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import sys
from typing import Dict, Tuple, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Generador de datos sintéticos de consumo energético"""
    
    # Perfiles de consumo (kW)
    PROFILES = {
        'small': {
            'base_consumption': 0.5,      # Consumo base nocturno
            'morning_peak': 2.5,          # Pico matutino (7-9 AM)
            'evening_peak': 3.0,          # Pico nocturno (18-21 PM)
            'day_consumption': 1.0,       # Consumo diurno
            'noise_std': 0.15,            # Desviación estándar del ruido
        },
        'medium': {
            'base_consumption': 0.6,
            'morning_peak': 3.0,
            'evening_peak': 4.0,
            'day_consumption': 1.5,
            'noise_std': 0.20,
        },
        'large': {
            'base_consumption': 0.8,
            'morning_peak': 4.0,
            'evening_peak': 5.5,
            'day_consumption': 2.0,
            'noise_std': 0.25,
        }
    }
    
    def __init__(
        self,
        days: int = 30,
        start_date: Optional[str] = None,
        profile: str = 'medium',
        frequency: str = '1min',
        anomaly_rate: float = 1.5,
        random_seed: Optional[int] = None
    ):
        """
        Inicializa el generador
        
        Args:
            days: Número de días a generar
            start_date: Fecha de inicio (YYYY-MM-DD). Si None, usa fecha actual - days
            profile: Perfil de consumo ('small', 'medium', 'large')
            frequency: Frecuencia de muestreo ('1min', '30s', etc.)
            anomaly_rate: Porcentaje de anomalías a inyectar (0-100)
            random_seed: Semilla para reproducibilidad
        """
        self.days = days
        self.profile_name = profile
        self.profile = self.PROFILES.get(profile, self.PROFILES['medium'])
        self.frequency = frequency
        self.anomaly_rate = anomaly_rate
        
        # Calcular fecha de inicio
        if start_date:
            self.start_date = pd.to_datetime(start_date)
        else:
            self.start_date = datetime.now() - timedelta(days=days)
        
        # Configurar semilla aleatoria
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Generar períodos de vacaciones aleatorios
        self.vacation_periods = self._generate_vacation_periods()
        
        logger.info(f"🎯 Generador inicializado:")
        logger.info(f"   Perfil: {profile}")
        logger.info(f"   Días: {days}")
        logger.info(f"   Fecha inicio: {self.start_date.strftime('%Y-%m-%d')}")
        logger.info(f"   Frecuencia: {frequency}")
        logger.info(f"   Tasa anomalías: {anomaly_rate}%")
    
    def _generate_vacation_periods(self) -> list:
        """
        Genera períodos de vacaciones aleatorios
        
        Returns:
            Lista de tuplas (fecha_inicio, fecha_fin) para vacaciones
        """
        vacation_periods = []
        
        # Probabilidad de vacaciones según duración del dataset
        if self.days >= 90:
            # Para 90+ días, generar 1-2 períodos de vacaciones
            n_vacations = np.random.randint(1, 3)
        elif self.days >= 30:
            # Para 30-90 días, 30% probabilidad de 1 período
            n_vacations = 1 if np.random.random() < 0.3 else 0
        else:
            # Menos de 30 días, sin vacaciones
            n_vacations = 0
        
        for _ in range(n_vacations):
            # Duración de vacaciones: 7-14 días
            vacation_days = np.random.randint(7, 15)
            
            # Elegir fecha de inicio aleatoria (no muy al principio o final)
            margin = max(5, self.days // 10)
            possible_start = np.random.randint(margin, max(margin + 1, self.days - vacation_days - margin))
            
            vacation_start = self.start_date + timedelta(days=possible_start)
            vacation_end = vacation_start + timedelta(days=vacation_days)
            
            vacation_periods.append((vacation_start, vacation_end))
            logger.info(f"🏖️  Período de vacaciones: {vacation_start.strftime('%Y-%m-%d')} → {vacation_end.strftime('%Y-%m-%d')}")
        
        return vacation_periods
    
    def _is_vacation(self, timestamp: pd.Timestamp) -> bool:
        """Verifica si una fecha está en período de vacaciones"""
        for vacation_start, vacation_end in self.vacation_periods:
            if vacation_start <= timestamp <= vacation_end:
                return True
        return False
    
    def _get_seasonal_factor(self, timestamp: pd.Timestamp) -> Tuple[float, float]:
        """
        Calcula factores estacionales para consumo base y HVAC
        
        Args:
            timestamp: Fecha a evaluar
            
        Returns:
            Tuple: (factor_base, factor_hvac)
                - factor_base: Multiplicador para consumo general (0.9-1.1)
                - factor_hvac: Multiplicador adicional para HVAC (0-1.5)
        """
        # Obtener mes (1-12)
        month = timestamp.month
        
        # Definir estaciones (hemisferio norte)
        # Invierno: Dic, Ene, Feb (12, 1, 2) - Más calefacción
        # Primavera: Mar, Abr, May (3, 4, 5) - Consumo normal
        # Verano: Jun, Jul, Ago (6, 7, 8) - Más aire acondicionado
        # Otoño: Sep, Oct, Nov (9, 10, 11) - Consumo normal
        
        if month in [12, 1, 2]:  # Invierno
            factor_base = 1.1  # +10% consumo base (menos luz natural)
            factor_hvac = 1.3  # +30% calefacción
        elif month in [6, 7, 8]:  # Verano
            factor_base = 0.95  # -5% consumo base (más luz natural)
            factor_hvac = 1.2  # +20% aire acondicionado
        elif month in [3, 4, 5]:  # Primavera
            factor_base = 1.0
            factor_hvac = 0.3  # HVAC mínimo
        else:  # Otoño (9, 10, 11)
            factor_base = 1.05
            factor_hvac = 0.5  # HVAC moderado
        
        return factor_base, factor_hvac
    
    def _generate_timestamps(self) -> pd.DatetimeIndex:
        """Genera secuencia de timestamps"""
        end_date = self.start_date + timedelta(days=self.days)
        timestamps = pd.date_range(
            start=self.start_date,
            end=end_date,
            freq=self.frequency,
            inclusive='left'
        )
        logger.info(f"📅 Timestamps generados: {len(timestamps):,} registros")
        return timestamps
    
    def _get_hourly_pattern(self, hour: int, is_weekend: bool, timestamp: pd.Timestamp) -> float:
        """
        Calcula el factor de consumo según la hora del día
        
        Args:
            hour: Hora del día (0-23)
            is_weekend: True si es fin de semana
            timestamp: Timestamp completo para variabilidad adicional
            
        Returns:
            Factor multiplicador de consumo (0.5-1.5)
        """
        # Variabilidad adicional: algunos fines de semana la gente sale (consumo bajo)
        # otros se quedan en casa (consumo alto)
        weekend_away_probability = 0.25  # 25% de fines de semana fuera
        weekend_home_probability = 0.35  # 35% de fines de semana en casa
        
        # Determinar tipo de fin de semana (usar día del año para consistencia)
        weekend_seed = timestamp.dayofyear % 100
        
        if is_weekend:
            if weekend_seed < 25:  # 25% - Fin de semana FUERA
                # Consumo muy bajo todo el día
                morning_peak_hour = 10  # Se despiertan tarde
                evening_peak_hour = 22  # Vuelven tarde
                morning_component = 0.3 * np.exp(-((hour - morning_peak_hour) ** 2) / (2 * 3 ** 2))
                evening_component = 0.4 * np.exp(-((hour - evening_peak_hour) ** 2) / (2 * 3 ** 2))
                pattern = 0.2 + morning_component + evening_component  # Muy bajo
                
            elif weekend_seed < 60:  # 35% - Fin de semana EN CASA
                # Consumo alto y más distribuido
                morning_peak_hour = 10  # Se despiertan tarde
                afternoon_peak = 14  # Comida/actividades
                evening_peak_hour = 21  # Cena/TV
                
                morning_component = 0.7 * np.exp(-((hour - morning_peak_hour) ** 2) / (2 * 2 ** 2))
                afternoon_component = 0.5 * np.exp(-((hour - afternoon_peak) ** 2) / (2 * 3 ** 2))
                evening_component = 0.9 * np.exp(-((hour - evening_peak_hour) ** 2) / (2 * 3 ** 2))
                pattern = 0.6 + morning_component + afternoon_component + evening_component
                
            else:  # 40% - Fin de semana NORMAL
                # Patrón normal pero desplazado (despertar tarde)
                morning_peak_hour = 10  # Despertar tarde
                evening_peak_hour = 21  # Cena más tarde
                
                morning_component = 0.6 * np.exp(-((hour - morning_peak_hour) ** 2) / (2 * 2.5 ** 2))
                evening_component = 0.8 * np.exp(-((hour - evening_peak_hour) ** 2) / (2 * 3 ** 2))
                pattern = 0.5 + morning_component + evening_component
        
        else:  # DÍAS LABORABLES
            morning_peak_hour = 7  # Despertar temprano
            evening_peak_hour = 20  # Vuelta del trabajo
            
            # Calcular componente sinusoidal para pico matutino
            morning_component = np.exp(-((hour - morning_peak_hour) ** 2) / (2 * 1.5 ** 2))
            
            # Calcular componente sinusoidal para pico nocturno
            evening_component = np.exp(-((hour - evening_peak_hour) ** 2) / (2 * 2.5 ** 2))
            
            # Combinar componentes
            pattern = 0.4 + 0.7 * morning_component + 1.0 * evening_component
        
        # Añadir variabilidad diaria (±10%)
        daily_variation = np.random.uniform(0.9, 1.1)
        pattern *= daily_variation
        
        return max(0.2, pattern)  # Mínimo 0.2
    
    def _generate_base_consumption(self, timestamps: pd.DatetimeIndex) -> np.ndarray:
        """
        Genera patrón de consumo base con estacionalidad
        
        Args:
            timestamps: Índice de fechas
            
        Returns:
            Array con consumos base (kW)
        """
        logger.info("⚡ Generando patrón de consumo base...")
        
        consumption = np.zeros(len(timestamps))
        
        for i, ts in enumerate(timestamps):
            hour = ts.hour
            is_weekend = ts.dayofweek >= 5  # Sábado=5, Domingo=6
            is_vacation = self._is_vacation(ts)
            
            # Obtener factores estacionales
            seasonal_base, seasonal_hvac = self._get_seasonal_factor(ts)
            
            # Factor horario con patrones mejorados
            hourly_factor = self._get_hourly_pattern(hour, is_weekend, ts)
            
            # Consumo base según hora
            if 0 <= hour < 6:  # Noche
                base = self.profile['base_consumption']
            elif 6 <= hour < 9:  # Mañana (pico)
                base = self.profile['morning_peak']
            elif 9 <= hour < 18:  # Día
                base = self.profile['day_consumption']
            else:  # Tarde-noche (pico)
                base = self.profile['evening_peak']
            
            # Aplicar factor horario
            consumption[i] = base * hourly_factor
            
            # Aplicar factor estacional al consumo base
            consumption[i] *= seasonal_base
            
            # Añadir consumo de HVAC según estación
            # El HVAC varía más durante el día (más uso cuando hace más calor/frío)
            if 10 <= hour <= 22:  # HVAC principalmente diurno
                hvac_consumption = self.profile['day_consumption'] * seasonal_hvac * 0.3
            else:
                hvac_consumption = self.profile['base_consumption'] * seasonal_hvac * 0.2
            
            consumption[i] += hvac_consumption
            
            # Si están de vacaciones, reducir consumo drásticamente
            if is_vacation:
                # Solo queda consumo base (nevera, standby, etc.)
                consumption[i] = consumption[i] * 0.15  # 15% del consumo normal
        
        return consumption
    
    def _add_noise(self, consumption: np.ndarray) -> np.ndarray:
        """
        Añade ruido gaussiano realista
        
        Args:
            consumption: Array de consumos base
            
        Returns:
            Array con ruido añadido
        """
        logger.info("🎲 Añadiendo variaciones aleatorias...")
        
        # Ruido gaussiano proporcional al consumo
        noise = np.random.normal(
            0,
            self.profile['noise_std'],
            size=len(consumption)
        )
        
        # Ruido adicional (spikes ocasionales)
        spike_probability = 0.01  # 1% de probabilidad de spike
        spikes = np.random.choice(
            [0, 1],
            size=len(consumption),
            p=[1 - spike_probability, spike_probability]
        )
        spike_magnitude = np.random.uniform(0.3, 1.0, size=len(consumption))
        
        consumption_with_noise = consumption + noise + (spikes * spike_magnitude)
        
        # Asegurar que no haya valores negativos
        consumption_with_noise = np.maximum(consumption_with_noise, 0.1)
        
        return consumption_with_noise
    
    def _inject_anomalies(
        self,
        consumption: np.ndarray,
        timestamps: pd.DatetimeIndex
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Inyecta anomalías controladas
        
        Args:
            consumption: Array de consumos
            timestamps: Índice de fechas
            
        Returns:
            Tuple: (consumos con anomalías, DataFrame con info de anomalías)
        """
        if self.anomaly_rate == 0:
            logger.info("✅ Sin anomalías inyectadas")
            return consumption, pd.DataFrame()
        
        logger.info(f"🚨 Inyectando anomalías ({self.anomaly_rate}%)...")
        
        n_anomalies = int(len(consumption) * (self.anomaly_rate / 100))
        anomaly_indices = np.random.choice(
            len(consumption),
            size=n_anomalies,
            replace=False
        )
        
        anomalies_info = []
        
        for idx in anomaly_indices:
            # Tipos de anomalías
            anomaly_type = np.random.choice(['high', 'medium', 'low'], p=[0.33, 0.33, 0.34])
            
            if anomaly_type == 'high':
                # Consumo excesivo (>5 kW)
                consumption[idx] = np.random.uniform(5.0, 7.0)
                severity = 'HIGH'
            elif anomaly_type == 'medium':
                # Pico inusual
                consumption[idx] = consumption[idx] * np.random.uniform(2.0, 3.0)
                severity = 'MEDIUM'
            else:
                # Variación menor
                consumption[idx] = consumption[idx] * np.random.uniform(1.5, 2.0)
                severity = 'LOW'
            
            anomalies_info.append({
                'timestamp': timestamps[idx],
                'severity': severity,
                'value': consumption[idx]
            })
        
        anomalies_df = pd.DataFrame(anomalies_info)
        logger.info(f"   ✅ {len(anomalies_info):,} anomalías inyectadas")
        
        return consumption, anomalies_df
    
    def _generate_related_variables(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Genera variables relacionadas manteniendo coherencia física
        
        Args:
            df: DataFrame con Global_active_power
            
        Returns:
            DataFrame completo con todas las variables
        """
        logger.info("🔗 Generando variables relacionadas...")
        
        # Voltage (230V ± 10V)
        df['Voltage'] = np.random.normal(235, 5, size=len(df))
        df['Voltage'] = df['Voltage'].clip(220, 245)
        
        # Global_reactive_power (10-20% de active power)
        reactive_factor = np.random.uniform(0.10, 0.20, size=len(df))
        df['Global_reactive_power'] = df['Global_active_power'] * reactive_factor
        
        # Global_intensity (Ley de Ohm: I = P / V × 1000)
        df['Global_intensity'] = (df['Global_active_power'] / df['Voltage']) * 1000
        
        # Sub-metering (proporciones del consumo total en kW)
        # Sub_metering_1: Cocina (0-40% del total)
        # Sub_metering_2: Lavandería (0-30% del total)
        # Sub_metering_3: Agua/Clima (0-30% del total)
        
        total_power_kw = df['Global_active_power']  # Ya está en kW
        
        # Distribución aleatoria pero coherente
        sub1_ratio = np.random.uniform(0.0, 0.4, size=len(df))
        sub2_ratio = np.random.uniform(0.0, 0.3, size=len(df))
        sub3_ratio = np.random.uniform(0.0, 0.3, size=len(df))
        
        # Normalizar para que no excedan el total
        total_ratio = sub1_ratio + sub2_ratio + sub3_ratio
        factor = np.where(total_ratio > 1.0, 1.0 / total_ratio, 1.0)
        
        df['Sub_metering_1'] = (total_power_kw * sub1_ratio * factor).round(3)
        df['Sub_metering_2'] = (total_power_kw * sub2_ratio * factor).round(3)
        df['Sub_metering_3'] = (total_power_kw * sub3_ratio * factor).round(3)
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        Valida la coherencia de los datos generados
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Dict con resultados de validaciones
        """
        logger.info("🔍 Validando datos generados...")
        
        validations = {}
        
        # 1. No valores NaN
        validations['no_nan'] = not df.isnull().any().any()
        
        # 2. No timestamps duplicados
        validations['no_duplicates'] = not df.index.duplicated().any()
        
        # 3. Voltage en rango
        validations['voltage_range'] = (
            (df['Voltage'] >= 220) & (df['Voltage'] <= 245)
        ).all()
        
        # 4. Potencia no negativa
        validations['power_positive'] = (df['Global_active_power'] >= 0).all()
        
        # 5. Sub-metering coherente (ahora en kW)
        total_submetering = (
            df['Sub_metering_1'] +
            df['Sub_metering_2'] +
            df['Sub_metering_3']
        )
        total_power_kw = df['Global_active_power']
        validations['submetering_coherent'] = (
            total_submetering <= total_power_kw * 1.01  # Tolerancia 1%
        ).all()
        
        # 6. Ley de Ohm (I = P/V × 1000)
        calculated_intensity = (df['Global_active_power'] / df['Voltage']) * 1000
        intensity_error = np.abs(df['Global_intensity'] - calculated_intensity).mean()
        validations['ohms_law'] = intensity_error < 0.1
        
        # Mostrar resultados
        all_passed = all(validations.values())
        if all_passed:
            logger.info("   ✅ Todas las validaciones pasadas")
        else:
            logger.warning("   ⚠️  Algunas validaciones fallaron:")
            for check, passed in validations.items():
                if not passed:
                    logger.warning(f"      ❌ {check}")
        
        return validations
    
    def generate(self) -> pd.DataFrame:
        """
        Genera el dataset completo
        
        Returns:
            DataFrame con todas las columnas
        """
        print("\n" + "=" * 70)
        print("📊 GENERADOR DE DATOS SINTÉTICOS - DomusAI")
        print("=" * 70)
        
        # 1. Generar timestamps
        timestamps = self._generate_timestamps()
        
        # 2. Generar consumo base
        consumption = self._generate_base_consumption(timestamps)
        
        # 3. Añadir ruido
        consumption = self._add_noise(consumption)
        
        # 4. Inyectar anomalías
        consumption, anomalies_df = self._inject_anomalies(consumption, timestamps)
        
        # 5. Crear DataFrame
        df = pd.DataFrame({
            'Datetime': timestamps,
            'Global_active_power': consumption
        })
        df.set_index('Datetime', inplace=True)
        
        # 6. Generar variables relacionadas
        df = self._generate_related_variables(df)
        
        # 7. Reordenar columnas (igual que Dataset_clean_test.csv)
        df = df[[
            'Global_active_power',
            'Global_reactive_power',
            'Voltage',
            'Global_intensity',
            'Sub_metering_1',
            'Sub_metering_2',
            'Sub_metering_3'
        ]]
        
        # 8. Redondear valores
        df = df.round(3)
        
        # 9. Validar
        validations = self._validate_data(df)
        
        # 10. Mostrar estadísticas
        self._print_statistics(df, anomalies_df, validations)
        
        return df
    
    def _print_statistics(
        self,
        df: pd.DataFrame,
        anomalies_df: pd.DataFrame,
        validations: Dict[str, bool]
    ):
        """Imprime estadísticas del dataset generado"""
        print("\n" + "=" * 70)
        print("✅ GENERACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        
        print(f"\n📊 Estadísticas del Dataset:")
        print(f"   Total registros:       {len(df):,}")
        print(f"   Rango de fechas:       {df.index.min().strftime('%Y-%m-%d %H:%M:%S')} → {df.index.max().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Días generados:        {self.days}")
        print(f"   Frecuencia:            {self.frequency}")
        
        print(f"\n📈 Consumo Energético:")
        print(f"   Consumo promedio:      {df['Global_active_power'].mean():.3f} kW")
        print(f"   Consumo mínimo:        {df['Global_active_power'].min():.3f} kW")
        print(f"   Consumo máximo:        {df['Global_active_power'].max():.3f} kW")
        print(f"   Desviación estándar:   {df['Global_active_power'].std():.3f} kW")
        
        print(f"\n⚡ Voltaje:")
        print(f"   Promedio:              {df['Voltage'].mean():.1f} V")
        print(f"   Rango:                 [{df['Voltage'].min():.1f}, {df['Voltage'].max():.1f}] V")
        
        if len(anomalies_df) > 0:
            print(f"\n🔍 Anomalías Inyectadas:")
            print(f"   Total:                 {len(anomalies_df):,} registros ({self.anomaly_rate}%)")
            severity_counts = anomalies_df['severity'].value_counts()
            for severity, count in severity_counts.items():
                pct = (count / len(anomalies_df)) * 100
                print(f"   {severity}:                  {count} ({pct:.1f}%)")
        
        print(f"\n✅ Validaciones:")
        for check, passed in validations.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check.replace('_', ' ').title()}")
        
        print("=" * 70 + "\n")
    
    def save(self, df: pd.DataFrame, output_dir: str = 'output') -> str:
        """
        Guarda el dataset en CSV
        
        Args:
            df: DataFrame a guardar
            output_dir: Directorio de salida
            
        Returns:
            Ruta del archivo guardado
        """
        # Crear directorio si no existe
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"synthetic_{self.days}days_{timestamp}.csv"
        filepath = Path(output_dir) / filename
        
        # Guardar
        logger.info(f"💾 Guardando archivo: {filepath}")
        df.to_csv(filepath)
        
        print(f"💾 Archivo guardado: {filepath}")
        print(f"   Tamaño: {filepath.stat().st_size / 1024:.1f} KB")
        
        return str(filepath)


def main():
    """Función principal CLI"""
    parser = argparse.ArgumentParser(
        description='📊 Generador de Datos Sintéticos de Consumo Energético',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Generar 30 días (hogar mediano)
  python generate_consumption_data.py --days 30
  
  # Generar 90 días (hogar grande) desde fecha específica
  python generate_consumption_data.py --days 90 --profile large --start-date 2025-10-01
  
  # Generar con muchas anomalías para testing
  python generate_consumption_data.py --days 30 --anomalies 5.0
  
  # Generar sin anomalías (datos limpios)
  python generate_consumption_data.py --days 30 --anomalies 0.0
        """
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Número de días a generar (default: 30)'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        help='Fecha de inicio YYYY-MM-DD (default: hoy - N días)'
    )
    parser.add_argument(
        '--profile',
        type=str,
        choices=['small', 'medium', 'large'],
        default='medium',
        help='Perfil de consumo (default: medium)'
    )
    parser.add_argument(
        '--frequency',
        type=str,
        default='1min',
        help='Frecuencia de muestreo (default: 1min)'
    )
    parser.add_argument(
        '--anomalies',
        type=float,
        default=1.5,
        help='Porcentaje de anomalías (0-100, default: 1.5)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='Directorio de salida (default: output/)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Semilla aleatoria para reproducibilidad'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Solo validar, no guardar'
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if args.days < 1:
        logger.error("❌ Error: --days debe ser >= 1")
        sys.exit(1)
    
    if not (0 <= args.anomalies <= 100):
        logger.error("❌ Error: --anomalies debe estar entre 0 y 100")
        sys.exit(1)
    
    # Crear generador
    generator = SyntheticDataGenerator(
        days=args.days,
        start_date=args.start_date,
        profile=args.profile,
        frequency=args.frequency,
        anomaly_rate=args.anomalies,
        random_seed=args.seed
    )
    
    # Generar datos
    df = generator.generate()
    
    # Guardar (si no es solo validación)
    if not args.validate:
        filepath = generator.save(df, output_dir=args.output)
        print(f"\n✅ ¡Listo! Puedes usar el archivo generado:")
        print(f"   {filepath}")
    else:
        print("\n✅ Validación completada (no se guardó el archivo)")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
