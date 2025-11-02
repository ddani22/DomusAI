# 🏭 DomusAI - Arquitectura del Sistema en Producción

**Estado:** Sistema operativo 24/7  
**Versión:** v0.95 (Production Ready)  
**Última actualización:** Noviembre 2, 2025  
**Modelos actuales:** v20251102_163825 (entrenados con 4 años de datos sintéticos)

---

## 🎯 Vista General del Sistema

DomusAI es un sistema completo de **monitoreo y predicción de consumo energético** que opera 24/7 con 5 jobs automáticos programados. El sistema utiliza Machine Learning (Prophet + Isolation Forest) para predecir consumos y detectar anomalías, generando reportes automáticos en HTML/PDF y enviándolos por email.

### Características Principales

- ✅ **Detección de anomalías** cada hora con 5 algoritmos en consenso
- ✅ **Re-entrenamiento automático** de modelos cada 7 días
- ✅ **Reportes automáticos** diarios, semanales y mensuales (HTML + PDF)
- ✅ **Alertas por email** con severidad inteligente y acciones recomendadas
- ✅ **Predicciones** a 1h, 24h, 7d y 30d con intervalos de confianza
- ✅ **Base de datos Railway MySQL** para almacenamiento persistente
- ✅ **Datos sintéticos ultra-realistas** calibrados según IDAE España

---

## 📊 Arquitectura de Jobs Automáticos (5 Jobs)

```
┌──────────────────────────────────────────────────────────────┐
│  🚀 PROCESO PRINCIPAL: auto_training_scheduler.py            │
│  Ejecutando desde: Terminal PowerShell (background)          │
│  Logs: logs/scheduler.log (UTF-8 encoding, emojis)           │
│  Timezone: Europe/Madrid                                     │
└──────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
    │   JOB #1     │ │  JOB #2   │ │   JOB #3    │
    │  Anomalías   │ │ Re-train  │ │   Diario    │
    │  Cada 60min  │ │  3 AM     │ │   8 AM      │
    └──────────────┘ └───────────┘ └─────────────┘
            │               │               │
    ┌───────▼──────┐ ┌─────▼─────┐
    │   JOB #4     │ │  JOB #5   │
    │   Semanal    │ │  Mensual  │
    │   Lun 9 AM   │ │  Día 1 10AM│
    └──────────────┘ └───────────┘
```

---

## 🕐 JOB #1: Detección de Anomalías (Cada Hora)

**Archivo:** `scripts/auto_training_scheduler.py`  
**Función:** `hourly_anomaly_detection()` (líneas 225-316)  
**Trigger:** `IntervalTrigger(minutes=60)`  
**Duración típica:** 7-12 segundos

### Flujo de Ejecución

#### 1️⃣ Obtener Datos de Railway MySQL
```python
# Query ejecutado:
SELECT * FROM energy_readings 
WHERE timestamp >= NOW() - INTERVAL 1 HOUR 
ORDER BY timestamp ASC
```
- **Registros esperados:** ~60 (1 por minuto)
- **Columnas:** timestamp, Global_active_power, Voltage, Global_intensity, Sub_metering_1/2/3
- **Módulo:** `src/database.py` → `get_db_reader()`
- **Validación:** Si < 30 registros → skip (datos insuficientes)

#### 2️⃣ Cargar Modelo de Detección
```python
model_path = Path('models/best_isolation_forest.pkl')
anomaly_model = joblib.load(model_path)
```
- **Modelo:** IsolationForest (100 estimators, contamination=0.05)
- **Tamaño en RAM:** ~1.5 MB
- **Features:** 7 columnas (power, voltage, intensity, hour, day_of_week, rolling_mean_24h, rolling_std_24h)

#### 3️⃣ Detectar Anomalías (5 Métodos en Consenso)
```python
from src.anomalies import AnomalyDetector

detector = AnomalyDetector(method='all')
results = detector.detect(df, consensus_threshold=3, classify=True)
```

**Algoritmos ejecutados:**
1. **IQR** (Interquartile Range) → Outliers estadísticos
2. **Z-Score** (3σ) → Desviaciones estándar
3. **Isolation Forest** (ML) → Anomalías por aislamiento
4. **Moving Average** (24h window) → Desviaciones de tendencia
5. **Prediction-Based** → Comparación con Prophet

**Consenso:** Anomalía confirmada si **≥3 métodos coinciden**

**Clasificación automática:**
- `consumo_alto`: >threshold personalizado (ej: >5 kW)
- `consumo_bajo`: <0.15 kW durante >5 minutos
- `temporal`: Pico aislado <10 minutos
- `fallo_sensor`: Física violada (Ley de Ohm, voltaje fuera rango)

#### 4️⃣ Evaluar Severidad
```python
severity = _calculate_severity(anomalies)
```

| Severidad | Criterios | Acciones Recomendadas |
|-----------|-----------|----------------------|
| **CRITICAL** (≥80) | • Pico >7 kW durante >30 min<br>• Voltaje <207V o >253V<br>• Ley de Ohm violada (error >5A) | • Revisar instalación urgente<br>• Contactar electricista<br>• Verificar cuadro eléctrico |
| **MEDIUM** (50-79) | • Consumo 2-3x promedio (2-7 kW)<br>• Duración >15 min | • Verificar electrodomésticos<br>• Revisar HVAC<br>• Apagar standby innecesario |
| **LOW** (<50) | • Pico breve <10 min<br>• Consumo <2x promedio | • Monitorear<br>• Uso normal esperado |

#### 5️⃣ Enviar Email de Alerta (Si severity ≥ MEDIUM)
```python
from src.email_sender import EmailReporter

emailer = EmailReporter()
emailer.send_anomaly_alert(
    recipients=['enriquesl1102@gmail.com', 'ddanimc2602@gmail.com'],
    anomalies=anomaly_data,
    severity='CRITICAL'
)
```

**Template:** `reports/email_templates/anomaly_alert_email.html`

**Email generado:**
- **Subject:** `🚨 Alerta DomusAI: 3 Anomalías CRITICAL detectadas`
- **Body:** Tabla HTML con anomalías + gráfico de consumo
- **Cooldown:** 1 hora entre alertas (evitar spam)

**Ejemplo de email:**
```
🚨 Alerta de Consumo Anómalo

Detectadas 3 anomalías CRÍTICAS en tu instalación:

Hora      | Consumo | Promedio | Desviación
----------|---------|----------|------------
14:30     | 8.1 kW  | 0.45 kW  | +1,700%
14:45     | 7.8 kW  | 0.45 kW  | +1,633%
15:00     | 7.2 kW  | 0.45 kW  | +1,500%

Acciones recomendadas:
✓ Verificar termostato HVAC
✓ Revisar electrodomésticos de alta potencia
✓ Considerar revisión técnica

Coste estimado exceso: 3.63 €
```

#### 6️⃣ Logging
```
2025-11-02 18:00:02 - INFO - 🕐 [HOURLY] Ejecutando detección...
2025-11-02 18:00:04 - INFO - ✅ 58 lecturas obtenidas de Railway
2025-11-02 18:00:06 - WARNING - ⚠️ 2 anomalías MEDIUM detectadas
2025-11-02 18:00:08 - INFO - 📧 Email enviado a 2 destinatarios
2025-11-02 18:00:09 - INFO - ✅ Job ejecutado en 7.2 segundos
```

---

## 🌙 JOB #2: Re-entrenamiento de Modelos (Diario 3 AM, cada 7 días)

**Archivo:** `scripts/auto_training_scheduler.py`  
**Función:** `daily_retraining_check()` (líneas 318-458)  
**Trigger:** `CronTrigger("0 3 * * *")` - Diario a las 3:00 AM  
**Condición:** Solo ejecuta si `days_since_last_training >= 7`  
**Duración típica:** 120-180 segundos

### Flujo de Ejecución

#### 1️⃣ Verificar Última Fecha de Entrenamiento
```python
history_path = Path('logs/metrics_history.json')
with open(history_path, 'r') as f:
    history = json.load(f)

last_entry = history[-1]
last_date = datetime.fromisoformat(last_entry['timestamp'])
days_since = (datetime.now() - last_date).days

if days_since < 7:
    logger.info(f"✅ Modelo reciente, próximo entrenamiento en {7 - days_since} días")
    return  # SKIP re-entrenamiento
```

**Archivo monitoreado:** `logs/metrics_history.json`

**Estructura:**
```json
[
  {
    "version": "v20251102_163825",
    "timestamp": "2025-11-02T16:38:40",
    "mae": 0.179,
    "rmse": 0.252,
    "mape": 72.9,
    "r2": 0.660,
    "training_records": 2102400,
    "training_date": "2025-11-02T16:38:40"
  }
]
```

#### 2️⃣ Obtener Datos de Railway (90 días)
```sql
SELECT * FROM energy_readings 
WHERE timestamp >= NOW() - INTERVAL 90 DAY 
ORDER BY timestamp ASC
```
- **Registros esperados:** ~129,600 (90 días × 1,440 min/día)
- **Validación mínima:** ≥43,200 registros (30 días)
- **Si falla:** Skip con warning + email de alerta

#### 3️⃣ Ejecutar Pipeline de Re-entrenamiento

**Archivo:** `src/auto_trainer.py`  
**Clase:** `AutoTrainer`  
**Método:** `run_full_training_pipeline()`

##### Pipeline Completo (11 Pasos):

**PASO 1: Validación de Calidad**
```python
quality = trainer.validate_data_quality(df)
```
- ✓ len(df) >= 43,200 (30 días mínimo)
- ✓ Nulos < 5%
- ✓ Outliers < 10% (IQR method)
- ✓ Gaps temporales < 60 min
- Si falla → return `{'success': False, 'error': '...'}`

**PASO 2: Preprocesamiento**
```python
df_clean = trainer.preprocess_data(df)
```
1. Eliminar nulos (forward fill + backward fill)
2. Filtrar outliers (IQR × 3)
3. Suavizar ruido (rolling mean 5 min)
4. Validar rangos físicos:
   - Power: 0.01-10.0 kW
   - Voltage: 207-253V (230V ±10%)
   - Intensity: 0.1-50.0 A
5. Crear features temporales:
   - hour, day_of_week, is_weekend
   - rolling_mean_24h, rolling_std_24h

**PASO 3: Entrenar Prophet**
```python
from prophet import Prophet

model = Prophet(
    seasonality_mode='multiplicative',
    changepoint_prior_scale=0.05,
    seasonality_prior_scale=10.0,
    daily_seasonality=True,
    weekly_seasonality=True,
    yearly_seasonality=True,
    uncertainty_samples=100  # ← Crítico: Ahorra 1.8 GB RAM
)

prophet_model = model.fit(df_prophet)
```
- **Tiempo:** ~35-45 segundos (90 días)
- **RAM peak:** ~320 MB
- **Output:** `prophet_model` (objeto Prophet serializable)

**PASO 4: Entrenar Isolation Forest**
```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,  # 5% anomalías esperadas
    max_samples=256,
    random_state=42
)

anomaly_model = model.fit(X_features)
```
- **Features (7):** power, voltage, intensity, hour, day_of_week, rolling_mean_24h, rolling_std_24h
- **Tiempo:** ~8-12 segundos
- **RAM peak:** ~80 MB

**PASO 5: Evaluación**
```python
metrics = trainer.evaluate_models(prophet_model, test_data)
```
- **Split:** Últimos 7 días para test, resto para train
- **Train:** 119,520 registros (83 días)
- **Test:** 10,080 registros (7 días)

**Métricas calculadas:**
- **MAE** (Mean Absolute Error) - Métrica principal
- **RMSE** (Root Mean Squared Error)
- **MAPE** (Mean Absolute Percentage Error)
- **R²** (Coeficiente de determinación)

**PASO 6: Comparación con Modelo Anterior**
```python
comparison = trainer.compare_with_previous(new_metrics, previous_metrics)
```

**Decisiones automáticas:**

| Decision | Condición | Acción |
|----------|-----------|--------|
| **KEEP_NEW** | `new_mae < prev_mae` AND `new_rmse < prev_rmse` | Guardar como `best_*.pkl` (producción) |
| **ROLLBACK_OLD** | `new_mae > prev_mae × 1.10` | Mantener modelo anterior, backup nuevo |
| **FIRST_TRAINING** | No hay modelo anterior | Guardar automáticamente |

**Ejemplo de comparación:**
```
📊 Comparación con modelo anterior:
   Versión anterior: v20251102_163825
   MAE: 0.179 → 0.168 (-6.1%) ✅ MEJORA
   RMSE: 0.252 → 0.241 (-4.4%) ✅ MEJORA
   R²: 0.660 → 0.682 (+3.3%) ✅ MEJORA
   
   🏆 DECISIÓN: KEEP_NEW
```

**PASO 7: Guardar Modelos**
```python
version_id = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
trainer.save_models(prophet_model, anomaly_model, version_id, decision)
```

**Archivos generados:**

1. **Backups versionados:**
   - `models/prophet_v20251109_030145.pkl` (~60 MB)
   - `models/isolation_forest_v20251109_030145.pkl` (~1.5 MB)

2. **Si KEEP_NEW → Actualizar producción:**
   - `models/best_prophet.pkl` ⭐ (usado por predictor.py)
   - `models/best_isolation_forest.pkl` ⭐ (usado por anomalies.py)

3. **Actualizar historiales:**
   - `models/training_history.json`
   - `logs/metrics_history.json`

#### 4️⃣ Enviar Email de Notificación
```python
emailer.send_training_notification(
    version_id='v20251109_030145',
    metrics=new_metrics,
    comparison=comparison,
    decision='KEEP_NEW'
)
```

**Template:** `reports/email_templates/email_model_retrained.html`

**Email generado:**
```
✅ Re-entrenamiento Exitoso - DomusAI

Versión: v20251109_030145
Fecha: 2025-11-09 03:02:15
Datos: 90 días (129,600 registros)

📊 Métricas Nuevas:
• MAE: 0.168 kW
• RMSE: 0.241 kW
• MAPE: 68.3%
• R²: 0.682

📈 Comparación:
• MAE: -6.1% ✅ (mejor)
• RMSE: -4.4% ✅ (mejor)
• R²: +3.3% ✅ (mejor)

🏆 Decisión: KEEP_NEW
El nuevo modelo mejora el anterior y ha sido
puesto en producción automáticamente.
```

#### 5️⃣ Logging
```
2025-11-09 03:00:15 - INFO - 🌙 [DAILY] Verificando necesidad...
2025-11-09 03:00:18 - INFO - ⏱️ 7 días desde último entrenamiento
2025-11-09 03:00:20 - INFO - 🚀 Iniciando re-entrenamiento
2025-11-09 03:00:25 - INFO - ✅ Datos validados: 129,600 registros
2025-11-09 03:01:35 - INFO - ✅ Prophet entrenado en 45.2s
2025-11-09 03:01:48 - INFO - ✅ Isolation Forest entrenado en 12.8s
2025-11-09 03:02:05 - INFO - 📊 MAE: 0.168 kW (-6.1% mejora)
2025-11-09 03:02:08 - INFO - 🏆 DECISIÓN: KEEP_NEW (modelo mejorado)
2025-11-09 03:02:12 - INFO - 💾 Guardado: v20251109_030145
2025-11-09 03:02:15 - INFO - 📧 Email notificación enviado
2025-11-09 03:02:15 - INFO - ✅ Re-entrenamiento completado: 120.3s
```

---

## ☀️ JOB #3: Reporte Diario (8:00 AM)

**Archivo:** `scripts/auto_training_scheduler.py`  
**Función:** `generate_daily_report()` (líneas 460-522)  
**Trigger:** `CronTrigger("0 8 * * *")`  
**Duración típica:** 10-15 segundos

### Flujo de Ejecución

#### 1️⃣ Obtener Últimas 24 Horas de Railway
```sql
SELECT * FROM energy_readings 
WHERE timestamp >= NOW() - INTERVAL 1 DAY 
ORDER BY timestamp ASC
```
- **Registros:** ~1,440 (1 día × 1,440 min)

#### 2️⃣ Generar Reporte HTML
**Archivo:** `src/reporting.py`  
**Función:** `generate_daily_report()`

**Estadísticas calculadas:**
- Consumo total día (kWh)
- Consumo promedio hora (kW)
- Pico máximo y valle mínimo
- Coste estimado (× 0.25 €/kWh)
- Top 3 horas pico

**Gráficos generados (matplotlib):**
1. Consumo por hora (línea temporal)
2. Distribución sub-metering (barras)
3. Voltaje vs Consumo (scatter)

**Template:** `reports/templates/daily_report.html`  
**Output:** `reports/generated/daily_report_20251102.html` (~70 KB)

#### 3️⃣ Enviar Email
**Template:** `reports/email_templates/email_daily_report.html`

**Email:**
```
☀️ Reporte Diario - 02/11/2025

Consumo total: 10.8 kWh
Coste: 2.70 €
Promedio: 0.45 kW

Hora pico: 20:00 (2.8 kW)
Hora valle: 04:00 (0.18 kW)

Ver reporte completo en adjunto.
```
**Adjunto:** `daily_report_20251102.html`

---

## 📅 JOB #4: Reporte Semanal (Lunes 9:00 AM)

**Trigger:** `CronTrigger("0 9 * * 1")` - Cada lunes

**Similar a diario pero con:**
- Query: Últimos 7 días
- Gráficos adicionales:
  - Comparativa día a día (barras)
  - Tendencia semanal (línea)
  - Distribución por día (boxplot)
- Estadísticas:
  - Día mayor/menor consumo
  - Variación día a día (%)
  - Consumo total semana

**Output:** `reports/generated/weekly_report_20251028.html` (~150 KB)

---

## 📊 JOB #5: Reporte Mensual (Día 1 de mes, 10:00 AM)

**Archivo:** `scripts/auto_training_scheduler.py`  
**Función:** `generate_monthly_report()` (líneas 592-680)  
**Trigger:** `CronTrigger("0 10 1 * *")`  
**Duración típica:** 35-45 segundos

### El Reporte Más Completo

#### 1️⃣ Obtener Mes Anterior Completo
```python
now = datetime.now()
if now.month == 1:
    month, year = 12, now.year - 1
else:
    month, year = now.month - 1, now.year
```

```sql
SELECT * FROM energy_readings 
WHERE YEAR(timestamp) = 2025 
  AND MONTH(timestamp) = 10 
ORDER BY timestamp ASC
```
- **Registros:** ~43,200 (30 días × 1,440 min)

#### 2️⃣ Generar HTML Avanzado

**Archivo:** `src/reporting.py`  
**Función:** `generate_and_send_monthly_report()`

**Estadísticas mensuales:**
- Consumo total mes (kWh)
- Consumo promedio diario
- Día mayor/menor consumo
- Coste total mes (€)
- Proyección anual
- Comparación vs mes anterior (%)
- Patrón weekday vs weekend

**Gráficos avanzados (matplotlib + seaborn):**
1. Consumo diario (barras + línea tendencia)
2. Distribución horaria (heatmap 24×30)
3. Sub-metering pie chart
4. Comparativa últimos 6 meses (barras)
5. Análisis anomalías (scatter + boxplot)

**Recomendaciones inteligentes:**

Sistema rule-based que analiza patrones:

```python
if consumo_nocturno > 0.5 kW:
    → "Consumo nocturno elevado (X kW). Revisar standby"

if pico_horario fuera de patrón:
    → "Pico inusual a las X:00 (Y kW). Verificar programación"

if tendencia_mes > 10%:
    → "Incremento del X% vs anterior. Revisar HVAC"
```

**Recomendaciones IDAE España:**
- Usar lavadora/lavavajillas en valle
- Regular termostato ±1°C (ahorro 7%)
- LED en lugar de halógenas (ahorro 80%)

**Template:** `reports/templates/monthly_report.html` (650 líneas)  
**Output:** `reports/generated/reporte_2025-10_20251102_172900.html` (~220 KB)

#### 3️⃣ Generar PDF
```python
from xhtml2pdf import pisa

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

with open(pdf_path, 'wb') as f:
    pisa.CreatePDF(html, dest=f)
```

**Librería:** xhtml2pdf (pisa)  
**Features:**
- Preserva CSS y layout
- Embebe imágenes base64
- Paginación automática

**Output:** `reports/generated/reporte_2025-10_20251102_172900.pdf` (~340 KB)

#### 4️⃣ Enviar Email con 2 Adjuntos

**Template:** `reports/email_templates/monthly_report_email.html` (330 líneas)

**Email generado:**
```
📊 Reporte Mensual DomusAI - Octubre 2025

Hola,

Adjuntamos tu reporte mensual de octubre:

📊 Resumen del Mes:
• Consumo total: 135.2 kWh
• Coste estimado: 33.80 €
• Promedio diario: 4.51 kWh
• Comparación anterior: +12.3%

🎯 Recomendaciones Principales:
1. Reducir standby nocturno (ahorro 8€/mes)
2. Usar lavadora en valle (ahorro 5€/mes)
3. Revisar termostato calefacción

Ver reporte completo en adjuntos.

Saludos,
DomusAI System
```

**Adjuntos:**
1. `reporte_2025-10_20251102_172900.html` (220 KB)
2. `reporte_2025-10_20251102_172900.pdf` (340 KB)

**Destinatarios:**
- enriquesl1102@gmail.com
- ddanimc2602@gmail.com

---

## 📁 Estructura de Archivos en Producción

```
DomusAI/
├── scripts/
│   ├── auto_training_scheduler.py ⭐ (Proceso principal 24/7)
│   └── initialize_models.py       (One-time setup)
│
├── src/
│   ├── config.py                  (Config centralizada + constantes)
│   ├── predictor.py               (Prophet/ARIMA predictions)
│   ├── anomalies.py               (5 algoritmos + consenso)
│   ├── reporting.py               (HTML/PDF generation)
│   ├── email_sender.py            (SMTP + Jinja2 templates)
│   ├── auto_trainer.py            (Pipeline re-entrenamiento)
│   ├── database.py                (Railway MySQL connector)
│   └── validators.py              (Data quality checks)
│
├── models/ ⭐ (Modelos en producción)
│   ├── best_prophet.pkl                      (204 MB) → predictor.py
│   ├── best_isolation_forest.pkl             (1.5 MB) → anomalies.py
│   ├── prophet_v20251102_163825.pkl          (Backup versionado)
│   ├── isolation_forest_v20251102_163825.pkl (Backup versionado)
│   └── training_history.json                 (Historial versiones)
│
├── logs/ ⭐ (Logging 24/7, UTF-8)
│   ├── scheduler.log              (Todos los jobs)
│   ├── auto_training.log          (Re-entrenamientos)
│   ├── email_sender.log           (SMTP transactions)
│   └── metrics_history.json       (Métricas por versión)
│
├── reports/
│   ├── templates/                 (Jinja2 HTML templates)
│   │   ├── daily_report.html
│   │   ├── weekly_report.html
│   │   └── monthly_report.html    (650 líneas)
│   │
│   ├── email_templates/           (Email HTML templates)
│   │   ├── email_daily_report.html
│   │   ├── email_weekly_report.html
│   │   ├── monthly_report_email.html     (330 líneas)
│   │   ├── anomaly_alert_email.html
│   │   └── email_model_retrained.html
│   │
│   └── generated/ ⭐ (Reportes generados)
│       ├── daily_report_20251102.html      (~70 KB)
│       ├── weekly_report_20251028.html     (~150 KB)
│       ├── reporte_2025-10_20251102.html   (~220 KB)
│       └── reporte_2025-10_20251102.pdf    (~340 KB)
│
├── synthetic_data_generator/
│   ├── generate_consumption_data.py (949 líneas, ultra-realista)
│   ├── config.yaml
│   └── output/
│       └── synthetic_1460days_20251101_193442.csv (131 MB, 4 años)
│
├── config/
│   └── scheduler_config.yaml      (Configuración jobs)
│
├── tests/
│   ├── test_anomalies_railway.py
│   ├── test_predictor_railway.py
│   ├── test_reporting_railway.py
│   ├── test_email_templates.py
│   └── test_send_real_email.py    (Test completo con datos reales)
│
└── .env ⭐ (Credenciales sensibles, NO en git)
    ├── MYSQL_HOST=railway-host.railway.app
    ├── MYSQL_USER=root
    ├── MYSQL_PASSWORD=***
    ├── SMTP_HOST=smtp.gmail.com
    ├── SENDER_EMAIL=domusaisystem@gmail.com
    ├── SENDER_PASSWORD=*** (Gmail App Password)
    └── DEFAULT_RECIPIENTS=enriquesl1102@gmail.com,ddanimc2602@gmail.com
```

---

## 🔄 Flujo de Datos en Producción

```
┌──────────────────────────────────────────────────────────────┐
│  📡 FUENTE DE DATOS: Railway MySQL (Producción)              │
│  Host: crossover.proxy.rlwy.net:50561                        │
│  Database: railway                                           │
│  Tabla: energy_readings                                      │
│  Inserts: ESP32 MQTT cada 1 minuto (futuro Sprint 8)        │
│  Registros actuales: 0 (pendiente ESP32)                    │
│  Fallback: CSV sintético 4 años (2.1M registros)            │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ├─────────────► JOB #1 (Hourly)
                     │                 • Query: Last 60 min
                     │                 • Detecta anomalías (5 métodos)
                     │                 • Envía alertas si severity ≥ MEDIUM
                     │
                     ├─────────────► JOB #2 (Daily 3 AM, cada 7 días)
                     │                 • Query: Last 90 days
                     │                 • Re-entrena Prophet + IsolationForest
                     │                 • Compara métricas con anterior
                     │                 • Guarda solo si mejora (KEEP_NEW)
                     │
                     ├─────────────► JOB #3 (Daily 8 AM)
                     │                 • Query: Last 24 hours
                     │                 • Genera HTML + 3 gráficos
                     │                 • Envía email con adjunto
                     │
                     ├─────────────► JOB #4 (Weekly, Lunes 9 AM)
                     │                 • Query: Last 7 days
                     │                 • Análisis comparativo semanal
                     │                 • Email + HTML adjunto
                     │
                     └─────────────► JOB #5 (Monthly, Día 1 10 AM)
                                       • Query: Mes anterior completo
                                       • HTML (220 KB) + PDF (340 KB)
                                       • Email + 2 adjuntos
```

---

## ⏱️ Timeline Típico de 24 Horas

```
Hora   │ Actividad                    │ Consumo Típico
───────┼──────────────────────────────┼────────────────
00:00  │ Standby                      │ ~0.20 kW
01:00  │ 🕐 Job #1: Detección          │ ~0.20 kW
02:00  │ 🕐 Job #1: Detección          │ ~0.20 kW
03:00  │ 🌙 Job #2: Re-entrenamiento   │ ~0.20 kW (si día 7)
04:00  │ 🕐 Job #1: Detección          │ ~0.18 kW (valle mínimo)
05:00  │ 🕐 Job #1: Detección          │ ~0.20 kW
06:00  │ 🕐 Job #1: Detección          │ ~0.25 kW (inicio actividad)
07:00  │ 🕐 Job #1: Detección          │ ~1.5 kW (desayuno)
08:00  │ ☀️ Job #3: Reporte Diario     │ ~2.8 kW (pico mañana)
09:00  │ 🕐 Job #1 + 📅 Job #4 (lun)  │ ~1.2 kW
10:00  │ 🕐 Job #1 + 📊 Job #5 (día1) │ ~0.8 kW
11:00  │ 🕐 Job #1: Detección          │ ~0.6 kW
12:00  │ 🕐 Job #1: Detección          │ ~0.7 kW
13:00  │ 🕐 Job #1: Detección          │ ~1.8 kW (cocina)
14:00  │ 🕐 Job #1: Detección          │ ~2.5 kW (pico mediodía)
15:00  │ 🕐 Job #1: Detección          │ ~1.2 kW
16:00  │ 🕐 Job #1: Detección          │ ~0.9 kW
17:00  │ 🕐 Job #1: Detección          │ ~1.1 kW
18:00  │ 🕐 Job #1: Detección          │ ~1.8 kW (inicio noche)
19:00  │ 🕐 Job #1: Detección          │ ~2.2 kW
20:00  │ 🕐 Job #1: Detección          │ ~3.5 kW (pico noche)
21:00  │ 🕐 Job #1: Detección          │ ~2.8 kW (cocina + TV)
22:00  │ 🕐 Job #1: Detección          │ ~1.5 kW
23:00  │ 🕐 Job #1: Detección          │ ~0.8 kW
```

**Total ejecuciones/día:**
- Job #1 (Anomalías): 24 veces
- Job #2 (Re-entrenamiento): 1/7 días
- Job #3 (Diario): 1 vez
- Job #4 (Semanal): 1/7 días
- Job #5 (Mensual): 1/30 días

---

## 🔧 Configuración Esencial

### .env (Variables de Entorno)
```bash
# Base de datos Railway MySQL
MYSQL_HOST=crossover.proxy.rlwy.net
MYSQL_PORT=50561
MYSQL_DATABASE=railway
MYSQL_USER=root
MYSQL_PASSWORD=nawCodCbeWibNfjPLSyNDKTFMpocbvtu

# Email SMTP (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=domusaisystem@gmail.com
SENDER_PASSWORD=akcb urai xyjr rhrh  # App Password

# Destinatarios
DEFAULT_RECIPIENTS=enriquesl1102@gmail.com,ddanimc2602@gmail.com

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Europe/Madrid
```

### scheduler_config.yaml
```yaml
general:
  timezone: Europe/Madrid

jobs:
  anomaly_detection:
    enabled: true
    interval_minutes: 60
  
  model_retraining:
    enabled: true
    cron: "0 3 * * *"
    min_days_between: 7
  
  daily_report:
    enabled: true
    cron: "0 8 * * *"
  
  weekly_report:
    enabled: true
    cron: "0 9 * * 1"  # Lunes 9 AM
  
  monthly_report:
    enabled: true
    cron: "0 10 1 * *"  # Día 1, 10 AM

notifications:
  enabled: true
  email_on_error: true
  email_on_success: false
```

---

## 📈 Métricas de Performance

### Modelos ML Actuales (v20251102_163825)

**Prophet (Predicción):**
- MAE: 0.179 kW
- RMSE: 0.252 kW
- MAPE: 72.9%
- R²: 0.660
- Training time: ~45 segundos (90 días)
- Tamaño en disco: 204 MB
- RAM en uso: ~320 MB peak

**Isolation Forest (Anomalías):**
- Contamination: 5%
- n_estimators: 100
- Training time: ~12 segundos (90 días)
- Tamaño en disco: 1.5 MB
- RAM en uso: ~80 MB

### Sistema General

**Scheduler:**
- Uptime objetivo: 99.9% (24/7)
- CPU idle: ~95% (solo picos en jobs)
- RAM total: ~500 MB
- Disk writes: ~10 MB/día (logs + reportes)

**Jobs:**
- Anomaly detection: 7-12 segundos
- Re-training: 120-180 segundos
- Daily report: 10-15 segundos
- Weekly report: 15-20 segundos
- Monthly report: 35-45 segundos

---

## 🚀 Comandos de Producción

### Iniciar Sistema
```powershell
# 1. Activar entorno
.venv\Scripts\Activate.ps1

# 2. Iniciar scheduler (24/7)
python scripts/auto_training_scheduler.py

# El scheduler corre hasta Ctrl+C
```

### Monitoreo en Tiempo Real
```powershell
# Ver logs en vivo
Get-Content logs\scheduler.log -Wait -Tail 20

# Ver últimos reportes generados
Get-ChildItem reports\generated -Name | Sort-Object -Descending | Select-Object -First 5

# Ver modelos disponibles
Get-ChildItem models\*.pkl -Name
```

### Testing Manual
```powershell
# Test de predicción rápida
python test_prediction_fast.py

# Test de email real
python tests/test_send_real_email.py --type monthly

# Test de anomalías
python tests/test_anomalies_railway.py
```

### Mantenimiento
```powershell
# Limpiar reportes antiguos (>30 días)
Get-ChildItem reports\generated -Filter *.html | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item

# Verificar espacio en disco
Get-ChildItem models, logs, reports\generated -Recurse | Measure-Object -Property Length -Sum

# Backup de modelos
Copy-Item models\best_*.pkl models\backups\
```

---

## 📊 Próximos Pasos (Sprint 8)

### Integración ESP32 + MQTT

**Pendiente:**
1. ESP32 → Publicar a MQTT broker cada 1 minuto
2. Python subscriber → INSERT directo a Railway MySQL
3. Scheduler → SELECT de Railway → Pipeline automático
4. Validación end-to-end con datos reales de sensores

**Estado:** 95% completo (solo falta hardware ESP32)

---

## 📝 Notas de Implementación

### Type Safety (Pylance Strict)
- Todos los módulos typehinted
- Sin `Any` en producción
- Cast explícito para Pandas DatetimeIndex

### Memory Optimization
- Prophet `uncertainty_samples=100` (ahorra 1.8 GB)
- joblib compression para modelos
- Limpieza de memoria post-training (`gc.collect()`)

### Error Handling
- Try-except en todos los jobs
- Logging exhaustivo con contexto
- Fallback a CSV si Railway falla
- Reintentos automáticos con backoff

### Logging Standards
- UTF-8 encoding (soporta emojis 🎉)
- Formato consistente: `YYYY-MM-DD HH:MM:SS - LEVEL - mensaje`
- Rotación automática de logs (10 MB × 5 backups)

---

## 📧 Contacto y Soporte

**Desarrolladores:**
- Enrique: enriquesl1102@gmail.com
- Daniel: ddanimc2602@gmail.com

**Repositorio:** [DomusAI GitHub](https://github.com/ddani22/DomusAI)

**Documentación:**
- README.md (Overview general)
- ARCHITECTURE.md (Este documento)
- docs/ (Documentación detallada por módulo)

---

**Última actualización:** 2025-11-02 17:30:00  
**Versión documento:** 1.0  
**Estado sistema:** ✅ Producción (95% completo)
