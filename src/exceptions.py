"""
🚨 DomusAI - Excepciones Personalizadas

Define excepciones específicas del dominio para mejor manejo de errores
y mensajes más claros para el usuario.
"""


class DomusAIError(Exception):
    """
    Excepción base para todas las excepciones de DomusAI
    
    Todas las excepciones personalizadas heredan de esta clase
    para facilitar el manejo con try-except genérico.
    """
    pass


# ============================================================================
# EXCEPCIONES DE DATOS
# ============================================================================

class DataValidationError(DomusAIError):
    """
    Error en validación de datos de entrada
    
    Ejemplos:
    - Archivo CSV con formato incorrecto
    - Columnas faltantes en DataFrame
    - Tipos de datos incorrectos
    - Fechas fuera de rango esperado
    """
    pass


class InsufficientDataError(DomusAIError):
    """
    Datos insuficientes para realizar análisis
    
    Ejemplos:
    - Menos de 100 registros para entrenamiento
    - Periodo muy corto para detectar estacionalidad
    - Dataset vacío después de limpieza
    """
    pass


class DataQualityError(DomusAIError):
    """
    Calidad de datos por debajo del umbral aceptable
    
    Ejemplos:
    - Más del 50% de valores nulos
    - Datos claramente erróneos (voltaje = 0)
    - Timestamps duplicados o fuera de orden
    """
    pass


# ============================================================================
# EXCEPCIONES DE MODELOS ML
# ============================================================================

class ModelNotTrainedError(DomusAIError):
    """
    Intento de usar modelo que no ha sido entrenado
    
    Ejemplo:
    >>> predictor = EnergyPredictor()
    >>> predictor.predict(7)  # ❌ Modelo no entrenado
    ModelNotTrainedError: Ejecuta train() primero
    """
    pass


class ModelTrainingError(DomusAIError):
    """
    Error durante el entrenamiento del modelo
    
    Ejemplos:
    - No convergencia de Prophet
    - ARIMA no encuentra parámetros válidos
    - Datos no estacionarios para ARIMA
    """
    pass


class PredictionError(DomusAIError):
    """
    Error al generar predicciones
    
    Ejemplos:
    - Horizonte de predicción demasiado largo
    - Datos de entrada fuera de distribución
    - Modelo corrupto o inválido
    """
    pass


# ============================================================================
# EXCEPCIONES DE ANOMALÍAS
# ============================================================================

class AnomalyDetectionError(DomusAIError):
    """
    Error en el proceso de detección de anomalías
    
    Ejemplos:
    - Método de detección no disponible
    - Parámetros inválidos para detector
    - Fallo en Isolation Forest
    """
    pass


class NoAnomaliesFoundError(DomusAIError):
    """
    No se encontraron anomalías en el periodo analizado
    
    Nota: Esta NO es un error crítico, puede ser el resultado esperado
    en periodos de consumo normal.
    """
    pass


# ============================================================================
# EXCEPCIONES DE REPORTES
# ============================================================================

class ReportGenerationError(DomusAIError):
    """
    Error al generar reportes HTML/PDF
    
    Ejemplos:
    - Template Jinja2 no encontrado
    - Error en generación de gráficos
    - xhtml2pdf falla en conversión PDF
    """
    pass


class TemplateNotFoundError(ReportGenerationError):
    """
    Template de reporte no encontrado
    
    Ejemplo:
    >>> generator.generate_report('nonexistent.html')
    TemplateNotFoundError: Template 'nonexistent.html' no existe
    """
    pass


# ============================================================================
# EXCEPCIONES DE EMAIL
# ============================================================================

class EmailDeliveryError(DomusAIError):
    """
    Error al enviar email
    
    Ejemplos:
    - Credenciales SMTP incorrectas
    - Servidor no disponible
    - Timeout en conexión
    - Attachment demasiado grande
    """
    pass


class EmailConfigurationError(DomusAIError):
    """
    Configuración de email incorrecta o faltante
    
    Ejemplos:
    - Variables de entorno no definidas
    - EMAIL_PASSWORD no configurado en .env
    - SMTP_SERVER inválido
    """
    pass


class AttachmentTooLargeError(EmailDeliveryError):
    """
    Archivo adjunto excede límite de tamaño
    
    Gmail límite: 25 MB
    """
    pass


# ============================================================================
# EXCEPCIONES DE IoT / MQTT (Sprint 8)
# ============================================================================

class MQTTConnectionError(DomusAIError):
    """
    Error de conexión con broker MQTT
    
    Ejemplos:
    - Mosquitto no está ejecutándose
    - Puerto bloqueado por firewall
    - Credenciales incorrectas
    """
    pass


class MQTTPublishError(DomusAIError):
    """
    Error al publicar mensaje en topic MQTT
    
    Ejemplos:
    - Desconexión durante publish
    - QoS no soportado
    - Mensaje demasiado grande
    """
    pass


class SensorReadError(DomusAIError):
    """
    Error al leer datos del sensor (ESP32 + ACS712)
    
    Ejemplos:
    - Sensor desconectado
    - Voltaje fuera de rango del ADC
    - Lectura analógica errónea
    """
    pass


class DatabaseError(DomusAIError):
    """
    Error en operaciones de base de datos (SQLite/InfluxDB/MySQL)
    
    Ejemplos:
    - DB bloqueada por otro proceso
    - Disco lleno
    - Schema inválido
    """
    pass


class DatabaseConnectionError(DatabaseError):
    """
    Error al conectar con la base de datos
    
    Ejemplos:
    - Host no alcanzable
    - Credenciales inválidas
    - Puerto bloqueado
    - Timeout de conexión
    """
    pass


class DatabaseSetupError(DatabaseError):
    """
    Error durante el setup/inicialización de la base de datos
    
    Ejemplos:
    - Error creando tablas
    - Error creando índices
    - Schema SQL inválido
    - Permisos insuficientes
    """
    pass


class DatabaseQueryError(DatabaseError):
    """
    Error ejecutando queries en la base de datos
    
    Ejemplos:
    - Query SQL malformado
    - Constraint violation
    - Foreign key error
    - Timeout de query
    """
    pass


# ============================================================================
# EXCEPCIONES DE CONFIGURACIÓN
# ============================================================================

class ConfigurationError(DomusAIError):
    """
    Error en configuración del sistema
    
    Ejemplos:
    - config.py corrupto
    - Paths inválidos
    - Variables requeridas faltantes
    """
    pass


class EnvironmentNotValidatedError(DomusAIError):
    """
    Entorno no validado antes de ejecutar operación
    
    Ejemplo:
    >>> from config import validate_environment
    >>> if not validate_environment():
    ...     raise EnvironmentNotValidatedError()
    """
    pass


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def format_error_message(error: Exception, context: str = "") -> str:
    """
    Formatear mensaje de error con contexto adicional
    
    Args:
        error: Excepción capturada
        context: Contexto adicional (ej: nombre de función)
    
    Returns:
        Mensaje formateado con emoji y contexto
    
    Example:
        >>> try:
        ...     model.predict()
        ... except ModelNotTrainedError as e:
        ...     print(format_error_message(e, "predict_consumption"))
        ❌ Error en predict_consumption: Modelo no entrenado
    """
    error_type = type(error).__name__
    emoji = "❌"
    
    # Emojis específicos por tipo de error
    if isinstance(error, DataValidationError):
        emoji = "📊❌"
    elif isinstance(error, ModelNotTrainedError):
        emoji = "🤖❌"
    elif isinstance(error, EmailDeliveryError):
        emoji = "📧❌"
    elif isinstance(error, MQTTConnectionError):
        emoji = "🔌❌"
    elif isinstance(error, AnomalyDetectionError):
        emoji = "🚨❌"
    
    if context:
        return f"{emoji} Error en {context} ({error_type}): {str(error)}"
    else:
        return f"{emoji} {error_type}: {str(error)}"


def is_critical_error(error: Exception) -> bool:
    """
    Determinar si un error es crítico y requiere detener ejecución
    
    Args:
        error: Excepción a evaluar
    
    Returns:
        True si error es crítico, False si es recuperable
    
    Example:
        >>> try:
        ...     send_email()
        ... except EmailDeliveryError as e:
        ...     if is_critical_error(e):
        ...         raise  # Re-raise si es crítico
        ...     else:
        ...         logger.warning(f"Email falló pero continuando: {e}")
    """
    # Errores críticos que deben detener ejecución
    critical_errors = (
        ConfigurationError,
        EnvironmentNotValidatedError,
        DatabaseError,
        DataQualityError,
    )
    
    # Errores no críticos (recuperables)
    recoverable_errors = (
        EmailDeliveryError,  # Puede reintentarse
        NoAnomaliesFoundError,  # Es resultado válido
        MQTTPublishError,  # MQTT puede reconectarse
    )
    
    return isinstance(error, critical_errors)


if __name__ == "__main__":
    """Ejemplos de uso de excepciones"""
    
    print("🚨 Ejemplos de Excepciones DomusAI\n")
    
    # Ejemplo 1: DataValidationError
    try:
        raise DataValidationError("Columna 'Global_active_power' faltante en CSV")
    except DomusAIError as e:
        print(format_error_message(e, "load_data"))
    
    # Ejemplo 2: ModelNotTrainedError
    try:
        raise ModelNotTrainedError("Ejecuta train() antes de predict()")
    except DomusAIError as e:
        print(format_error_message(e, "predict"))
    
    # Ejemplo 3: EmailDeliveryError (no crítico)
    try:
        raise EmailDeliveryError("SMTP timeout después de 30s")
    except DomusAIError as e:
        print(format_error_message(e, "send_report"))
        if not is_critical_error(e):
            print("   ℹ️  Error recuperable - reintentando...")
    
    # Ejemplo 4: Captura genérica con isinstance
    try:
        raise AnomalyDetectionError("Isolation Forest falló - contamination=0.5 inválido")
    except DomusAIError as e:
        if isinstance(e, AnomalyDetectionError):
            print(f"\n🚨 Detectado error de anomalías: {e}")
            print("   Solución: Usar contamination entre 0.0 y 0.5")
