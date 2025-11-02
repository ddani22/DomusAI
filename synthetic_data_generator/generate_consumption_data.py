"""
📊 GENERADOR DE DATOS SINTÉTICOS DE CONSUMO ENERGÉTICO - ESPAÑA
================================================================

Genera datos sintéticos ultra-realistas para un hogar español, incluyendo:
- Patrones diarios/semanales específicos de España
- Estacionalidad (calefacción invierno, AC verano)
- Vacaciones españolas (Agosto, Navidad, Semana Santa, puentes)
- Sub-medidores coherentes (Cocina, Lavandería, Clima/Agua)
- Relaciones físicas correctas (Ley de Ohm, Factor de Potencia)

Autor: DomusAI Team
Fecha: 2025-11-01
Versión: 2.0.0 - Optimizado para España

Uso:
    python generate_consumption_data.py --days 1460  # 4 años
    python generate_consumption_data.py --days 365 --profile large
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
    """Generador de datos sintéticos de consumo energético para España"""
    
    # Perfiles de consumo (kW) - AJUSTADOS PARA DATOS REALES ESPAÑA
    # Basados en IDAE: Consumo promedio 3,500 kWh/año = 0.40-0.52 kW promedio continuo
    PROFILES = {
        'small': {
            # Piso pequeño (1-2 personas): 2,500-3,000 kWh/año → 0.28-0.34 kW promedio
            'base_consumption': 0.12,     # Consumo base nocturno (nevera, standby)
            'morning_peak': 0.9,          # Pico matutino (7-9 AM)
            'evening_peak': 1.1,          # Pico nocturno (19-22 PM)
            'day_consumption': 0.20,      # Consumo diurno (casa vacía)
            'noise_std': 0.04,            # Desviación estándar del ruido
        },
        'medium': {
            # Vivienda mediana (3-4 personas): 3,500-4,500 kWh/año → 0.40-0.52 kW promedio
            'base_consumption': 0.15,     # Consumo base nocturno
            'morning_peak': 1.2,          # Pico matutino
            'evening_peak': 1.5,          # Pico nocturno
            'day_consumption': 0.28,      # Consumo diurno (teletrabajo ligero)
            'noise_std': 0.05,            # Desviación estándar del ruido
        },
        'large': {
            # Casa grande (5+ personas): 5,000-7,000 kWh/año → 0.57-0.80 kW promedio
            'base_consumption': 0.22,     # Consumo base nocturno
            'morning_peak': 1.8,          # Pico matutino
            'evening_peak': 2.2,          # Pico nocturno
            'day_consumption': 0.45,      # Consumo diurno
            'noise_std': 0.08,            # Desviación estándar del ruido
        }
    }
    
    # Festivos españoles fijos (mes, día)
    SPANISH_HOLIDAYS = [
        (1, 1),   # Año Nuevo
        (1, 6),   # Reyes
        (5, 1),   # Día del Trabajo
        (8, 15),  # Asunción
        (10, 12), # Día de la Hispanidad
        (11, 1),  # Todos los Santos
        (12, 6),  # Constitución
        (12, 8),  # Inmaculada
        (12, 25), # Navidad
    ]
    
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
        
        # Generar períodos de vacaciones y eventos especiales españoles
        self.vacation_periods = self._generate_spanish_vacation_periods()
        self.bridge_weekends = self._generate_bridge_weekends()
        
        # Generar variabilidad mensual aleatoria
        self.monthly_variation = self._generate_monthly_variation()
        
        logger.info(f"🎯 Generador inicializado:")
        logger.info(f"   Perfil: {profile}")
        logger.info(f"   Días: {days}")
        logger.info(f"   Fecha inicio: {self.start_date.strftime('%Y-%m-%d')}")
        logger.info(f"   Frecuencia: {frequency}")
        logger.info(f"   Tasa anomalías: {anomaly_rate}%")
    
    def _generate_spanish_vacation_periods(self) -> list:
        """
        Genera períodos de vacaciones típicos españoles
        
        Returns:
            Lista de tuplas (fecha_inicio, fecha_fin, tipo, probabilidad_fuera)
        """
        vacation_periods = []
        
        # Calcular cuántos años completos abarca el dataset
        end_date = self.start_date + timedelta(days=self.days)
        years = list(range(self.start_date.year, end_date.year + 1))
        
        for year in years:
            # 1. AGOSTO - Vacaciones de verano (2-3 semanas, siempre fuera)
            august_start = max(self.start_date, datetime(year, 8, 1))
            august_duration = np.random.randint(14, 22)  # 2-3 semanas
            august_end = august_start + timedelta(days=august_duration)
            
            if august_end <= end_date:
                vacation_periods.append((august_start, august_end, 'AGOSTO', 1.0))
                logger.info(f"🏖️  Vacaciones de Agosto {year}: {august_start.strftime('%Y-%m-%d')} → {august_end.strftime('%Y-%m-%d')}")
            
            # 2. NAVIDAD (23 Dic - 7 Ene, 50% probabilidad fuera/casa)
            christmas_start = max(self.start_date, datetime(year, 12, 23))
            christmas_end = min(end_date, datetime(year + 1, 1, 7))
            
            if christmas_start < end_date and christmas_end > self.start_date:
                away_probability = 0.5  # 50% fuera, 50% en casa con familia
                vacation_periods.append((christmas_start, christmas_end, 'NAVIDAD', away_probability))
                logger.info(f"🎄 Vacaciones de Navidad {year}: {christmas_start.strftime('%Y-%m-%d')} → {christmas_end.strftime('%Y-%m-%d')}")
            
            # 3. SEMANA SANTA (varía cada año, aproximadamente finales marzo/abril)
            # Simplificación: 2ª semana de abril
            easter_start = max(self.start_date, datetime(year, 4, 8))
            easter_end = min(end_date, datetime(year, 4, 15))
            
            if easter_start < end_date and easter_end > self.start_date:
                away_probability = 0.5  # 50% fuera, 50% en casa
                vacation_periods.append((easter_start, easter_end, 'SEMANA_SANTA', away_probability))
                logger.info(f"🐣 Semana Santa {year}: {easter_start.strftime('%Y-%m-%d')} → {easter_end.strftime('%Y-%m-%d')}")
        
        return vacation_periods
    
    def _generate_bridge_weekends(self) -> list:
        """
        Genera fines de semana "puente" españoles
        
        Returns:
            Lista de tuplas (fecha_inicio, fecha_fin) para puentes
        """
        bridge_weekends = []
        end_date = self.start_date + timedelta(days=self.days)
        years = list(range(self.start_date.year, end_date.year + 1))
        
        # Festivos que suelen generar puentes
        bridge_holidays = [
            (5, 1),   # 1 de Mayo
            (10, 12), # 12 de Octubre
            (11, 1),  # 1 de Noviembre
            (12, 6),  # Constitución
            (12, 8),  # Inmaculada
        ]
        
        for year in years:
            for month, day in bridge_holidays:
                holiday_date = datetime(year, month, day)
                
                # Si el festivo cae en martes o jueves, hay puente
                if holiday_date.weekday() in [1, 3]:  # Martes=1, Jueves=3
                    if holiday_date.weekday() == 1:  # Martes -> puente desde viernes
                        bridge_start = holiday_date - timedelta(days=4)  # Viernes anterior
                    else:  # Jueves -> puente hasta lunes
                        bridge_start = holiday_date - timedelta(days=2)  # Miércoles (algunos salen)
                    
                    bridge_end = holiday_date + timedelta(days=3)  # Hasta domingo
                    
                    if bridge_start >= self.start_date and bridge_end <= end_date:
                        bridge_weekends.append((bridge_start, bridge_end))
                        logger.info(f"� Puente festivo: {bridge_start.strftime('%Y-%m-%d')} → {bridge_end.strftime('%Y-%m-%d')}")
        
        return bridge_weekends
    
    def _generate_monthly_variation(self) -> Dict[int, float]:
        """
        Genera variación aleatoria mensual del consumo
        
        Returns:
            Dict con factores multiplicadores por mes (1-12)
        """
        monthly_factors = {}
        
        # Generar factores aleatorios entre 0.85 y 1.15 (±15% variación)
        for month in range(1, 13):
            # Algunos meses con más variación que otros
            if month in [7, 8]:  # Verano - puede variar más por vacaciones
                factor = np.random.uniform(0.80, 1.10)
            elif month in [12, 1]:  # Invierno - puede variar por fiestas
                factor = np.random.uniform(0.90, 1.20)
            else:
                factor = np.random.uniform(0.90, 1.10)
            
            monthly_factors[month] = factor
            logger.info(f"📅 Variación mes {month}: {factor:.2f}x")
        
        return monthly_factors
    
    def _is_vacation(self, timestamp: pd.Timestamp) -> Tuple[bool, str, float]:
        """Verifica si una fecha está en período de vacaciones"""
        for vacation_start, vacation_end, vacation_type, away_prob in self.vacation_periods:
            if vacation_start <= timestamp <= vacation_end:
                return True, vacation_type, away_prob
        return False, '', 0.0
    
    def _is_bridge_weekend(self, timestamp: pd.Timestamp) -> bool:
        """Verifica si una fecha está en un puente festivo"""
        for bridge_start, bridge_end in self.bridge_weekends:
            if bridge_start <= timestamp <= bridge_end:
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
            factor_base = 1.05  # +5% consumo base (menos luz natural)
            factor_hvac = 1.0   # Calefacción moderada
        elif month in [6, 7, 8]:  # Verano
            factor_base = 0.98  # -2% consumo base (más luz natural)
            factor_hvac = 0.9   # Aire acondicionado moderado
        elif month in [3, 4, 5]:  # Primavera
            factor_base = 1.0
            factor_hvac = 0.2  # HVAC mínimo
        else:  # Otoño (9, 10, 11)
            factor_base = 1.02
            factor_hvac = 0.3  # HVAC moderado
        
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
        Calcula el factor de consumo según la hora del día (Patrón español)
        
        Args:
            hour: Hora del día (0-23)
            is_weekend: True si es fin de semana
            timestamp: Timestamp completo para variabilidad adicional
            
        Returns:
            Factor multiplicador de consumo
        """
        # Determinar tipo de fin de semana (usar día del año para consistencia)
        weekend_seed = timestamp.dayofyear % 100
        
        if is_weekend:
            if weekend_seed < 25:  # 25% - Fin de semana FUERA
                # Consumo muy bajo todo el día
                morning_peak_hour = 11  # Se despiertan muy tarde
                evening_peak_hour = 23  # Vuelven tarde de cenar fuera
                morning_component = 0.1 * np.exp(-((hour - morning_peak_hour) ** 2) / (2 * 3 ** 2))
                evening_component = 0.15 * np.exp(-((hour - evening_peak_hour) ** 2) / (2 * 3 ** 2))
                pattern = 0.10 + morning_component + evening_component
                
            elif weekend_seed < 60:  # 35% - Fin de semana EN CASA
                # Consumo alto y más distribuido (horario español)
                morning_peak_hour = 10  # Desayuno tardío
                lunch_peak = 14  # Comida (hora española)
                evening_peak_hour = 21  # Cena (hora española)
                
                morning_component = 0.35 * np.exp(-((hour - morning_peak_hour) ** 2) / (2 * 2 ** 2))
                lunch_component = 0.45 * np.exp(-((hour - lunch_peak) ** 2) / (2 * 2 ** 2))
                evening_component = 0.50 * np.exp(-((hour - evening_peak_hour) ** 2) / (2 * 2.5 ** 2))
                pattern = 0.30 + morning_component + lunch_component + evening_component
                
            else:  # 40% - Fin de semana NORMAL
                # Patrón normal pero con horarios españoles
                morning_peak_hour = 10  # Despertar tarde
                lunch_peak = 15  # Comida tardía
                evening_peak_hour = 22  # Cena tardía
                
                morning_component = 0.30 * np.exp(-((hour - morning_peak_hour) ** 2) / (2 * 2 ** 2))
                lunch_component = 0.35 * np.exp(-((hour - lunch_peak) ** 2) / (2 * 2 ** 2))
                evening_component = 0.40 * np.exp(-((hour - evening_peak_hour) ** 2) / (2 * 2.5 ** 2))
                pattern = 0.25 + morning_component + lunch_component + evening_component
        
        else:  # DÍAS LABORABLES (horario español)
            # Noche (00:00-06:00): Consumo base muy bajo
            if 0 <= hour < 6:
                pattern = 0.12  # Muy bajo (solo nevera y standby)
            # Mañana (06:00-09:00): Pico moderado (duchas, desayuno)
            elif 6 <= hour < 9:
                morning_peak_hour = 7.5
                pattern = 0.55 * np.exp(-((hour - morning_peak_hour) ** 2) / (2 * 1 ** 2)) + 0.15
            # Día (09:00-17:00): Consumo bajo (casa vacía)
            elif 9 <= hour < 17:
                # Pequeño pico a mediodía (algunos vuelven a comer)
                lunch_component = 0.15 * np.exp(-((hour - 14) ** 2) / (2 * 1.5 ** 2))
                pattern = 0.12 + lunch_component  # Muy bajo, casa vacía
            # Tarde/Noche (17:00-23:00): Pico principal (cocina, luces, TV)
            else:
                # Pico principal entre 19:00-22:00 (hora española de cena)
                evening_peak_hour = 20.5
                pattern = 0.65 * np.exp(-((hour - evening_peak_hour) ** 2) / (2 * 2 ** 2)) + 0.22
        
        # Añadir variabilidad diaria (±10%)
        daily_variation = np.random.uniform(0.9, 1.1)
        pattern *= daily_variation
        
        return max(0.1, pattern)
    
    def _generate_base_consumption(self, timestamps: pd.DatetimeIndex) -> np.ndarray:
        """
        Genera patrón de consumo base con estacionalidad española
        
        Args:
            timestamps: Índice de fechas
            
        Returns:
            Array con consumos base (kW)
        """
        logger.info("⚡ Generando patrón de consumo base...")
        
        consumption = np.zeros(len(timestamps))
        
        for i, ts in enumerate(timestamps):
            hour = ts.hour
            month = ts.month
            is_weekend = ts.dayofweek >= 5  # Sábado=5, Domingo=6
            is_vacation, vacation_type, away_prob = self._is_vacation(ts)
            is_bridge = self._is_bridge_weekend(ts)
            
            # Obtener factores estacionales
            seasonal_base, seasonal_hvac = self._get_seasonal_factor(ts)
            
            # Obtener variación mensual aleatoria
            monthly_factor = self.monthly_variation.get(month, 1.0)
            
            # Factor horario con patrones españoles
            hourly_factor = self._get_hourly_pattern(hour, is_weekend, ts)
            
            # Consumo base según hora
            if 0 <= hour < 6:  # Noche
                base = self.profile['base_consumption']
            elif 6 <= hour < 9:  # Mañana (pico)
                base = self.profile['morning_peak']
            elif 9 <= hour < 17:  # Día
                base = self.profile['day_consumption']
            else:  # Tarde-noche (pico ALTO en España)
                base = self.profile['evening_peak']
            
            # Aplicar factor horario
            consumption[i] = base * hourly_factor
            
            # Aplicar factor estacional al consumo base
            consumption[i] *= seasonal_base
            
            # Aplicar variación mensual aleatoria
            consumption[i] *= monthly_factor
            
            # Añadir consumo de HVAC según estación (reducido para promedios realistas)
            # El HVAC varía más durante el día
            if 10 <= hour <= 22:  # HVAC principalmente diurno
                hvac_consumption = self.profile['day_consumption'] * seasonal_hvac * 0.15
            else:
                hvac_consumption = self.profile['base_consumption'] * seasonal_hvac * 0.10
            
            consumption[i] += hvac_consumption
            
            # Gestionar vacaciones y puentes
            if is_vacation:
                # Decidir si están fuera basado en probabilidad
                if np.random.random() < away_prob:
                    # FUERA: Solo queda consumo base (nevera, standby)
                    consumption[i] = consumption[i] * 0.15  # 15% del consumo normal
                else:
                    # EN CASA: Aumentar consumo (familia, invitados, más cocina)
                    if vacation_type in ['NAVIDAD', 'SEMANA_SANTA']:
                        consumption[i] = consumption[i] * 1.25  # +25% por invitados/actividades
            
            elif is_bridge:
                # Puentes: 70% de probabilidad de estar fuera
                if np.random.random() < 0.7:
                    consumption[i] = consumption[i] * 0.15  # Fuera de casa
        
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
        Genera variables relacionadas manteniendo coherencia física (España)
        
        Args:
            df: DataFrame con Global_active_power e índice de timestamps
            
        Returns:
            DataFrame completo con todas las variables
        """
        logger.info("🔗 Generando variables relacionadas y sub-medidores...")
        
        # 1. VOLTAJE (230V ± 8V con ruido gaussiano)
        df['Voltage'] = np.random.normal(230, 2.5, size=len(df))
        df['Voltage'] = df['Voltage'].clip(225, 238)
        
        # 2. SUB-MEDIDORES (patrones españoles realistas)
        sub1_values = []  # Cocina
        sub2_values = []  # Lavandería
        sub3_values = []  # Clima/Agua
        
        for idx in range(len(df)):
            ts = df.index[idx]
            hour = ts.hour
            is_weekend = ts.dayofweek >= 5
            month = ts.month
            total_power = df.iloc[idx]['Global_active_power']
            
            # SUB_METERING_1: COCINA
            # Picos en desayuno (8h), comida (14h), cena (21h) - horarios españoles
            breakfast_peak = 0.6 * np.exp(-((hour - 8) ** 2) / (2 * 1 ** 2))
            lunch_peak = 0.8 * np.exp(-((hour - 14) ** 2) / (2 * 1.5 ** 2))
            dinner_peak = 0.85 * np.exp(-((hour - 21) ** 2) / (2 * 1.5 ** 2))
            
            kitchen_factor = breakfast_peak + lunch_peak + dinner_peak
            kitchen_base = 0.03  # Nevera siempre encendida (reducido)
            sub1 = (total_power * 0.20 * kitchen_factor + kitchen_base) * np.random.uniform(0.8, 1.2)
            
            # SUB_METERING_2: LAVANDERÍA
            # Picos esporádicos, más frecuentes en fines de semana (sábado mañana)
            if is_weekend and ts.dayofweek == 5:  # Sábado
                if 10 <= hour <= 13:  # Sábado mañana
                    laundry_prob = 0.3
                else:
                    laundry_prob = 0.05
            else:
                laundry_prob = 0.08
            
            if np.random.random() < laundry_prob:
                sub2 = total_power * 0.20 * np.random.uniform(0.8, 1.5)
            else:
                sub2 = 0.02  # Consumo residual
            
            # SUB_METERING_3: CLIMA/AGUA
            # Componente estacional fuerte + duchas matutinas
            seasonal_base, seasonal_hvac = self._get_seasonal_factor(ts)
            
            # Duchas matutinas (7-9h) y nocturnas (22-23h)
            shower_morning = 0.5 * np.exp(-((hour - 8) ** 2) / (2 * 1 ** 2))
            shower_evening = 0.3 * np.exp(-((hour - 22) ** 2) / (2 * 1 ** 2))
            shower_factor = shower_morning + shower_evening
            
            # HVAC según estación (reducido para promedios realistas)
            if month in [6, 7, 8]:  # Verano - AC
                if 14 <= hour <= 18:  # Pico de calor
                    hvac_factor = 0.8
                elif 10 <= hour <= 22:
                    hvac_factor = 0.5
                else:
                    hvac_factor = 0.1
            elif month in [12, 1, 2]:  # Invierno - Calefacción
                if 6 <= hour <= 23:  # Calefacción todo el día
                    hvac_factor = 0.6
                else:
                    hvac_factor = 0.2
            else:  # Primavera/Otoño
                hvac_factor = 0.1
            
            sub3 = (total_power * 0.18 * hvac_factor * seasonal_hvac + 
                    total_power * 0.12 * shower_factor) * np.random.uniform(0.8, 1.2)
            
            # Limitar sub-medidores para que no excedan el total
            sub_total = sub1 + sub2 + sub3
            if sub_total > total_power * 0.75:  # Máximo 75% medido
                factor = (total_power * 0.75) / sub_total
                sub1 *= factor
                sub2 *= factor
                sub3 *= factor
            
            sub1_values.append(max(0, sub1))
            sub2_values.append(max(0, sub2))
            sub3_values.append(max(0, sub3))
        
        df['Sub_metering_1'] = np.array(sub1_values).round(3)
        df['Sub_metering_2'] = np.array(sub2_values).round(3)
        df['Sub_metering_3'] = np.array(sub3_values).round(3)
        
        # 3. POTENCIA REACTIVA (factor de potencia 0.85-0.95)
        # Simulando inductancia de motores/transformadores
        power_factor = np.random.uniform(0.85, 0.95, size=len(df))
        # tan(φ) = Q/P, donde cos(φ) = PF
        tan_phi = np.tan(np.arccos(power_factor))
        df['Global_reactive_power'] = (df['Global_active_power'] * tan_phi * 
                                       np.random.uniform(0.9, 1.1, size=len(df)))
        
        # 4. INTENSIDAD (Ley de Ohm con factor de potencia)
        # P = V × I × cos(φ) → I = P / (V × cos(φ))
        # Simplificado: I (A) = (P_kW × 1000) / (V × 0.9)
        noise_intensity = np.random.normal(0, 0.05, size=len(df))
        df['Global_intensity'] = ((df['Global_active_power'] * 1000) / 
                                  (df['Voltage'] * 0.9)) + noise_intensity
        df['Global_intensity'] = df['Global_intensity'].clip(0)
        
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
