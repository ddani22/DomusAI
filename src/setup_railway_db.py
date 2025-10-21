"""
setup_railway_db.py
===================
Script ONE-TIME para configurar el schema de Railway MySQL (SIMPLIFICADO SPRINT 8).

PROPÓSITO:
  - Crear SOLO tabla energy_readings en Railway MySQL (formato DomusAI)
  - Insertar datos de prueba para validar conexión
  - Verificar schema creado correctamente

USO:
  1. Asegurarse que .env tiene las credenciales de Railway correctas
  2. Ejecutar: python src/setup_railway_db.py
  3. Verificar en Railway console que la tabla existe

ARQUITECTURA SPRINT 8:
  - Compañero → ESP32 → INSERT directo a Railway MySQL
  - Tú → SELECT de Railway → Auto-train ML → Anomalies → Reports
  
VERSIÓN: 2.0 (Simplificada - Solo energy_readings)
FECHA: 2025-01-XX
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import mysql.connector
from mysql.connector import Error
import logging

# Configurar ruta del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DB_CONFIG
from src.exceptions import DatabaseConnectionError, DatabaseSetupError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class RailwayDatabaseSetup:
    """Manager para configurar schema de Railway MySQL (SOLO energy_readings)"""
    
    def __init__(self):
        self.connection: Any = None
        self.cursor: Any = None
    
    def connect(self) -> None:
        """Conectar a Railway MySQL usando credenciales de .env"""
        
        logger.info("🔌 Conectando a Railway MySQL...")
        
        try:
            self.connection = mysql.connector.connect(
                **DB_CONFIG.connection_params,
                connection_timeout=30
            )
            
            # Asegurar que la conexión es válida antes de crear cursor
            if self.connection is None or not self.connection.is_connected():
                raise DatabaseConnectionError("Conexión fallida")
            
            self.cursor = self.connection.cursor()
            
            # Verificar versión de MySQL
            if self.cursor is not None:
                self.cursor.execute("SELECT VERSION()")
                result = self.cursor.fetchone()
                version = result[0] if result else "Unknown"
                
                logger.info(f"✅ Conectado exitosamente")
                logger.info(f"   MySQL Version: {version}")
                logger.info(f"   Host: {DB_CONFIG.MYSQL_HOST}")
                logger.info(f"   Database: {DB_CONFIG.MYSQL_DATABASE}")
            
        except Error as e:
            error_msg = f"Error conectando a Railway: {e}"
            logger.error(f"❌ {error_msg}")
            raise DatabaseConnectionError(error_msg)
    
    def create_tables(self) -> None:
        """Crear tabla principal energy_readings"""
        
        logger.info("\n📊 Creando tabla principal...")
        
        if self.cursor is None or self.connection is None:
            raise DatabaseSetupError("Cursor o conexión no inicializados")
        
        # Tabla: energy_readings (lecturas en tiempo real - COLUMNAS DEL DATASET DOMUSAI)
        sql_energy_readings = """
        CREATE TABLE IF NOT EXISTS energy_readings (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            Datetime DATETIME NOT NULL COMMENT 'Fecha y hora de la lectura',
            Global_active_power DECIMAL(10, 3) NOT NULL COMMENT 'Potencia activa global (kW)',
            Global_reactive_power DECIMAL(10, 3) COMMENT 'Potencia reactiva global (kW)',
            Voltage DECIMAL(6, 2) NOT NULL COMMENT 'Voltaje (V)',
            Global_intensity DECIMAL(8, 3) COMMENT 'Intensidad global (A)',
            Sub_metering_1 DECIMAL(10, 3) DEFAULT 0 COMMENT 'Sub-medición 1: Cocina (Wh)',
            Sub_metering_2 DECIMAL(10, 3) DEFAULT 0 COMMENT 'Sub-medición 2: Lavandería (Wh)',
            Sub_metering_3 DECIMAL(10, 3) DEFAULT 0 COMMENT 'Sub-medición 3: Climatización (Wh)',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp de inserción en DB',
            
            INDEX idx_datetime (Datetime),
            INDEX idx_created_at (created_at),
            INDEX idx_power (Global_active_power),
            INDEX idx_voltage (Voltage)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='Lecturas de consumo energético en tiempo real desde ESP32 (formato DomusAI)';
        """
        
        try:
            logger.info("   Creando tabla: energy_readings")
            self.cursor.execute(sql_energy_readings)
            self.connection.commit()
            logger.info("   ✅ Tabla energy_readings creada exitosamente")
        except Error as e:
            if e.errno == 1050:  # Table already exists
                logger.info("   ℹ️ Tabla energy_readings ya existe (omitiendo)")
            else:
                logger.error(f"   ❌ Error creando energy_readings: {e}")
                raise DatabaseSetupError(f"Error creando tabla energy_readings: {e}")
    
    def verify_setup(self) -> Dict[str, Any]:
        """Verificar que el setup se completó correctamente"""
        
        logger.info("\n🔍 Verificando setup...")
        
        if self.cursor is None:
            raise DatabaseSetupError("Cursor no inicializado")
        
        try:
            # Contar tablas creadas
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_type = 'BASE TABLE'
            """, (DB_CONFIG.MYSQL_DATABASE,))
            
            result = self.cursor.fetchone()
            tables_count = result[0] if result else 0
            
            # Obtener nombres de tablas
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """, (DB_CONFIG.MYSQL_DATABASE,))
            tables = [row[0] for row in self.cursor.fetchall()]
            
            logger.info(f"   ✅ Tablas creadas: {tables_count}")
            for table in tables:
                logger.info(f"      - {table}")
            
            return {
                'tables_count': tables_count,
                'tables': tables,
                'status': 'success'
            }
            
        except Error as e:
            logger.error(f"   ❌ Error verificando setup: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def insert_test_data(self) -> None:
        """Insertar datos de prueba para validar la tabla"""
        
        logger.info("\n🧪 Insertando datos de prueba...")
        
        if self.cursor is None or self.connection is None:
            raise DatabaseSetupError("Cursor o conexión no inicializados")
        
        # Datos de prueba realistas (simulando lectura del ESP32)
        test_data = {
            'Datetime': datetime.now().replace(microsecond=0),
            'Global_active_power': 2.648,
            'Global_reactive_power': 0.226,
            'Voltage': 241.78,
            'Global_intensity': 11.2,
            'Sub_metering_1': 1.0,
            'Sub_metering_2': 1.0,
            'Sub_metering_3': 17.0
        }
        
        sql_test_reading = """
        INSERT INTO energy_readings 
        (Datetime, Global_active_power, Global_reactive_power, Voltage, Global_intensity, 
         Sub_metering_1, Sub_metering_2, Sub_metering_3)
        VALUES 
        (%(Datetime)s, %(Global_active_power)s, %(Global_reactive_power)s, %(Voltage)s, 
         %(Global_intensity)s, %(Sub_metering_1)s, %(Sub_metering_2)s, %(Sub_metering_3)s)
        """
        
        try:
            self.cursor.execute(sql_test_reading, test_data)
            self.connection.commit()
            logger.info("   ✅ Datos de prueba insertados")
            
            # Mostrar resumen
            self.cursor.execute("SELECT COUNT(*) FROM energy_readings")
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"   📊 Total lecturas en DB: {count}")
            
            # Mostrar última lectura
            self.cursor.execute("""
                SELECT Datetime, Global_active_power, Voltage, Global_intensity 
                FROM energy_readings 
                ORDER BY created_at DESC LIMIT 1
            """)
            last_reading = self.cursor.fetchone()
            
            if last_reading:
                dt, power, voltage, intensity = last_reading
                logger.info(f"   📅 Última lectura: {dt}")
                logger.info(f"   ⚡ Potencia: {power} kW")
                logger.info(f"   🔋 Voltaje: {voltage} V")
                logger.info(f"   📊 Intensidad: {intensity} A")
                
        except Error as e:
            logger.error(f"   ❌ Error insertando datos de prueba: {e}")
            raise DatabaseSetupError(f"Error insertando datos de prueba: {e}")
    
    def close(self) -> None:
        """Cerrar conexión a Railway"""
        
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("\n🔌 Conexión cerrada correctamente")
        except Error as e:
            logger.error(f"⚠️ Error cerrando conexión: {e}")
    
    def run_setup(self) -> bool:
        """Ejecutar setup completo de Railway MySQL"""
        
        logger.info("=" * 70)
        logger.info("🚀 RAILWAY MYSQL SETUP - SPRINT 8 SIMPLIFICADO")
        logger.info("=" * 70)
        
        try:
            # Paso 1: Conectar
            self.connect()
            
            # Paso 2: Crear tabla energy_readings
            self.create_tables()
            
            # Paso 3: Insertar datos de prueba
            self.insert_test_data()
            
            # Paso 4: Verificar
            verification = self.verify_setup()
            
            # Resultado final
            logger.info("\n" + "=" * 70)
            logger.info("🎉 SETUP COMPLETADO EXITOSAMENTE")
            logger.info("=" * 70)
            logger.info(f"✅ Tablas creadas: {verification['tables_count']}")
            logger.info(f"✅ Base de datos: {DB_CONFIG.MYSQL_DATABASE}")
            logger.info(f"✅ Host: {DB_CONFIG.MYSQL_HOST}:{DB_CONFIG.MYSQL_PORT}")
            logger.info("=" * 70)
            
            return True
            
        except (DatabaseConnectionError, DatabaseSetupError) as e:
            logger.error(f"\n❌ SETUP FALLIDO: {e}")
            return False
        
        finally:
            self.close()


def main():
    """Función principal"""
    setup = RailwayDatabaseSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
