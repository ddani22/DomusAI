import pandas as pd
import numpy as np

def limpiar_dataset_consumo():
    """
    Script para limpiar el dataset de consumo energético.
    
    Pasos realizados:
    1. Cargar el archivo CSV con pandas
    2. Eliminar la columna "index"
    3. Combinar columnas "Date" y "Time" en "Datetime" y establecer como índice
    4. Convertir columnas numéricas a tipo float
    5. Manejar valores nulos de "Sub_metering_3"
    6. Convertir años de 2 dígitos a 4 dígitos
    7. Guardar el DataFrame limpio
    """
    
    print("🔄 Iniciando limpieza del dataset de consumo energético...")
    
    # 1. Cargar el archivo CSV con pandas
    print("📊 Cargando archivo CSV...")
    df = pd.read_csv("Dataset de prueba de consumo.csv")
    print(f"   Filas cargadas: {len(df):,}")
    print(f"   Columnas: {list(df.columns)}")
    
    # 2. Eliminar la columna "index"
    print("\n🗑️  Eliminando columna 'index'...")
    if 'index' in df.columns:
        df = df.drop('index', axis=1)
        print("   ✅ Columna 'index' eliminada correctamente")
    else:
        print("   ⚠️  Columna 'index' no encontrada")
    
    # 3. Convertir fechas de 2 dígitos a 4 dígitos
    print("\n📅 Convirtiendo fechas de 2 a 4 dígitos...")
    
    def convertir_fecha_a_4_digitos(fecha_str):
        """Convierte fechas dd/mm/yy a dd/mm/yyyy"""
        try:
            partes = fecha_str.split('/')
            if len(partes) != 3:
                return fecha_str
                
            dia, mes, año_str = partes[0], partes[1], partes[2]
            
            # Manejar casos donde el año ya podría ser de 4 dígitos
            if len(año_str) == 4:
                return fecha_str  # Ya está en formato correcto
            
            año_2d = int(año_str)
            
            # Convertir año de 2 dígitos a 4 dígitos
            # Para datos de consumo energético, es más probable que sean 2000-2010s
            # Asumiendo que años 00-30 son 2000-2030, y 70-99 son 1970-1999
            if año_2d <= 30:
                año_4d = 2000 + año_2d
            elif año_2d >= 70:
                año_4d = 1900 + año_2d
            else:
                # Para valores entre 31-69, asumir 2000s (más probable para datos de consumo)
                año_4d = 2000 + año_2d
            
            return f"{dia}/{mes}/{año_4d}"
        except Exception as e:
            print(f"   ⚠️  Error procesando fecha '{fecha_str}': {e}")
            return fecha_str  # Retornar original si hay error
    
    # Primero verificar el formato de la fecha en una muestra
    print(f"   Muestra de fechas originales: {df['Date'].head(3).tolist()}")
    
    df['Date_4digitos'] = df['Date'].apply(convertir_fecha_a_4_digitos)
    print(f"   Muestra de fechas convertidas: {df['Date_4digitos'].head(3).tolist()}")
    print("   ✅ Fechas convertidas a formato de 4 dígitos")
    
    # 4. Combinar las columnas "Date" y "Time" en una sola columna "Datetime"
    print("\n📅 Combinando columnas 'Date' y 'Time'...")
    
    # Crear la columna Datetime combinando Date y Time con años de 4 dígitos
    df['Datetime'] = pd.to_datetime(df['Date_4digitos'] + ' ' + df['Time'], 
                                    format='%d/%m/%Y %H:%M:%S', 
                                    errors='coerce')
    
    # Mostrar el rango de fechas para verificar la conversión
    fecha_min = df['Datetime'].min()
    fecha_max = df['Datetime'].max()
    print(f"   Rango de fechas convertido: {fecha_min} a {fecha_max}")
    
    # Establecer como índice del DataFrame
    df.set_index('Datetime', inplace=True)
    
    # Eliminar las columnas originales Date, Time y Date_4digitos
    df = df.drop(['Date', 'Time', 'Date_4digitos'], axis=1)
    print("   ✅ Columnas combinadas en 'Datetime' y establecida como índice")
    
    # 5. Convertir todas las columnas de consumo y voltaje a tipo float
    print("\n🔢 Convirtiendo columnas numéricas a tipo float...")
    columnas_numericas = [
        "Global_active_power", 
        "Global_reactive_power", 
        "Voltage", 
        "Global_intensity", 
        "Sub_metering_1", 
        "Sub_metering_2", 
        "Sub_metering_3"
    ]
    
    for columna in columnas_numericas:
        if columna in df.columns:
            # Convertir '?' y otros valores no numéricos a NaN, luego a float
            df[columna] = pd.to_numeric(df[columna], errors='coerce').astype('float64')
            print(f"   ✅ '{columna}' convertida a float")
        else:
            print(f"   ⚠️  Columna '{columna}' no encontrada")
    
    # 6. Manejar los valores nulos de "Sub_metering_3"
    print("\n🔧 Manejando valores nulos en 'Sub_metering_3'...")
    valores_nulos_antes = df['Sub_metering_3'].isna().sum()
    print(f"   Valores nulos encontrados: {valores_nulos_antes:,}")
    
    if valores_nulos_antes > 0:
        df['Sub_metering_3'] = df['Sub_metering_3'].fillna(0)
        print("   ✅ Valores nulos rellenados con 0")
    else:
        print("   ℹ️  No se encontraron valores nulos")
    
    # Verificar si hay otros valores nulos en el dataset
    print("\n🔍 Verificando valores nulos en todo el dataset...")
    valores_nulos_por_columna = df.isnull().sum()
    if valores_nulos_por_columna.sum() > 0:
        print("   Valores nulos por columna:")
        for col, nulos in valores_nulos_por_columna.items():
            if nulos > 0:
                print(f"     - {col}: {nulos:,} valores nulos")
    else:
        print("   ✅ No hay valores nulos en el dataset")
    
    # 7. Guardar el DataFrame limpio en un nuevo CSV
    print("\n💾 Guardando DataFrame limpio...")
    df.to_csv("consumo_limpio_pruebas.csv")
    print("   ✅ Dataset guardado como 'consumo_limpio_pruebas.csv'")

    # Mostrar resultados finales
    print("\n" + "="*60)
    print("📊 RESUMEN DEL DATASET LIMPIO")
    print("="*60)
    
    print("\n🔍 Primeras 5 filas del DataFrame limpio:")
    print(df.head())
    
    print(f"\n📈 Información del DataFrame:")
    print(f"   - Forma: {df.shape}")
    print(f"   - Índice: {type(df.index).__name__}")
    print(f"   - Rango de fechas: {df.index.min()} a {df.index.max()}")
    
    print(f"\n📋 Resumen de info() para confirmar tipos de datos:")
    df.info()
    
    print("\n✅ ¡Limpieza del dataset completada exitosamente!")
    return df

if __name__ == "__main__":
    # Ejecutar la función de limpieza
    dataset_limpio = limpiar_dataset_consumo()