"""
database.py
===========
Módulo para gestionar conexiones READ-ONLY a Railway MySQL.

PROPÓSITO:
  - Leer datos de energy_readings desde Railway MySQL
  - Retornar DataFrames en formato DomusAI (compatibles con ML pipeline)
  - Connection pooling para rendimiento óptimo
  - Health checks y manejo de errores robusto

FUNCIONES PRINCIPALES:
  - get_recent_readings(hours=24) → DataFrame con últimas N horas
  - get_all_data() → DataFrame completo (para entrenamiento ML)
  - get_latest_reading() → Dict con última lectura
  - get_data_by_date_range(start, end) → DataFrame por rango de fechas
  - test_connection() → bool para health check
  - get_statistics() → Dict con estadísticas básicas

ARQUITECTURA SPRINT 8:
  - Este módulo es READ-ONLY (solo SELECT)
  - Tu compañero hace INSERT directo desde ESP32
  - Tú usas estas funciones para entrenar modelos ML y detectar anomalías
  
VERSIÓN: 1.0
FECHA: 2025-10-19
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pandas as pd
import mysql.connector
from mysql.connector import Error, pooling
import logging

# Configurar ruta del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DB_CONFIG
from src.exceptions import DatabaseConnectionError, DatabaseQueryError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RailwayDatabaseReader:
    """
    Manager para lectura READ-ONLY de datos de Railway MySQL.
    
    Características:
    - Connection pooling para rendimiento
    - Retorna DataFrames compatibles con pipeline ML de DomusAI
    - Manejo robusto de errores
    - Health checks automáticos
    """
    
    def __init__(self):
        """Inicializar connection pool"""
        self.pool: Optional[pooling.MySQLConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Crear connection pool para conexiones reutilizables"""
        
        try:
            logger.info("🔌 Inicializando connection pool de Railway MySQL...")
            
            self.pool = pooling.MySQLConnectionPool(
                pool_name="railway_readonly_pool",
                pool_size=DB_CONFIG.POOL_SIZE,
                pool_reset_session=True,
                **DB_CONFIG.connection_params
            )
            
            logger.info(f"✅ Connection pool creado (size={DB_CONFIG.POOL_SIZE})")
            
        except Error as e:
            error_msg = f"Error creando connection pool: {e}"
            logger.error(f"❌ {error_msg}")
            raise DatabaseConnectionError(error_msg)
    
    def _get_connection(self):
        """Obtener conexión del pool"""
        
        if self.pool is None:
            raise DatabaseConnectionError("Connection pool no inicializado")
        
        try:
            return self.pool.get_connection()
        except Error as e:
            raise DatabaseConnectionError(f"Error obteniendo conexión del pool: {e}")
    
    def test_connection(self) -> bool:
        """
        Test de conexión a Railway MySQL.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
            
        Example:
            >>> db = RailwayDatabaseReader()
            >>> if db.test_connection():
            ...     print("Conexión OK")
        """
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            logger.info("✅ Test de conexión exitoso")
            return result is not None and result[0] == 1
            
        except (DatabaseConnectionError, Error) as e:
            logger.error(f"❌ Test de conexión fallido: {e}")
            return False
    
    def get_latest_reading(self) -> Optional[Dict[str, Any]]:
        """
        Obtener la última lectura de energy_readings.
        
        Returns:
            Dict con los campos de la última lectura, o None si no hay datos
            
        Example:
            >>> db = RailwayDatabaseReader()
            >>> latest = db.get_latest_reading()
            >>> print(f"Potencia: {latest['Global_active_power']} kW")
        """
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    id, Datetime, Global_active_power, Global_reactive_power,
                    Voltage, Global_intensity, Sub_metering_1, Sub_metering_2,
                    Sub_metering_3, created_at
                FROM energy_readings
                ORDER BY created_at DESC
                LIMIT 1
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result:
                logger.info(f"✅ Última lectura: {result['Datetime']} - {result['Global_active_power']} kW")
            else:
                logger.warning("⚠️ No se encontraron lecturas en la base de datos")
            
            return result
            
        except Error as e:
            error_msg = f"Error obteniendo última lectura: {e}"
            logger.error(f"❌ {error_msg}")
            raise DatabaseQueryError(error_msg)
    
    def get_recent_readings(self, hours: int = 24) -> pd.DataFrame:
        """
        Obtener lecturas de las últimas N horas.
        
        Args:
            hours: Número de horas hacia atrás (default: 24)
            
        Returns:
            DataFrame con las lecturas en formato DomusAI
            
        Example:
            >>> db = RailwayDatabaseReader()
            >>> df = db.get_recent_readings(hours=24)
            >>> print(f"Lecturas últimas 24h: {len(df)}")
        """
        
        try:
            connection = self._get_connection()
            
            # Calcular timestamp límite
            limit_datetime = datetime.now() - timedelta(hours=hours)
            
            query = """
                SELECT 
                    Datetime, Global_active_power, Global_reactive_power,
                    Voltage, Global_intensity, Sub_metering_1, Sub_metering_2,
                    Sub_metering_3
                FROM energy_readings
                WHERE Datetime >= %s
                ORDER BY Datetime ASC
            """
            
            # Usar pandas para leer directamente a DataFrame
            df = pd.read_sql(
                query,
                connection,
                params=(limit_datetime,),
                parse_dates=['Datetime']
            )
            
            connection.close()
            
            # Configurar Datetime como índice (formato DomusAI)
            if not df.empty:
                df.set_index('Datetime', inplace=True)
            
            logger.info(f"✅ Lecturas obtenidas: {len(df)} registros (últimas {hours}h)")
            
            return df
            
        except Error as e:
            error_msg = f"Error obteniendo lecturas recientes: {e}"
            logger.error(f"❌ {error_msg}")
            raise DatabaseQueryError(error_msg)
    
    def get_all_data(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Obtener TODOS los datos de energy_readings (para entrenamiento ML).
        
        Args:
            limit: Máximo número de registros (None = todos)
            
        Returns:
            DataFrame completo en formato DomusAI
            
        Example:
            >>> db = RailwayDatabaseReader()
            >>> df = db.get_all_data()
            >>> print(f"Total registros: {len(df)}")
            >>> # Entrenar modelo con df
        """
        
        try:
            connection = self._get_connection()
            
            query = """
                SELECT 
                    Datetime, Global_active_power, Global_reactive_power,
                    Voltage, Global_intensity, Sub_metering_1, Sub_metering_2,
                    Sub_metering_3
                FROM energy_readings
                ORDER BY Datetime ASC
            """
            
            if limit is not None:
                query += f" LIMIT {limit}"
            
            # Leer a DataFrame
            df = pd.read_sql(
                query,
                connection,
                parse_dates=['Datetime']
            )
            
            connection.close()
            
            # Configurar Datetime como índice (formato DomusAI)
            if not df.empty:
                df.set_index('Datetime', inplace=True)
            
            logger.info(f"✅ Dataset completo obtenido: {len(df)} registros")
            
            return df
            
        except Error as e:
            error_msg = f"Error obteniendo todos los datos: {e}"
            logger.error(f"❌ {error_msg}")
            raise DatabaseQueryError(error_msg)
    
    def get_data_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Obtener datos por rango de fechas específico.
        
        Args:
            start_date: Fecha/hora de inicio
            end_date: Fecha/hora de fin
            
        Returns:
            DataFrame con datos en el rango especificado
            
        Example:
            >>> db = RailwayDatabaseReader()
            >>> start = datetime(2025, 10, 1)
            >>> end = datetime(2025, 10, 19)
            >>> df = db.get_data_by_date_range(start, end)
        """
        
        try:
            connection = self._get_connection()
            
            query = """
                SELECT 
                    Datetime, Global_active_power, Global_reactive_power,
                    Voltage, Global_intensity, Sub_metering_1, Sub_metering_2,
                    Sub_metering_3
                FROM energy_readings
                WHERE Datetime BETWEEN %s AND %s
                ORDER BY Datetime ASC
            """
            
            df = pd.read_sql(
                query,
                connection,
                params=(start_date, end_date),
                parse_dates=['Datetime']
            )
            
            connection.close()
            
            # Configurar Datetime como índice
            if not df.empty:
                df.set_index('Datetime', inplace=True)
            
            logger.info(f"✅ Datos obtenidos: {len(df)} registros ({start_date} a {end_date})")
            
            return df
            
        except Error as e:
            error_msg = f"Error obteniendo datos por rango: {e}"
            logger.error(f"❌ {error_msg}")
            raise DatabaseQueryError(error_msg)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas básicas de la base de datos.
        
        Returns:
            Dict con estadísticas: total_records, first_reading, last_reading, etc.
            
        Example:
            >>> db = RailwayDatabaseReader()
            >>> stats = db.get_statistics()
            >>> print(f"Total registros: {stats['total_records']}")
        """
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Contar registros totales
            cursor.execute("SELECT COUNT(*) as total FROM energy_readings")
            total = cursor.fetchone()['total']
            
            # Primera lectura
            cursor.execute("""
                SELECT Datetime, Global_active_power 
                FROM energy_readings 
                ORDER BY Datetime ASC LIMIT 1
            """)
            first = cursor.fetchone()
            
            # Última lectura
            cursor.execute("""
                SELECT Datetime, Global_active_power 
                FROM energy_readings 
                ORDER BY Datetime DESC LIMIT 1
            """)
            last = cursor.fetchone()
            
            # Promedios
            cursor.execute("""
                SELECT 
                    AVG(Global_active_power) as avg_power,
                    MAX(Global_active_power) as max_power,
                    MIN(Global_active_power) as min_power,
                    AVG(Voltage) as avg_voltage
                FROM energy_readings
            """)
            averages = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            stats = {
                'total_records': total,
                'first_reading': first['Datetime'] if first else None,
                'last_reading': last['Datetime'] if last else None,
                'avg_power_kw': float(averages['avg_power']) if averages['avg_power'] else 0,
                'max_power_kw': float(averages['max_power']) if averages['max_power'] else 0,
                'min_power_kw': float(averages['min_power']) if averages['min_power'] else 0,
                'avg_voltage': float(averages['avg_voltage']) if averages['avg_voltage'] else 0
            }
            
            logger.info(f"✅ Estadísticas obtenidas: {total} registros")
            
            return stats
            
        except Error as e:
            error_msg = f"Error obteniendo estadísticas: {e}"
            logger.error(f"❌ {error_msg}")
            raise DatabaseQueryError(error_msg)
    
    def get_hourly_consumption(self, days: int = 7) -> pd.DataFrame:
        """
        Obtener consumo agregado por hora (últimos N días).
        
        Args:
            days: Número de días hacia atrás (default: 7)
            
        Returns:
            DataFrame con consumo promedio por hora
            
        Example:
            >>> db = RailwayDatabaseReader()
            >>> hourly = db.get_hourly_consumption(days=7)
            >>> # Útil para análisis de patrones horarios
        """
        
        try:
            connection = self._get_connection()
            
            limit_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT 
                    DATE_FORMAT(Datetime, '%%Y-%%m-%%d %%H:00:00') as hour,
                    AVG(Global_active_power) as avg_power,
                    MAX(Global_active_power) as max_power,
                    MIN(Global_active_power) as min_power,
                    COUNT(*) as readings_count
                FROM energy_readings
                WHERE Datetime >= %s
                GROUP BY DATE_FORMAT(Datetime, '%%Y-%%m-%%d %%H:00:00')
                ORDER BY hour ASC
            """
            
            df = pd.read_sql(
                query,
                connection,
                params=(limit_date,),
                parse_dates=['hour']
            )
            
            connection.close()
            
            if not df.empty:
                df.set_index('hour', inplace=True)
            
            logger.info(f"✅ Consumo horario obtenido: {len(df)} horas (últimos {days} días)")
            
            return df
            
        except Error as e:
            error_msg = f"Error obteniendo consumo horario: {e}"
            logger.error(f"❌ {error_msg}")
            raise DatabaseQueryError(error_msg)
    
    def close_pool(self) -> None:
        """Cerrar connection pool (llamar al finalizar aplicación)"""
        
        if self.pool:
            logger.info("🔌 Cerrando connection pool...")
            # MySQL connector pool se cierra automáticamente
            self.pool = None
            logger.info("✅ Connection pool cerrado")


# Instancia global singleton para uso en toda la aplicación
_db_reader_instance: Optional[RailwayDatabaseReader] = None


def get_db_reader() -> RailwayDatabaseReader:
    """
    Obtener instancia singleton de RailwayDatabaseReader.
    
    Returns:
        Instancia global de RailwayDatabaseReader
        
    Example:
        >>> from src.database import get_db_reader
        >>> db = get_db_reader()
        >>> df = db.get_recent_readings(hours=24)
    """
    
    global _db_reader_instance
    
    if _db_reader_instance is None:
        _db_reader_instance = RailwayDatabaseReader()
    
    return _db_reader_instance


# Funciones de conveniencia para uso directo
def get_recent_data(hours: int = 24) -> pd.DataFrame:
    """Función de conveniencia: obtener datos recientes"""
    return get_db_reader().get_recent_readings(hours)


def get_all_data(limit: Optional[int] = None) -> pd.DataFrame:
    """Función de conveniencia: obtener todos los datos"""
    return get_db_reader().get_all_data(limit)


def get_latest() -> Optional[Dict[str, Any]]:
    """Función de conveniencia: obtener última lectura"""
    return get_db_reader().get_latest_reading()


def test_db_connection() -> bool:
    """Función de conveniencia: test de conexión"""
    return get_db_reader().test_connection()


# Demo de uso
if __name__ == "__main__":
    print("=" * 70)
    print("🧪 DEMO - Railway Database Reader")
    print("=" * 70)
    
    # Crear instancia
    db = RailwayDatabaseReader()
    
    # Test 1: Conexión
    print("\n1️⃣ Test de conexión...")
    if db.test_connection():
        print("   ✅ Conexión exitosa")
    else:
        print("   ❌ Conexión fallida")
        sys.exit(1)
    
    # Test 2: Estadísticas
    print("\n2️⃣ Estadísticas de la base de datos...")
    try:
        stats = db.get_statistics()
        print(f"   📊 Total registros: {stats['total_records']}")
        print(f"   📅 Primera lectura: {stats['first_reading']}")
        print(f"   📅 Última lectura: {stats['last_reading']}")
        print(f"   ⚡ Potencia promedio: {stats['avg_power_kw']:.3f} kW")
        print(f"   📈 Potencia máxima: {stats['max_power_kw']:.3f} kW")
        print(f"   📉 Potencia mínima: {stats['min_power_kw']:.3f} kW")
        print(f"   🔋 Voltaje promedio: {stats['avg_voltage']:.2f} V")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Última lectura
    print("\n3️⃣ Última lectura...")
    try:
        latest = db.get_latest_reading()
        if latest:
            print(f"   📅 Datetime: {latest['Datetime']}")
            print(f"   ⚡ Potencia: {latest['Global_active_power']} kW")
            print(f"   🔋 Voltaje: {latest['Voltage']} V")
            print(f"   📊 Intensidad: {latest['Global_intensity']} A")
        else:
            print("   ⚠️ No hay lecturas")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Últimas 24 horas
    print("\n4️⃣ Lecturas últimas 24 horas...")
    try:
        df = db.get_recent_readings(hours=24)
        print(f"   📊 Registros obtenidos: {len(df)}")
        if not df.empty:
            print(f"   📋 Columnas: {', '.join(df.columns)}")
            print(f"   📅 Rango: {df.index.min()} a {df.index.max()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Todos los datos
    print("\n5️⃣ Obtener todos los datos...")
    try:
        df_all = db.get_all_data(limit=10)  # Limitar para demo
        print(f"   📊 Registros obtenidos: {len(df_all)}")
        if not df_all.empty:
            print(f"   📊 Muestra de datos:")
            print(df_all.head())
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETADA")
    print("=" * 70)
