"""
✅ DomusAI - Módulo de Validaciones

Funciones reutilizables para validar datos, paths, configuraciones
y otros inputs del usuario o externos.

Autor: DomusAI Team
Fecha: Octubre 2025
Versión: 1.0
"""

from pathlib import Path
from typing import Union, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from exceptions import (
    DataValidationError,
    InsufficientDataError,
    DataQualityError,
    ConfigurationError
)


# ============================================================================
# VALIDADORES DE PATHS Y ARCHIVOS
# ============================================================================

def validate_csv_path(path: Union[str, Path], must_exist: bool = True) -> Path:
    """
    Validar que path existe y es archivo CSV válido
    
    Args:
        path: Ruta al archivo CSV
        must_exist: Si True, verifica que archivo exista
    
    Returns:
        Path validado y convertido a objeto Path
    
    Raises:
        FileNotFoundError: Si archivo no existe y must_exist=True
        DataValidationError: Si no es archivo CSV
    
    Example:
        >>> csv_path = validate_csv_path("data/Dataset_clean_test.csv")
        >>> print(csv_path)
        data/Dataset_clean_test.csv
    """
    path = Path(path)
    
    if must_exist and not path.exists():
        raise FileNotFoundError(
            f"❌ Archivo no encontrado: {path}\n"
            f"   Verifica que la ruta sea correcta"
        )
    
    if path.suffix.lower() not in ['.csv', '.txt']:
        raise DataValidationError(
            f"❌ Archivo debe ser CSV o TXT, recibido: {path.suffix}\n"
            f"   Archivo: {path}"
        )
    
    return path


def validate_directory(path: Union[str, Path], create_if_missing: bool = False) -> Path:
    """
    Validar que path es directorio válido
    
    Args:
        path: Ruta al directorio
        create_if_missing: Si True, crea directorio si no existe
    
    Returns:
        Path validado
    
    Raises:
        FileNotFoundError: Si directorio no existe y create_if_missing=False
        ConfigurationError: Si path es archivo, no directorio
    """
    path = Path(path)
    
    if not path.exists():
        if create_if_missing:
            path.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(
                f"❌ Directorio no encontrado: {path}\n"
                f"   Usa create_if_missing=True para crear automáticamente"
            )
    
    if path.exists() and not path.is_dir():
        raise ConfigurationError(
            f"❌ Path debe ser directorio, no archivo: {path}"
        )
    
    return path


def safe_path(base_dir: Path, user_input: str) -> Path:
    """
    Crear path seguro evitando path traversal attacks
    
    Args:
        base_dir: Directorio base permitido
        user_input: Input del usuario (ej: nombre de archivo)
    
    Returns:
        Path seguro dentro de base_dir
    
    Raises:
        DataValidationError: Si user_input intenta escapar de base_dir
    
    Example:
        >>> from config import PATHS
        >>> report_path = safe_path(PATHS.GENERATED_REPORTS, "reporte.html")
        >>> # ✅ reports/generated/reporte.html
        >>> 
        >>> bad_path = safe_path(PATHS.GENERATED_REPORTS, "../../secrets.txt")
        >>> # ❌ DataValidationError: Path no permitido
    """
    # Resolver path absoluto
    requested_path = (base_dir / user_input).resolve()
    base_dir_resolved = base_dir.resolve()
    
    # Verificar que esté dentro de base_dir
    try:
        requested_path.relative_to(base_dir_resolved)
    except ValueError:
        raise DataValidationError(
            f"❌ Path no permitido: {user_input}\n"
            f"   Debe estar dentro de: {base_dir}\n"
            f"   Se intentó acceder a: {requested_path}"
        )
    
    return requested_path


# ============================================================================
# VALIDADORES DE DATAFRAMES
# ============================================================================

def validate_dataframe(
    df: pd.DataFrame,
    required_columns: Optional[List[str]] = None,
    min_rows: int = 10,
    allow_nulls: bool = True,
    max_null_percentage: float = 50.0
) -> None:
    """
    Validar que DataFrame tenga estructura esperada
    
    Args:
        df: DataFrame a validar
        required_columns: Lista de columnas que deben existir
        min_rows: Número mínimo de filas requeridas
        allow_nulls: Si False, no permite valores nulos
        max_null_percentage: Porcentaje máximo de nulos permitido
    
    Raises:
        DataValidationError: Si DataFrame inválido
        InsufficientDataError: Si menos filas que min_rows
        DataQualityError: Si demasiados nulos
    
    Example:
        >>> validate_dataframe(
        ...     df,
        ...     required_columns=['Global_active_power', 'Voltage'],
        ...     min_rows=100,
        ...     max_null_percentage=10.0
        ... )
    """
    # Validar DataFrame no vacío
    if df is None or df.empty:
        raise DataValidationError("❌ DataFrame vacío o None")
    
    # Validar número mínimo de filas
    if len(df) < min_rows:
        raise InsufficientDataError(
            f"❌ DataFrame debe tener al menos {min_rows} filas, tiene {len(df)}\n"
            f"   Necesitas más datos para análisis confiable"
        )
    
    # Validar columnas requeridas
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise DataValidationError(
                f"❌ Columnas faltantes: {missing}\n"
                f"   Columnas disponibles: {list(df.columns)}"
            )
    
    # Validar calidad de datos (nulos)
    if not allow_nulls:
        null_cols = df.columns[df.isnull().any()].tolist()
        if null_cols:
            raise DataQualityError(
                f"❌ Valores nulos no permitidos\n"
                f"   Columnas con nulos: {null_cols}"
            )
    
    # Validar porcentaje de nulos
    null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    if null_percentage > max_null_percentage:
        raise DataQualityError(
            f"❌ Demasiados valores nulos: {null_percentage:.1f}%\n"
            f"   Máximo permitido: {max_null_percentage}%\n"
            f"   Considera limpiar datos o rellenar nulos"
        )


def validate_datetime_index(df: pd.DataFrame) -> None:
    """
    Validar que DataFrame tiene índice datetime válido
    
    Args:
        df: DataFrame a validar
    
    Raises:
        DataValidationError: Si índice no es DatetimeIndex
    
    Example:
        >>> df = pd.read_csv('data.csv', index_col=0, parse_dates=True)
        >>> validate_datetime_index(df)
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise DataValidationError(
            f"❌ Índice debe ser DatetimeIndex, recibido: {type(df.index).__name__}\n"
            f"   Solución: pd.read_csv(..., index_col=0, parse_dates=True)"
        )
    
    # Validar que no hay timestamps nulos
    if df.index.isnull().any():
        null_count = df.index.isnull().sum()
        raise DataQualityError(
            f"❌ Índice datetime contiene {null_count} valores nulos\n"
            f"   Limpia datos antes de análisis"
        )


def validate_date_range(
    df: pd.DataFrame,
    date_column: Optional[str] = None,
    min_date: Optional[pd.Timestamp] = None,
    max_date: Optional[pd.Timestamp] = None
) -> None:
    """
    Validar rango de fechas en DataFrame
    
    Args:
        df: DataFrame a validar
        date_column: Nombre de columna datetime (None = usar índice)
        min_date: Fecha mínima permitida
        max_date: Fecha máxima permitida
    
    Raises:
        DataValidationError: Si fechas fuera de rango
    
    Example:
        >>> validate_date_range(
        ...     df,
        ...     min_date=pd.Timestamp('2007-01-01'),
        ...     max_date=pd.Timestamp('2010-12-31')
        ... )
    """
    # Obtener columna de fechas
    if date_column is None:
        if not isinstance(df.index, pd.DatetimeIndex):
            raise DataValidationError(
                "❌ date_column=None requiere DatetimeIndex"
            )
        dates = df.index
    else:
        if date_column not in df.columns:
            raise DataValidationError(
                f"❌ Columna {date_column} no existe en DataFrame"
            )
        dates = pd.to_datetime(df[date_column], errors='coerce')
    
    # Validar fechas válidas
    if dates.isnull().all():
        raise DataValidationError(
            f"❌ Columna no contiene fechas válidas"
        )
    
    # Validar rango mínimo
    if min_date and dates.min() < min_date:
        raise DataValidationError(
            f"❌ Fecha mínima {dates.min()} es anterior a {min_date}\n"
            f"   Filtra datos con: df[df.index >= '{min_date}']"
        )
    
    # Validar rango máximo
    if max_date and dates.max() > max_date:
        raise DataValidationError(
            f"❌ Fecha máxima {dates.max()} es posterior a {max_date}\n"
            f"   Filtra datos con: df[df.index <= '{max_date}']"
        )


def validate_numeric_column(
    df: pd.DataFrame,
    column: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_negative: bool = True,
    allow_zero: bool = True
) -> None:
    """
    Validar que columna numérica esté en rango válido
    
    Args:
        df: DataFrame
        column: Nombre de columna a validar
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido
        allow_negative: Si False, rechaza valores negativos
        allow_zero: Si False, rechaza valores cero
    
    Raises:
        DataValidationError: Si columna no existe o no es numérica
        DataQualityError: Si valores fuera de rango
    
    Example:
        >>> # Validar voltaje en rango europeo
        >>> validate_numeric_column(
        ...     df,
        ...     'Voltage',
        ...     min_value=200.0,
        ...     max_value=260.0,
        ...     allow_negative=False
        ... )
    """
    # Validar columna existe
    if column not in df.columns:
        raise DataValidationError(
            f"❌ Columna '{column}' no existe\n"
            f"   Columnas disponibles: {list(df.columns)}"
        )
    
    # Validar tipo numérico
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise DataValidationError(
            f"❌ Columna '{column}' debe ser numérica\n"
            f"   Tipo actual: {df[column].dtype}"
        )
    
    # Obtener valores no-nulos
    values = df[column].dropna()
    
    if len(values) == 0:
        raise DataQualityError(
            f"❌ Columna '{column}' no tiene valores válidos (todos nulos)"
        )
    
    # Validar valores negativos
    if not allow_negative and (values < 0).any():
        negative_count = (values < 0).sum()
        raise DataQualityError(
            f"❌ Columna '{column}' contiene {negative_count} valores negativos\n"
            f"   Rango encontrado: [{values.min():.2f}, {values.max():.2f}]"
        )
    
    # Validar valores cero
    if not allow_zero and (values == 0).any():
        zero_count = (values == 0).sum()
        raise DataQualityError(
            f"❌ Columna '{column}' contiene {zero_count} valores cero\n"
            f"   Esto puede indicar fallo de sensor"
        )
    
    # Validar rango mínimo
    if min_value is not None and values.min() < min_value:
        raise DataQualityError(
            f"❌ Columna '{column}' tiene valores por debajo de mínimo\n"
            f"   Mínimo encontrado: {values.min():.2f}\n"
            f"   Mínimo permitido: {min_value:.2f}"
        )
    
    # Validar rango máximo
    if max_value is not None and values.max() > max_value:
        raise DataQualityError(
            f"❌ Columna '{column}' tiene valores por encima de máximo\n"
            f"   Máximo encontrado: {values.max():.2f}\n"
            f"   Máximo permitido: {max_value:.2f}"
        )


# ============================================================================
# VALIDADORES DE CONFIGURACIÓN
# ============================================================================

def validate_email_config(
    smtp_server: str,
    smtp_port: int,
    email_from: str,
    email_password: str
) -> None:
    """
    Validar configuración de email
    
    Args:
        smtp_server: Servidor SMTP
        smtp_port: Puerto SMTP
        email_from: Dirección email remitente
        email_password: Contraseña email
    
    Raises:
        ConfigurationError: Si configuración inválida
    """
    if not smtp_server or smtp_server.strip() == "":
        raise ConfigurationError("❌ SMTP_SERVER no configurado")
    
    if smtp_port not in [25, 465, 587]:
        raise ConfigurationError(
            f"❌ SMTP_PORT inválido: {smtp_port}\n"
            f"   Puertos comunes: 587 (TLS), 465 (SSL), 25 (sin cifrar)"
        )
    
    if not email_from or '@' not in email_from:
        raise ConfigurationError(
            f"❌ EMAIL_FROM inválido: {email_from}\n"
            f"   Debe ser email válido"
        )
    
    if not email_password or email_password.strip() == "":
        raise ConfigurationError(
            "❌ EMAIL_PASSWORD no configurado\n"
            f"   Agrega EMAIL_PASSWORD='tu_contraseña' en .env"
        )


def validate_model_config(
    contamination: float,
    z_score_threshold: float,
    iqr_multiplier: float
) -> None:
    """
    Validar configuración de modelos de detección
    
    Args:
        contamination: Contamination de Isolation Forest
        z_score_threshold: Umbral Z-Score
        iqr_multiplier: Multiplicador IQR
    
    Raises:
        ConfigurationError: Si parámetros inválidos
    """
    if not (0.0 < contamination < 0.5):
        raise ConfigurationError(
            f"❌ contamination debe estar entre 0.0 y 0.5\n"
            f"   Valor recibido: {contamination}"
        )
    
    if z_score_threshold < 1.0 or z_score_threshold > 5.0:
        raise ConfigurationError(
            f"❌ z_score_threshold debe estar entre 1.0 y 5.0\n"
            f"   Valor recibido: {z_score_threshold}\n"
            f"   Recomendado: 3.0"
        )
    
    if iqr_multiplier < 1.0 or iqr_multiplier > 3.0:
        raise ConfigurationError(
            f"❌ iqr_multiplier debe estar entre 1.0 y 3.0\n"
            f"   Valor recibido: {iqr_multiplier}\n"
            f"   Recomendado: 1.5"
        )


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_validation_summary(df: pd.DataFrame) -> dict:
    """
    Obtener resumen de validación de DataFrame
    
    Args:
        df: DataFrame a analizar
    
    Returns:
        Diccionario con métricas de calidad
    
    Example:
        >>> summary = get_validation_summary(df)
        >>> print(summary['null_percentage'])
        1.4
    """
    total_cells = len(df) * len(df.columns)
    null_count = df.isnull().sum().sum()
    
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'total_cells': total_cells,
        'null_count': null_count,
        'null_percentage': (null_count / total_cells * 100) if total_cells > 0 else 0,
        'has_datetime_index': isinstance(df.index, pd.DatetimeIndex),
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }


if __name__ == "__main__":
    """Tests de validadores"""
    
    print("✅ Tests de Validadores DomusAI\n")
    
    # Test 1: Validar CSV path
    try:
        csv_path = validate_csv_path("data/Dataset_clean_test.csv", must_exist=False)
        print(f"✅ CSV path válido: {csv_path}")
    except Exception as e:
        print(f"❌ {e}")
    
    # Test 2: Crear DataFrame de prueba
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    df_test = pd.DataFrame({
        'Global_active_power': np.random.uniform(1, 5, 100),
        'Voltage': np.random.uniform(220, 240, 100)
    }, index=dates)
    
    print(f"\n📊 DataFrame de prueba creado: {len(df_test)} filas")
    
    # Test 3: Validar DataFrame
    try:
        validate_dataframe(
            df_test,
            required_columns=['Global_active_power', 'Voltage'],
            min_rows=50
        )
        print("✅ DataFrame válido")
    except Exception as e:
        print(f"❌ {e}")
    
    # Test 4: Validar datetime index
    try:
        validate_datetime_index(df_test)
        print("✅ DatetimeIndex válido")
    except Exception as e:
        print(f"❌ {e}")
    
    # Test 5: Resumen de validación
    summary = get_validation_summary(df_test)
    print(f"\n📈 Resumen de validación:")
    print(f"   Filas: {summary['rows']}")
    print(f"   Columnas: {summary['columns']}")
    print(f"   Nulos: {summary['null_percentage']:.2f}%")
    print(f"   Memoria: {summary['memory_usage_mb']:.2f} MB")
