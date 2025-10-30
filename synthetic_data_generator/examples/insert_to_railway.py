"""
🚀 SCRIPT PARA SUBIR DATOS SINTÉTICOS A RAILWAY MYSQL

Inserta datos sintéticos generados en la base de datos Railway.
Usa batch inserts para mejor rendimiento.

Uso:
    python insert_to_railway.py ../output/synthetic_30days_20251029.csv
    python insert_to_railway.py ../output/synthetic_30days_20251029.csv --batch-size 500
"""

import sys
import pandas as pd
import mysql.connector
from mysql.connector import Error
from pathlib import Path
import argparse
import logging
from datetime import datetime
from typing import Optional

# Agregar src/ del proyecto principal al path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config import DatabaseConfig
except ImportError:
    print("❌ Error: No se pudo importar DatabaseConfig")
    print("   Asegúrate de que estás ejecutando desde synthetic_data_generator/")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_csv(filepath: str) -> pd.DataFrame:
    """
    Carga el CSV sintético
    
    Args:
        filepath: Ruta al archivo CSV
        
    Returns:
        DataFrame con los datos
    """
    logger.info(f"📂 Cargando CSV: {filepath}")
    
    df = pd.read_csv(filepath)
    
    # Asegurar que Datetime está en formato correcto
    if 'Datetime' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'])
    else:
        # Si la primera columna es el índice sin nombre
        df.index = pd.to_datetime(df.index)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Datetime'}, inplace=True)
    
    # Validar columnas requeridas
    required_columns = [
        'Datetime',
        'Global_active_power',
        'Global_reactive_power',
        'Voltage',
        'Global_intensity',
        'Sub_metering_1',
        'Sub_metering_2',
        'Sub_metering_3'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"❌ Error: Faltan columnas requeridas: {missing_columns}")
        sys.exit(1)
    
    logger.info(f"   ✅ {len(df):,} registros cargados")
    logger.info(f"   Rango: {df['Datetime'].min()} → {df['Datetime'].max()}")
    
    return df


def insert_to_railway(
    df: pd.DataFrame,
    batch_size: int = 1000,
    dry_run: bool = False
) -> bool:
    """
    Inserta datos en Railway MySQL
    
    Args:
        df: DataFrame con los datos
        batch_size: Tamaño de batch para inserts
        dry_run: Si True, solo simula la inserción
        
    Returns:
        True si la inserción fue exitosa
    """
    if dry_run:
        logger.info("🔍 MODO DRY RUN - No se insertará nada en la BD")
    
    # Obtener configuración
    config = DatabaseConfig()
    
    logger.info("\n📡 Conectando a Railway MySQL...")
    logger.info(f"   Host: {config.MYSQL_HOST}")
    logger.info(f"   Base de datos: {config.MYSQL_DATABASE}")
    
    try:
        connection = mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE
        )
        
        if connection.is_connected():
            logger.info("   ✅ Conexión establecida")
            cursor = connection.cursor()
            
            # Verificar tabla existe
            cursor.execute("SHOW TABLES LIKE 'energy_readings'")
            result = cursor.fetchone()
            if not result:
                logger.error("❌ Error: Tabla 'energy_readings' no existe")
                cursor.close()
                connection.close()
                return False
            
            if dry_run:
                logger.info("\n✅ DRY RUN COMPLETADO - Conexión exitosa")
                cursor.close()
                connection.close()
                return True
            
            # Preparar query de inserción
            insert_query = """
                INSERT INTO energy_readings (
                    datetime,
                    global_active_power,
                    global_reactive_power,
                    voltage,
                    global_intensity,
                    sub_metering_1,
                    sub_metering_2,
                    sub_metering_3
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            # Insertar en batches
            logger.info(f"\n💾 Insertando {len(df):,} registros (batch size: {batch_size})...")
            
            total_batches = (len(df) + batch_size - 1) // batch_size
            inserted_count = 0
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min((batch_num + 1) * batch_size, len(df))
                batch_df = df.iloc[start_idx:end_idx]
                
                # Preparar datos del batch
                batch_data = []
                for _, row in batch_df.iterrows():
                    batch_data.append((
                        row['Datetime'],
                        float(row['Global_active_power']),
                        float(row['Global_reactive_power']),
                        float(row['Voltage']),
                        float(row['Global_intensity']),
                        float(row['Sub_metering_1']),
                        float(row['Sub_metering_2']),
                        float(row['Sub_metering_3'])
                    ))
                
                # Ejecutar batch insert
                cursor.executemany(insert_query, batch_data)
                connection.commit()
                
                inserted_count += len(batch_data)
                progress = (inserted_count / len(df)) * 100
                
                logger.info(
                    f"   Batch {batch_num + 1}/{total_batches}: "
                    f"{inserted_count:,}/{len(df):,} registros ({progress:.1f}%)"
                )
            
            # Verificar inserción
            cursor.execute("SELECT COUNT(*) FROM energy_readings")
            count_result = cursor.fetchone()
            total_records = count_result[0] if count_result else 0
            
            print("\n" + "=" * 70)
            print("✅ INSERCIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 70)
            print(f"   Registros insertados:  {inserted_count:,}")
            print(f"   Total en Railway:      {total_records:,}")
            print(f"   Tiempo:                {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)
            
            cursor.close()
            return True
        else:
            logger.error("❌ Error: No se pudo establecer conexión con Railway")
            return False
            
    except Error as e:
        logger.error(f"❌ Error de MySQL: {e}")
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            logger.info("\n📡 Conexión cerrada")


def main():
    """Función principal CLI"""
    parser = argparse.ArgumentParser(
        description='🚀 Subir datos sintéticos a Railway MySQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Insertar archivo generado
  python insert_to_railway.py ../output/synthetic_30days_20251029.csv
  
  # Con batch size personalizado
  python insert_to_railway.py ../output/synthetic_30days_20251029.csv --batch-size 500
  
  # Dry run (solo probar conexión)
  python insert_to_railway.py ../output/synthetic_30days_20251029.csv --dry-run
        """
    )
    
    parser.add_argument(
        'csv_file',
        type=str,
        help='Ruta al archivo CSV generado'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Tamaño de batch para inserts (default: 1000)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Solo probar conexión sin insertar datos'
    )
    
    args = parser.parse_args()
    
    # Verificar que el archivo existe
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        logger.error(f"❌ Error: Archivo no encontrado: {csv_path}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("🚀 INSERCIÓN DE DATOS SINTÉTICOS A RAILWAY")
    print("=" * 70)
    
    # Cargar CSV
    df = load_csv(str(csv_path))
    
    # Insertar en Railway
    success = insert_to_railway(
        df,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
