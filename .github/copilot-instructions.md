# DomusAI - Sistema de Monitoreo y Predicción de Consumo Energético

## Project Status: 95% Complete (v0.95) - Production Ready

**Sistema completo** de análisis energético con ML, detección de anomalías, reportes PDF/HTML y automatización por email. Pendiente: Integración IoT con ESP32 (Sprint 8).

## Core Architecture

### Data Flow (End-to-End Pipeline)
```
CSV/ESP32 → data_cleaning.py → Clean Dataset
    ↓
EnergyPredictor → Prophet/ARIMA forecasts (1h-30d)
    ↓
AnomalyDetector → Multi-method consensus (5 algorithms)
    ↓
ReportGenerator → HTML/PDF con gráficos matplotlib
    ↓
EmailReporter → SMTP automático (mensual + alertas críticas)
```

### Key Modules (src/)

**predictor.py** (1,561 líneas) - Motor de predicción
```python
from src.predictor import EnergyPredictor

# Prophet es el modelo principal (mejor balance precisión/velocidad)
predictor = EnergyPredictor('data/Dataset_clean_test.csv')
predictor.train_prophet_model()
pred = predictor.predict(horizon_days=7, model='prophet')
# Retorna: {'predictions': [...], 'statistics': {...}, 'confidence_intervals': {...}}
```
- **Prophet**: Modelo principal (MAPE 12.3%, 35s entrenamiento)
- **ARIMA**: Validación cruzada (MAPE 13.9%, 42s)
- **Prophet Enhanced**: MCMC sampling (MAPE 11.1%, 3h)
- **Optimización crítica**: `uncertainty_samples=100` (reducido de 1000 → ahorra 1.8 GB RAM)

**anomalies.py** (1,060 líneas) - Detección multi-método
```python
from src.anomalies import AnomalyDetector

detector = AnomalyDetector(method='isolation_forest')
results = detector.detect(df, method='all', consensus_threshold=3, classify=True)
# Retorna: {'anomalies': [], 'consensus_anomalies': [], 'classified_anomalies': {}, 'alerts': []}
```
- **5 métodos**: IQR, Z-Score, Isolation Forest, Moving Average, Prediction-Based
- **Consenso**: ≥3 métodos = alta confianza (reduce falsos positivos)
- **Clasificación**: 4 tipos (consumo_alto, consumo_bajo, temporal, fallo_sensor)
- **Alertas**: Severidad automática (critical/medium/low) con acciones recomendadas

**reporting.py** (968 líneas) - Generación de reportes
```python
from src.reporting import generate_monthly_report_with_pdf

html_path, pdf_path = generate_monthly_report_with_pdf(
    data_path='data/Dataset_clean_test.csv',
    month=6, year=2007
)
# Genera: reporte_2007-06_TIMESTAMP.html + .pdf
```
- **Templates Jinja2**: `reports/templates/monthly_report.html`
- **Gráficos embebidos**: matplotlib → PNG base64 en HTML
- **Recomendaciones**: Sistema inteligente basado en patrones (ej: "Pico nocturno 40% sobre promedio")
- **PDF**: xhtml2pdf para conversión HTML→PDF (340 KB típico)

**email_sender.py** (702 líneas) - Automatización SMTP
```python
from src.reporting import generate_and_send_monthly_report

result = generate_and_send_monthly_report(
    data_path='data/Dataset_clean_test.csv',
    month=6, year=2007,
    include_pdf=True,
    auto_send=True  # Pipeline completo: genera + envía
)
# result: {'email_sent': True, 'html_path': ..., 'pdf_path': ..., 'email_recipients': [...]}
```
- **Templates**: `reports/email_templates/monthly_report_email.html` (330 líneas)
- **SMTP**: Gmail con TLS (configuración en `.env`)
- **Adjuntos**: PDFs hasta 25 MB, multi-destinatario
- **Logging**: UTF-8 compatible Windows (`logs/email_sender.log`)

**config.py** (400+ líneas) - Configuración centralizada
```python
from src.config import PATHS, ML_CONFIG, EMAIL_CONFIG, DB_CONFIG, ENERGY

# Ejemplo: Usar paths centralizados
df = pd.read_csv(PATHS.CLEAN_CSV)  # data/Dataset_clean_test.csv
model_path = PATHS.PROPHET_MODEL    # models/prophet_production.pkl

# Constantes de dominio energético (España)
ENERGY.VOLTAGE_NOMINAL  # 230V
ENERGY.CONSUMPTION_NORMAL  # 3.0 kW
ENERGY.PRICE_PER_KWH_PEAK  # 0.25 €/kWh
```
- **PathConfig**: Rutas centralizadas (data/, reports/, models/, logs/)
- **MLConfig**: Hiperparámetros (Prophet, ARIMA, Isolation Forest)
- **DatabaseConfig**: Railway MySQL credentials (`.env` requerido)
- **EnergyConstants**: Dominio español (230V±10%, precios IDAE)

### Synthetic Data Generator (Crítico para Testing)

**generate_consumption_data.py** (949 líneas) - Generador ultra-realista español
```bash
# Generar 4 años de datos (2.1M registros, 130 MB)
python synthetic_data_generator/generate_consumption_data.py --days 1460 --profile medium --start-date 2025-10-30

# Output: synthetic_1460days_TIMESTAMP.csv
# Promedio: ~0.44 kW (realista para hogar español 3-4 personas según IDAE)
```
**Patrones implementados**:
- **Vacaciones españolas**: Agosto (100% fuera), Navidad/Semana Santa (50% fuera), puentes (70% fuera)
- **Consumo ajustado a IDAE**: `medium` → 3,500-4,500 kWh/año = 0.40-0.52 kW promedio
- **Estacionalidad**: HVAC invierno/verano, comidas horario español (8h, 14h, 21h)
- **Sub-metering coherente**: Cocina (25%), Lavandería (8%), HVAC (30%)
- **Validaciones físicas**: Ley de Ohm, voltaje 225-238V, power factor 0.85-0.95

**CRÍTICO**: Datos sintéticos calibrados tras 3 iteraciones para match con consumos reales españoles (usuario reportó feb 2028 con 0.97 kW → ajustado a 0.47 kW).

## Essential Coding Patterns

### Type Safety (Pylance Strict Mode)
```python
# ❌ EVITAR: Pandas index ambiguo
df.index.year  # Error: Series[Any] no tiene .year

# ✅ CORRECTO: Cast explícito
idx = pd.DatetimeIndex(df.index)
idx.year, idx.month, idx.hour  # OK: DatetimeIndex tiene atributos temporales

# ✅ CORRECTO: .to_numpy() en lugar de .values
plt.plot(df['col'].to_numpy())  # Preferred para matplotlib
```

### Logging con UTF-8 (Windows PowerShell Compatible)
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/module.log', encoding='utf-8'),  # ← encoding crítico
        logging.StreamHandler()
    ]
)
logger.info("✅ Reporte generado exitosamente")  # Emojis funcionan en logs
```

### Error Handling con Contexto
```python
try:
    model = Prophet(uncertainty_samples=100).fit(df)
except Exception as e:
    logger.error(f"❌ Error entrenando Prophet: {e}")
    logger.error(f"   Dataset shape: {df.shape}")
    logger.error(f"   Memory usage: {df.memory_usage().sum() / 1e6:.1f} MB")
    raise  # Re-raise con contexto en logs
```

### Memory Optimization (Prophet en datasets grandes)
```python
# Problema: MemoryError con 256k registros (1.91 GB arrays)
# Solución 1: Reducir uncertainty_samples durante entrenamiento
model = Prophet(
    uncertainty_samples=100,  # Default: 1000 (ahorra 1.72 GB)
    seasonality_mode='multiplicative',
    changepoint_prior_scale=0.05
)

# Solución 2: Sin IC durante validación
temp_model = Prophet(uncertainty_samples=0).fit(train_data)
forecast = temp_model.predict(test_data)  # Sin intervalos de confianza
```

### Output Formatting Conventions
```python
# Siempre usar emojis para estados
logger.info("🔄 Procesando dataset...")
logger.info("✅ Dataset procesado correctamente")
logger.warning("⚠️ Valores nulos detectados: {count}")
logger.error("❌ Error crítico en módulo XYZ")

# Números con separador de miles
print(f"📊 Registros procesados: {len(df):,}")  # 260,640 en lugar de 260640
print(f"💰 Coste estimado: {cost:,.2f} €")     # 1,234.56 €
```

## Domain-Specific Knowledge

### Spanish Energy Patterns (IDAE Data)
- **Hogar pequeño** (1-2p): 2,500-3,000 kWh/año → 0.28-0.34 kW promedio
- **Hogar mediano** (3-4p): 3,500-4,500 kWh/año → 0.40-0.52 kW promedio ⭐ TARGET
- **Hogar grande** (5+p): 5,000-7,000 kWh/año → 0.57-0.80 kW promedio

**Horarios pico** (patrón español):
- Mañana: 07:00-09:00 (duchas, desayuno) → 1.5-3.5 kW
- Noche: 18:00-22:00 (cocina, TV, lavadora) → 2.0-4.5 kW
- Valle: 00:00-06:00 (standby, nevera) → 0.15-0.30 kW

**Voltaje europeo**: 230V ±10% (207-253V válido, >260V crítico)

### Data Validation Rules
```python
# Sub-metering debe sumar ≤ 75% del total (resto = unmeasured loads)
total = df['Global_active_power']
sub_total = df[['Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']].sum(axis=1)
assert (sub_total <= total * 0.75).all(), "Sub-metering incoherente"

# Ley de Ohm: I = P / V × 1000
calculated_I = (df['Global_active_power'] * 1000) / df['Voltage']
error = abs(calculated_I - df['Global_intensity']).mean()
assert error < 0.5, f"Ley de Ohm violada: error {error:.2f}A"
```

## Critical Commands

### Setup & Configuration
```bash
# 1. Activar entorno virtual
.venv\Scripts\Activate.ps1

# 2. Instalar dependencias (25+ paquetes)
pip install -r requirements.txt

# 3. Validar configuración
python src/config.py  # Imprime resumen + valida paths

# 4. Configurar .env para emails/database
cp .env.example .env  # Editar con credenciales SMTP + Railway MySQL
```

### Testing & Validation
```bash
# Test suite completa (Sprint 7)
python tests/test_anomalies_railway.py      # Detección de anomalías
python tests/test_predictor_railway.py      # Predicciones Prophet
python tests/test_reporting_railway.py      # Reportes HTML/PDF
python tests/test_email_templates.py        # Templates de email

# Generación de datos sintéticos
cd synthetic_data_generator
python generate_consumption_data.py --days 30 --validate
```

### Production Pipeline
```bash
# Pipeline completo: datos → predicción → anomalías → reporte → email
python -c "
from src.reporting import generate_and_send_monthly_report
result = generate_and_send_monthly_report(
    data_path='data/Dataset_clean_test.csv',
    month=6, year=2007,
    include_pdf=True,
    auto_send=True
)
print(f'✅ Email enviado: {result[\"email_sent\"]}')
"
```

## Railway MySQL Integration (Sprint 8 - Pending)

**Database Schema** (simplificado para ESP32):
```sql
CREATE TABLE energy_readings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME NOT NULL,
    global_active_power DECIMAL(8,3),
    voltage DECIMAL(6,2),
    global_intensity DECIMAL(6,3),
    sub_metering_1 DECIMAL(8,3),
    sub_metering_2 DECIMAL(8,3),
    sub_metering_3 DECIMAL(8,3),
    INDEX idx_timestamp (timestamp)
);
```

**Setup**:
```bash
# 1. Configurar .env con credenciales Railway
MYSQL_HOST=your-railway-host.railway.app
MYSQL_PORT=3306
MYSQL_DATABASE=railway
MYSQL_USER=root
MYSQL_PASSWORD=your-password

# 2. Crear schema (one-time)
python src/setup_railway_db.py

# 3. Insertar datos sintéticos para testing
python synthetic_data_generator/examples/insert_to_railway.py
```

**Connection Pattern**:
```python
from src.config import DB_CONFIG
import mysql.connector

conn = mysql.connector.connect(**DB_CONFIG.connection_params)
cursor = conn.cursor()
cursor.execute("SELECT * FROM energy_readings ORDER BY timestamp DESC LIMIT 1440")
# Último día de datos (1440 minutos)
```

## Team Collaboration Notes

**Division**: Python/AI dev (este código) + Electronics partner (ESP32 MQTT)

**Next Sprint (8)**: 
- ESP32 → INSERT directo a Railway MySQL
- Python → SELECT de Railway → Auto-train → Anomalies → Reports
- Scheduler automático: Diario (8 AM), Semanal (Lunes 9 AM), Mensual (día 1, 10 AM)

**Code Reviews**: Verificar type-safety (Pylance strict), logging UTF-8, memory optimization en Prophet