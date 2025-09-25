# DomusAI - Sistema de Monitoreo y Predicción de Consumo Energético

## Project Architecture & Data Flow

**Core Domain**: Energy consumption analysis and prediction for residential/community monitoring with automated reporting.

**Data Pipeline**: Raw CSV → `limpiar_dataset.py` → Clean CSV → Analysis → Predictions → Reports → Email notifications

**Key Data Schema**:
- **Input**: `Dataset de prueba de consumo.csv` with columns: `Date` (dd/mm/yy), `Time`, `Global_active_power`, `Global_reactive_power`, `Voltage`, `Global_intensity`, `Sub_metering_1-3`
- **Output**: `consumo_limpio_pruebas.csv` with `Datetime` index (converted to 4-digit years) and float64 columns

## Essential Patterns & Conventions

### Data Cleaning Workflow (`limpiar_dataset.py`)
```python
# Standard pattern for year conversion (2-digit to 4-digit)
def convertir_fecha_a_4_digitos(fecha_str):
    # Rule: 00-30 → 2000-2030, 31-99 → 1931-1999
    if año_2d <= 30:
        año_4d = 2000 + año_2d
    elif año_2d >= 70:
        año_4d = 1900 + año_2d
```

### Error Handling Philosophy
- Use `errors='coerce'` for datetime parsing to handle malformed data
- Fill `Sub_metering_3` nulls with 0 (domain-specific: sub-metering can be legitimately zero)
- Convert '?' and non-numeric values to NaN before float conversion

### Output Formatting
- Always use emoji-prefixed progress messages: `🔄`, `📊`, `✅`, `⚠️`
- Show data samples and statistics for verification
- Include comma-formatted numbers for readability: `f"{len(df):,}"`

## Project Structure

```
proyecto-energia/
│── data/                    # Datasets originales y limpios
│   ├── Dataset_original_test.csv
│   ├── Dataset_clean_test.csv
│
│── notebooks/               # Jupyter Notebooks de pruebas y EDA
│   ├── 01_eda.ipynb
│   ├── 02_prediccion.ipynb
│   ├── 03_anomalias.ipynb
│
│── src/                     # Código principal en Python
│   ├── data_cleaning.py     # Limpieza y preparación de datos
│   ├── eda.py               # Funciones de análisis exploratorio
│   ├── prediction.py        # Modelos de predicción
│   ├── anomalies.py         # Detección de anomalías
│   ├── reporting.py         # Generación de reportes
│   ├── email_sender.py      # Envío de correos automáticos
│
│── reports/                 # Reportes generados (PDF/HTML)
│   ├── reporte_2025-01.pdf
│
│── README.md               # Descripción del proyecto
│── requirements.txt        # Dependencias de Python
```

## Technology Stack & Dependencies

**Core Processing**:
- **Python** - Backend de procesamiento de datos
- **Pandas/Numpy** - Limpieza y manipulación de datos

**Visualization**:
- **Matplotlib/Seaborn/Plotly** - Visualización de datos

**Prediction Models**:
- **Statsmodels/Prophet/Scikit-learn/TensorFlow (LSTM)** - Modelos de predicción de consumo

**Anomaly Detection**:
- **Scikit-learn/Isolation Forest/Autoencoders** - Detección de anomalías

**Data Storage**:
- **SQLite o InfluxDB** - Almacenamiento de datos

**Reporting & Communication**:
- **smtplib/yagmail** - Envío de correos con reportes
- **Reportlab/WeasyPrint** - Generación de reportes PDF/HTML

**Optional Dashboard**:
- **Flask/Dash** - Dashboard web para visualización en tiempo real

**Current Dependencies**: Minimal setup (`pandas==2.3.2`, `numpy==2.3.3`) ready for expansion.

## Development Workflow

**Sequential Pipeline**:
1. **Limpieza de datos** → preparar dataset (`data_cleaning.py`)
2. **EDA (análisis exploratorio)** → gráficas y patrones básicos (`eda.py`)
3. **Modelado predictivo** → entrenar modelos de series temporales (`prediction.py`)
4. **Detección de anomalías** → identificar consumos anormales (`anomalies.py`)
5. **Generación de reportes** → PDF/HTML con gráficas y predicciones (`reporting.py`)
6. **Envío automático de reportes** → correo electrónico (`email_sender.py`)
7. **(Opcional) Dashboard web** → monitoreo en tiempo real

**Current Status**:
- ✅ Dataset de prueba cargado
- ✅ Limpieza de datos (completada con `limpiar_dataset.py`)
- ⏳ **Next Priority**: Exploración inicial y visualizaciones
- 🔄 **Upcoming**: Primer modelo de predicción, detección de anomalías, reportes automáticos## Energy Domain Knowledge

**Data Characteristics**:
- 1-minute resolution time series data (260,640 rows = ~6 months)
- Missing data patterns: ~3,771 nulls (1.4%) typically occur in clusters (sensor failures)
- Sub-metering values: 0-based, can legitimately be zero during off-peak hours
- Voltage range: ~230-245V (European standard)

**Expected Analysis Patterns**:
- Daily/weekly seasonality in consumption
- Peak hours: morning (7-9am) and evening (6-9pm)
- Anomalies: sudden spikes, prolonged high consumption, sensor failures

## Collaboration Context

**Team Structure**: Python/AI developer + Electronics partner (ESP32/Arduino, MQTT)
**Future Integration**: Real-time sensor data via MQTT → Database → Analysis pipeline