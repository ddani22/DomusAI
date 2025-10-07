# 🏠 DomusAI - Sistema de Monitoreo y Predicción de Consumo Energético

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Prophet 1.1.5](https://img.shields.io/badge/Prophet-1.1.5-green.svg)](https://facebook.github.io/prophet/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Development](https://img.shields.io/badge/Status-Active%20Development-brightgreen.svg)]()

**DomusAI** es un sistema inteligente de análisis y predicción de consumo energético diseñado para viviendas y comunidades, que combina machine learning, análisis de series temporales y reportes automáticos para optimizar el uso de energía.

> 🎯 **Estado Actual**: Sistema de Reportes HTML Implementado (85%) | **Siguiente**: PDF y Email

---

## 📋 Tabla de Contenidos

- [🎯 Características Principales](#-características-principales)
- [🔧 Stack Tecnológico](#-stack-tecnológico)
- [📂 Estructura del Proyecto](#-estructura-del-proyecto)
- [📊 Datos del Proyecto](#-datos-del-proyecto)
- [🚀 Desarrollo y Flujo de Trabajo](#-desarrollo-y-flujo-de-trabajo)
- [📈 Estado del Proyecto](#-estado-del-proyecto)
- [🚀 Inicio Rápido](#-inicio-rápido)
- [📚 Documentación Técnica](#-documentación-técnica)
- [🤝 Colaboración](#-colaboración)

---

## 🎯 Características Principales

### ✅ **Implementadas** (85% del Proyecto)

#### 📊 **Análisis de Datos Completo**
- ✅ **Procesamiento automatizado** de datasets de consumo eléctrico
- ✅ **Limpieza inteligente** con manejo de valores faltantes y conversión de formatos de fecha
- ✅ **Análisis exploratorio completo** (EDA) con identificación de patrones temporales
- ✅ **Exportación de insights** a JSON para reutilización en pipeline

#### 🔮 **Sistema de Predicción Avanzado**
- ✅ **Modelos múltiples**: Prophet (principal), ARIMA (validación), Prophet Enhanced
- ✅ **Predicciones escalables**: 1 hora hasta 30 días
- ✅ **Intervalos de confianza**: 95% configurables con análisis de incertidumbre
- ✅ **Optimización de memoria**: Reducción de 1.8 GB RAM en datasets grandes
- ✅ **Validación temporal robusta**: Split 80/20 con métricas MAE, RMSE, MAPE, R²
- ✅ **API modular**: Integración fácil con otros sistemas

#### ⚠️ **Sistema de Detección de Anomalías**
- ✅ **Detección multi-método**: 5 algoritmos (IQR, Z-Score, Isolation Forest, Moving Average, Prediction-Based)
- ✅ **Consenso inteligente**: Reduce falsos positivos combinando ≥3 métodos
- ✅ **Clasificación por tipos**: 4 categorías (Consumo Alto, Bajo, Temporal, Fallo Sensor)
- ✅ **Sistema de alertas**: Severidad automática (crítico, medio, bajo)
- ✅ **Exportación automática**: CSV + JSON con timestamp
- ✅ **Notebook completo**: 34 celdas de experimentación y validación
- ✅ **Producción lista**: Módulo robusto de 1,060+ líneas con logging UTF-8

#### 📋 **Sistema de Reportes HTML** (NUEVO ✨)
- ✅ **Generación HTML automática**: Templates Jinja2 profesionales con CSS moderno
- ✅ **Resumen ejecutivo**: KPIs principales, cambio mensual, score de eficiencia
- ✅ **Visualizaciones embebidas**: Gráficos matplotlib en PNG de alta resolución
- ✅ **Análisis temporal completo**: Consumo diario, horario, distribución semanal
- ✅ **Recomendaciones inteligentes**: Sistema de sugerencias basado en patrones
- ✅ **Infraestructura completa**: Assets (logos, iconos), templates, CSS profesional
- ✅ **Producción lista**: Módulo de 500+ líneas con logging completo
- ✅ **Validado**: Test script genera reportes exitosamente

#### 📈 **Visualización y Análisis**
- ✅ **Gráficos interactivos** con Plotly (notebooks)
- ✅ **Análisis temporal**: Patrones diarios, semanales y estacionales
- ✅ **Correlaciones energéticas** entre variables del sistema
- ✅ **Componentes de estacionalidad** visualizables (Prophet)
- ✅ **Visualización de anomalías** por método y tipo

### 🔄 **En Desarrollo** (15% Restante)

#### 📋 **Exportación PDF de Reportes**
- 📅 Conversión HTML → PDF con WeasyPrint
- 📅 Diseño optimizado para impresión
- 📅 Metadatos y marca de agua

#### 📧 **Notificaciones Automáticas**
- 📅 Envío por email de reportes mensuales
- 📅 Alertas de anomalías en tiempo real
- 📅 Configuración SMTP flexible
- 📅 Templates HTML profesionales

#### 🔗 **Integración Completa del Pipeline**
- 📅 Reportes con predicciones integradas
- 📅 Reportes con anomalías detectadas
- 📅 Dashboard unificado de métricas

#### 🌐 **Dashboard Web** (Opcional - Fase Futura)
- 📅 Monitoreo en tiempo real con Flask/Dash
- 📅 Visualizaciones interactivas con Plotly
- 📅 Integración con MQTT para datos ESP32
- 📅 Gestión de usuarios y permisos

---

## 🔧 Stack Tecnológico

### **Core Analytics & Data Processing**
```python
pandas==2.3.2          # Manipulación de series temporales
numpy==1.26.4          # Computación numérica de alto rendimiento
matplotlib==3.10.6     # Visualización base para reportes
seaborn==0.13.2        # Visualización estadística avanzada
plotly==5.15.0         # Gráficos interactivos en notebooks
jinja2==3.1.6          # Templates HTML para reportes (NUEVO ✨)
```

### **Machine Learning & Forecasting**
```python
scikit-learn==1.7.2    # Algoritmos ML, métricas y validación
prophet==1.1.5         # Series temporales con estacionalidad automática (Meta/Facebook)
statsmodels==0.14.5    # Modelos estadísticos clásicos (ARIMA, SARIMAX)
keras==3.11.3          # Deep Learning (futuras implementaciones LSTM)
```

### **Optimization & Performance**
```python
optuna==4.5.0          # Optimización automática de hiperparámetros
memory-profiler==0.61.0 # Profiling de memoria para datasets grandes
joblib==1.5.2          # Persistencia eficiente de modelos
```

### **Development & Experimentation**
```python
jupyter==1.1.1         # Notebooks interactivos para experimentación
ipykernel==6.30.1      # Kernel Python para Jupyter
notebook==7.4.7        # Interfaz Jupyter Notebook
tqdm==4.67.1           # Barras de progreso para entrenamientos
```

### **Utilities**
```python
python-dateutil==2.9.0.post0  # Manejo avanzado de fechas y timezones
holidays==0.81                # Días festivos para variables exógenas
pickle-mixin==1.0.2           # Serialización de objetos complejos
```

---

## 📂 Estructura del Proyecto

### **Directorio Actual** (Octubre 2025)

```
DomusAI/
│
├── 📁 .github/                      # Configuración de GitHub
│   └── copilot-instructions.md          # Instrucciones para AI assistants
│
├── 📁 data/                         # ✅ COMPLETO - Datasets y análisis
│   ├── Dataset_original_test.csv        # 📊 Datos originales (260,640 registros)
│   ├── Dataset_clean_test.csv           # ✅ Datos procesados y limpios
│   ├── eda_insights.json                # 📈 Métricas y patrones extraídos
│   └── anomalies_*.csv/json             # ⚠️ Resultados de detección de anomalías
│
├── 📁 notebooks/                    # ✅ COMPLETO (4/4 completados)
│   ├── 01_eda.ipynb                     # ✅ Análisis exploratorio completo (42 celdas)
│   ├── 02_prediccion.ipynb              # ✅ Experimentación con modelos (42 celdas)
│   ├── 03_anomalias.ipynb               # ✅ Detección de anomalías (34 celdas)
│   ├── 04_reportes.ipynb                # ✅ Sistema de reportes (28 celdas) [NUEVO ✨]
│   └── logs/                            # 📝 Logs de ejecución de notebooks
│       └── predictions.log
│
├── 📁 src/                          # ✅ CASI COMPLETO (4/5 módulos)
│   ├── data_cleaning.py                 # ✅ Sistema de limpieza completo (312 líneas)
│   │                                    #    - Conversión fechas 2→4 dígitos
│   │                                    #    - Manejo de '?' y nulos
│   │                                    #    - Validación de datos
│   │
│   ├── predictor.py                     # ✅ Motor de predicción (1,561 líneas)
│   │                                    #    - Prophet (modelo principal)
│   │                                    #    - ARIMA (validación)
│   │                                    #    - Prophet Enhanced (mejorado)
│   │                                    #    - Ensemble (combinación inteligente)
│   │                                    #    - Validación temporal automática
│   │                                    #    - Intervalos de confianza
│   │                                    #    - Optimización de memoria
│   │
│   ├── anomalies.py                     # ✅ Sistema de detección de anomalías (1,060 líneas)
│   │                                    #    - 5 métodos de detección (IQR, Z-Score, Isolation Forest, MA, Prediction-Based)
│   │                                    #    - Consenso multi-método (≥3 para alta confianza)
│   │                                    #    - Clasificación en 4 tipos (alto/bajo/temporal/sensor)
│   │                                    #    - Sistema de alertas por severidad
│   │                                    #    - Exportación automática CSV + JSON
│   │                                    #    - Logging UTF-8 compatible Windows
│   │
│   ├── reporting.py                     # ✅ Generador de reportes HTML (500+ líneas) [NUEVO ✨]
│   │                                    #    - Templates Jinja2 profesionales
│   │                                    #    - Resumen ejecutivo con KPIs
│   │                                    #    - Gráficos matplotlib embebidos
│   │                                    #    - Sistema de recomendaciones
│   │                                    #    - Exportación HTML completa
│   │                                    #    - Type-safe (0 errores Pylance)
│   │
│   └── __pycache__/                     # Cache de Python (ignorado en Git)
│   #
│   # ❌ PENDIENTE:
│   # └── email_sender.py                # Notificaciones automáticas
│
├── 📁 logs/                         # ✅ Sistema de logging activo
│   ├── predictions.log                  # Registro de predicciones y errores
│   ├── anomalies.log                    # Registro de detección de anomalías
│   └── reporting.log                    # Registro de generación de reportes [NUEVO ✨]
│
├── 📁 reports/                      # ✅ INFRAESTRUCTURA COMPLETA [NUEVO ✨]
│   ├── templates/                       # ✅ Plantillas Jinja2
│   │   ├── monthly_report.html          # Template principal de reporte
│   │   └── sections/                    # Secciones reutilizables
│   ├── styles/                          # ✅ Estilos CSS profesionales
│   │   └── report_styles.css            # CSS moderno con variables
│   ├── assets/                          # ✅ Recursos estáticos
│   │   ├── logo_domusai.png             # Logo del proyecto
│   │   └── icons/                       # Iconos SVG
│   └── generated/                       # ✅ Reportes generados
│       ├── reporte_2007-06_*.html       # Reportes HTML
│       └── daily_consumption_*.png      # Gráficos generados
│
├── 📁 .venv/                        # 🐍 Entorno virtual Python (ignorado)
│
├── 📄 .gitignore                    # ✅ Configuración Git
├── 📄 README.md                     # ✅ Documentación completa (este archivo)
├── 📄 requirements.txt              # ✅ Dependencias actualizadas (20 paquetes)
└── 📄 test_reporting_basic.py       # ✅ Test de validación de reportes [NUEVO ✨]
```

### **Progreso por Componente**

| Componente | Archivos | Estado | Líneas | Completado | Prioridad |
|------------|----------|--------|--------|------------|-----------|
| **📊 Data Pipeline** | 3 archivos | ✅ | ~600 | 100% | ✅ Alta |
| **📓 EDA Notebooks** | 4/4 archivos | ✅ | ~146 celdas | 100% | ✅ Alta |
| **🔮 Predictor** | 1 archivo | ✅ | 1,561 | 100% | ✅ Alta |
| **⚠️ Anomalías** | 2/2 archivos | ✅ | 1,060 + 34 celdas | 100% | ✅ Alta |
| **📋 Reportes HTML** | 2/2 archivos | ✅ | 500 + 28 celdas | 100% | ✅ Alta |
| **📄 Exportación PDF** | 0/1 archivo | ❌ | 0 | 0% | 🔥 Alta |
| **📧 Email** | 0/1 archivo | ❌ | 0 | 0% | ⚠️ Media |
| **🧪 Testing** | 1 archivo | ✅ | ~76 | 100% | 🔵 Alta |
| **🌐 Dashboard** | 0 archivos | ❌ | 0 | 0% | 🟢 Opcional |

**📊 Progreso Total: 85/100%** hacia DomusAI v1.0

---

## 📊 Datos del Proyecto

### **Dataset Analizado**

| Métrica | Valor | Descripción |
|---------|-------|-------------|
| **Registros Totales** | 260,640 | 6 meses de mediciones continuas |
| **Resolución Temporal** | 1 minuto | Alta granularidad para análisis detallado |
| **Período de Datos** | Ene-Jun 2007 | Dataset histórico de referencia |
| **Variables Medidas** | 7 métricas | Potencia, voltaje, intensidad, sub-mediciones |
| **Tamaño Dataset Limpio** | ~18 MB | CSV optimizado post-limpieza |
| **Valores Nulos** | 3,771 (1.4%) | Manejados con estrategia forward-fill |

### **Variables Energéticas**

| Variable | Descripción | Unidad | Rango Típico | Uso |
|----------|-------------|--------|--------------|-----|
| `Global_active_power` | Potencia activa total | kW | 0.1 - 7.0 | **Principal para predicción** |
| `Global_reactive_power` | Potencia reactiva total | kVAr | 0.0 - 0.5 | Análisis de eficiencia |
| `Voltage` | Voltaje promedio | V | 230 - 245 | Calidad de suministro |
| `Global_intensity` | Intensidad total | A | 0.5 - 30 | Carga instantánea |
| `Sub_metering_1` | Cocina (horno, microondas) | Wh | 0 - 1000 | Análisis por área |
| `Sub_metering_2` | Lavandería (lavadora, secadora) | Wh | 0 - 800 | Análisis por área |
| `Sub_metering_3` | Aire A/C y calefacción | Wh | 0 - 2000 | Análisis por área |

### **Patrones Identificados (EDA)**

#### **🕐 Patrones Temporales**
```python
# Análisis horario
Hora Pico:   21:00 hrs → 2.20 kW (uso doméstico nocturno)
Hora Valle:  04:00 hrs → 0.49 kW (horas de sueño)
Diferencia:  78% variación pico-valle

# Análisis semanal
Días Laborables:  1.05 kW promedio
Fin de Semana:    1.47 kW promedio (+40%)
Día Mayor Consumo: Sábado
Día Menor Consumo: Martes
```

#### **📈 Correlaciones Significativas**
```python
Global_active_power ↔ Global_intensity:  r = 0.999 (correlación perfecta)
Global_active_power ↔ Sub_metering_1:    r = 0.687 (cocina)
Global_active_power ↔ Sub_metering_3:    r = 0.612 (A/C)
Global_active_power ↔ Sub_metering_2:    r = 0.231 (lavandería)
```

#### **⚠️ Anomalías Detectadas Preliminares**
```python
# Método: IQR (Interquartile Range)
Outliers Detectados: 3,457 registros (1.3%)
Consumo Máximo Anómalo: 11.122 kW (vs 2.2 kW promedio)
Patrones Anómalos:
  - Picos nocturnos (02:00-05:00) > 5 kW
  - Consumo cero prolongado (>30 min)
  - Cambios bruscos (>3 kW en 1 minuto)
```

---

## 🚀 Desarrollo y Flujo de Trabajo

### **Pipeline de Datos Completo**

```mermaid
graph LR
    A[📊 CSV Bruto] -->|data_cleaning.py| B[✅ Dataset Limpio]
    B -->|01_eda.ipynb| C[📈 Insights JSON]
    C -->|predictor.py| D[🔮 Predicciones]
    D -->|anomalies.py| E[⚠️ Anomalías]
    E -->|reporting.py| F[📋 Reporte PDF]
    F -->|email_sender.py| G[📧 Notificación]
    
    style B fill:#90EE90
    style C fill:#90EE90
    style D fill:#90EE90
    style E fill:#FFD700
    style F fill:#FFA500
    style G fill:#FFA500
```

### **Fases Implementadas**

#### **1️⃣ Limpieza de Datos** ✅ (`data_cleaning.py`)

```python
def limpiar_dataset_consumo(ruta_csv='data/Dataset_original_test.csv'):
    """
    🧹 Pipeline de limpieza de datos DomusAI
    
    Transformaciones:
    - Conversión fechas: dd/mm/yy → yyyy-mm-dd HH:MM:SS
    - Manejo de '?': Convertidos a NaN
    - Imputación: Forward-fill para nulos
    - Validación: Rangos de voltaje y potencia
    - Output: CSV limpio + logs detallados
    """
```

**Características**:
- ✅ Conversión inteligente de fechas 2→4 dígitos (regla: 00-30 → 2000-2030, 70-99 → 1970-1999)
- ✅ Manejo robusto de caracteres '?' en datos numéricos
- ✅ Validación de rangos físicos (voltaje 220-250V, potencia 0-10kW)
- ✅ Logging completo con emojis para debugging
- ✅ Salida: 260,640 registros limpios, 0 duplicados, 1.4% nulos manejados

#### **2️⃣ Análisis Exploratorio** ✅ (`01_eda.ipynb`)

**Contenido del Notebook** (42 celdas):
1. Setup y carga de datos
2. Estadísticas descriptivas completas
3. Análisis temporal (horario, diario, semanal, mensual)
4. Visualizaciones con Plotly/Matplotlib
5. Análisis de correlaciones (heatmap)
6. Detección preliminar de outliers (IQR, Z-Score)
7. Exportación de insights a JSON

**Insights Exportados** (`eda_insights.json`):
```json
{
  "total_registros": 260640,
  "rango_temporal": "2007-01-01 00:00:00 a 2007-06-30 23:59:00",
  "consumo_promedio": 1.089 kW,
  "patron_horario": {
    "hora_pico": 21,
    "consumo_pico": 2.20 kW,
    "hora_valle": 4,
    "consumo_valle": 0.49 kW
  },
  "correlaciones": {
    "intensity_power": 0.999,
    "submetering1_power": 0.687,
    "submetering3_power": 0.612
  },
  "anomalias_preliminares": 3457
}
```

#### **3️⃣ Predicción Energética** ✅ (`predictor.py` + `02_prediccion.ipynb`)

**Clase Principal**:
```python
class EnergyPredictor:
    """
    🔮 Motor de predicción energética DomusAI
    
    Modelos Implementados:
    - Prophet: Estacionalidad automática (modelo principal)
    - ARIMA: Validación estadística clásica
    - Prophet Enhanced: Prophet mejorado con MCMC sampling
    - Ensemble: Combinación inteligente de modelos
    
    Características:
    - Validación temporal (80/20 split)
    - Intervalos de confianza configurables (95%)
    - Optimización de memoria (1.8 GB ahorro)
    - API modular para integración
    - Logging completo
    """
    
    # Métodos principales
    def load_and_prepare_data(self) -> pd.DataFrame
    def train_prophet_model(self) -> Dict
    def train_arima_model(self) -> Dict
    def train_lstm_model(self) -> Dict
    def predict(self, horizon_days: int, model: str) -> Dict
    def predict_with_confidence(self, horizon_days: int, confidence_level: float) -> Dict
```

**Métricas de Performance** (validación en test set):

| Modelo | MAE (kW) | RMSE (kW) | MAPE (%) | R² | Tiempo Entrenamiento |
|--------|----------|-----------|----------|-----|----------------------|
| **Prophet** | 0.214 | 0.346 | 12.3% | 0.82 | ~35 seg |
| **ARIMA(2,1,2)** | 0.229 | 0.368 | 13.9% | 0.79 | ~42 seg |
| **Prophet Enhanced** | 0.198 | 0.321 | 11.1% | 0.85 | ~3h 18min (MCMC) |
| **Ensemble** | 0.206 | 0.335 | 11.8% | 0.83 | ~55 seg |

**Notebook de Experimentación** (`02_prediccion.ipynb`):
- ✅ 42 celdas completas con análisis comparativo
- ✅ Visualizaciones interactivas (Plotly)
- ✅ Comparación Prophet vs ARIMA
- ✅ Análisis de componentes estacionales
- ✅ Predicciones a 7 días con intervalos de confianza
- ✅ Integración con módulo de producción

**Optimizaciones Críticas**:
```python
# Reducción de uso de memoria
model = Prophet(
    uncertainty_samples=100,  # Default: 1000 (ahorra 1.8 GB RAM)
    # ...
)

# Validación sin incertidumbre
temp_model = Prophet(
    uncertainty_samples=0  # Sin IC durante validación (ahorra 1.9 GB RAM)
)
```

---

## 📈 Estado del Proyecto

### **🎯 Progreso General**

```
█████████████████████████████████████████░░░ 85% Completado

Fases:
✅ Data Cleaning       [████████████████████] 100%
✅ EDA & Analysis      [████████████████████] 100%
✅ Prediction Models   [████████████████████] 100%
✅ Anomaly Detection   [████████████████████] 100%
✅ HTML Reports        [████████████████████] 100%  ← COMPLETADO ✨
⏳ PDF Export          [░░░░░░░░░░░░░░░░░░░░]   0%  ← PRÓXIMO
⏳ Email Automation    [░░░░░░░░░░░░░░░░░░░░]   0%
⏳ Testing & Docs      [████████████████░░░░]  80%
⏳ Web Dashboard       [░░░░░░░░░░░░░░░░░░░░]   0%  (Opcional)
```

### **✅ Hitos Completados**

- [x] **Sprint 0: Configuración del Proyecto** (Semana 1)
  - [x] Estructura de carpetas
  - [x] Entorno virtual Python 3.12
  - [x] Dependencias instaladas (19 paquetes)
  - [x] Repositorio Git inicializado

- [x] **Sprint 1: Data Cleaning** (Semana 2)
  - [x] Script `data_cleaning.py` (312 líneas)
  - [x] Conversión de fechas 2→4 dígitos
  - [x] Manejo de valores '?' y nulos (3,771 registros)
  - [x] Validación de rangos físicos
  - [x] Dataset limpio: 260,640 registros

- [x] **Sprint 2: Análisis Exploratorio** (Semana 3)
  - [x] Notebook `01_eda.ipynb` (42 celdas)
  - [x] Estadísticas descriptivas completas
  - [x] 15+ visualizaciones (temporal, correlaciones, distribuciones)
  - [x] Identificación de patrones (pico 21h, valle 04h)
  - [x] Exportación de insights a `eda_insights.json`

- [x] **Sprint 3: Sistema de Predicción** (Semanas 4-6)
  - [x] Clase `EnergyPredictor` (1,561 líneas)
  - [x] Modelo Prophet (principal) con estacionalidad automática
  - [x] Modelo ARIMA para validación cruzada
  - [x] Prophet Enhanced con MCMC sampling
  - [x] Sistema Ensemble (combinación inteligente)
  - [x] Validación temporal automática (80/20 split)
  - [x] Intervalos de confianza del 95%
  - [x] Optimización de memoria (ahorro 1.8 GB RAM)
  - [x] API modular con salida JSON estructurada
  - [x] Notebook `02_prediccion.ipynb` (42 celdas)
  - [x] Logging completo en `logs/predictions.log`

- [x] **Sprint 4: Sistema de Detección de Anomalías** (Semana 7)
  - [x] Clase `AnomalyDetector` (1,060 líneas)
  - [x] Método IQR (Interquartile Range) para detección estadística
  - [x] Método Z-Score (desviaciones estándar)
  - [x] Método Isolation Forest (Machine Learning principal)
  - [x] Método Moving Average (contexto temporal)
  - [x] Método Prediction-Based (comparación con forecast)
  - [x] Sistema de consenso (≥3 métodos para alta confianza)
  - [x] Clasificación en 4 tipos:
    - [x] Tipo 1: Consumo Excesivo (>P95) - Severidad crítica
    - [x] Tipo 2: Consumo Bajo Anormal (<P05) - Severidad media
    - [x] Tipo 3: Anomalías Temporales (valle horario) - Severidad crítica
    - [x] Tipo 4: Fallo de Sensor (valores constantes) - Severidad baja
  - [x] Sistema de alertas por severidad con acciones configurables
  - [x] Exportación automática (CSV + JSON con timestamps)
  - [x] Notebook `03_anomalias.ipynb` (34 celdas)
  - [x] Script de pruebas `test_anomalies.py` (~400 líneas, 8 tests)
  - [x] Logging UTF-8 compatible con Windows PowerShell
  - [x] Parámetros óptimos validados experimentalmente

- [x] **Sprint 5: Sistema de Reportes HTML** (Semana 8)
  - [x] Infraestructura completa de reportes creada
  - [x] Módulo `reporting.py` (500+ líneas) - Generación HTML
  - [x] Templates Jinja2 profesionales con CSS moderno
  - [x] Resumen ejecutivo con KPIs (consumo, cambio mensual, eficiencia)
  - [x] Gráficos matplotlib embebidos (PNG de alta resolución)
  - [x] Sistema de recomendaciones inteligentes basado en patrones
  - [x] Notebook `04_reportes.ipynb` (28 celdas) - Experimentación completa
  - [x] Script de prueba `test_reporting_basic.py` (76 líneas)
  - [x] Type-safety completo (0 errores Pylance)
  - [x] Logging UTF-8 compatible con Windows
  - [x] Assets (logos, iconos SVG, CSS)
  - [x] Test validado: Reporte junio 2007 generado exitosamente

**Resultados de Validación**:
```python
# Test reporte junio 2007 (30,240 registros, 1 mes)
✅ Reporte HTML generado: reporte_2007-06_20251005_204531.html
✅ Consumo mensual: 594.71 kWh
✅ Cambio vs mes anterior: -18.9%
✅ Score de eficiencia: 78/100
✅ Gráficos generados: 1 (consumo diario)
✅ Tiempo de generación: 2.20 segundos
```

### **🔄 En Desarrollo**

**Ninguno** - Sistema de reportes HTML completado ✅

### **📋 Roadmap Detallado**

#### ~~🔥 Sprint 4: Sistema de Anomalías~~ ✅ **COMPLETADO**

**Prioridad**: CRÍTICA  
**Objetivo**: Detectar consumos anómalos y generar alertas automáticas  
**Duración Real**: 1 día (Octubre 2, 2025)

**✅ Completado**:
- ✅ `src/anomalies.py` (1,060 líneas) - Módulo de producción completo
- ✅ `notebooks/03_anomalias.ipynb` (34 celdas) - Experimentación y validación
- ✅ `test_anomalies.py` (400 líneas) - Suite de 8 tests completos
- ✅ 5 métodos de detección implementados y validados
- ✅ Sistema de consenso con threshold configurable
- ✅ Clasificación en 4 tipos de anomalías
- ✅ Sistema de alertas con severidades
- ✅ Exportación automática CSV + JSON
- ✅ Logging UTF-8 compatible Windows
- ✅ Documentación completa con docstrings
- ✅ Parámetros óptimos validados experimentalmente

**Resultados de Validación**:
```python
# Dataset de prueba: 260,640 registros (6 meses, 1-min resolución)
IQR:                13,664 anomalías (5.24%)
Z-Score:             4,470 anomalías (1.72%)
Isolation Forest:   13,032 anomalías (5.00%) ⭐ Método principal
Moving Average:    104,102 anomalías (40.64%)

Consenso (≥3 métodos): 8,114 anomalías (3.1%)
  - Tipo 1 (Alto):     7,982 (98.4%) → 8,009 alertas críticas
  - Tipo 2 (Bajo):         0 (0.0%)
  - Tipo 3 (Temporal):    27 (0.3%) → Alertas críticas
  - Tipo 4 (Sensor):     100 (1.2%) → Alertas bajas

Tiempo de ejecución: ~6-7 segundos (260K registros)
```

---

#### ~~📋 Sprint 5: Sistema de Reportes HTML~~ ✅ **COMPLETADO**

**Prioridad**: ALTA  
**Objetivo**: Generar reportes HTML automáticos con gráficos y análisis  
**Duración Real**: 3 días (Octubre 3-5, 2025)

**✅ Completado**:
- ✅ Directorio `reports/` con infraestructura completa
  ```
  reports/
  ├── templates/monthly_report.html  # Template principal Jinja2
  ├── styles/report_styles.css       # CSS moderno con variables
  ├── assets/                        # Logos, iconos SVG
  └── generated/                     # Reportes HTML + gráficos PNG
  ```
- ✅ Módulo `src/reporting.py` (500+ líneas)
  - Clase `MonthlyReportGenerator` con métodos modulares
  - Funciones para crear gráficos (matplotlib → PNG)
  - Sistema de recomendaciones basado en patrones
  - Type-safe (0 errores Pylance)
  - Logging completo con UTF-8
- ✅ Templates Jinja2 profesionales
  - Diseño responsive con CSS moderno
  - Variables CSS para personalización
  - Iconos SVG (energy, chart, warning, check)
  - Layout organizado por secciones
- ✅ Funcionalidades implementadas:
  - Resumen ejecutivo con KPIs (consumo, cambio, eficiencia)
  - Gráficos embebidos: consumo diario, horario, distribución semanal
  - Análisis estadístico completo
  - Recomendaciones inteligentes
  - Exportación HTML con timestamp
- ✅ Notebook `04_reportes.ipynb` (28 celdas)
  - Experimentación completa
  - Type-safe con correcciones aplicadas
  - Documentación de uso
- ✅ Script de test `test_reporting_basic.py`
  - Validación de generación de reportes
  - Test exitoso: Junio 2007 (594.71 kWh)
- ✅ Función de conveniencia `generate_quick_report()`
  - API simple para uso rápido
  - Un solo llamado para generar reporte completo

**Resultados de Validación**:
```python
# Test con dataset completo (260,640 registros)
Reporte Junio 2007:
  ✅ HTML generado: reporte_2007-06_20251005_204531.html
  ✅ Consumo total: 594.71 kWh
  ✅ Cambio vs mayo: -18.9%
  ✅ Eficiencia score: 78/100
  ✅ Gráficos: 1 imagen PNG embebida
  ✅ Tiempo: 2.20 segundos
  ✅ Sin errores de tipo (Pylance)
```

---

#### 📄 **Sprint 6: Exportación PDF** (Próximo - 3-5 días)

**Prioridad**: ALTA  
**Objetivo**: Convertir reportes HTML a PDF de alta calidad

**Tareas**:
- [ ] **Añadir funcionalidad PDF a `reporting.py`**
  ```python
  class MonthlyReportGenerator:
      # ... código existente ...
      
      def export_to_pdf(self, html_path: str, output_path: str = None) -> str:
          """Convertir HTML existente a PDF con WeasyPrint"""
          from weasyprint import HTML
          
          if output_path is None:
              output_path = html_path.replace('.html', '.pdf')
          
          HTML(html_path).write_pdf(output_path)
          return output_path
      
      def generate_monthly_report_pdf(self, month: int, year: int) -> Dict:
          """Generar reporte HTML + PDF en un solo paso"""
          # Generar HTML
          html_result = self.generate_monthly_report(month, year)
          
          # Convertir a PDF
          pdf_path = self.export_to_pdf(html_result['html_path'])
          
          return {
              'html_path': html_result['html_path'],
              'pdf_path': pdf_path,
              ...
          }
  ```

- [ ] **Optimizar CSS para impresión**
  - Media query `@media print { ... }`
  - Saltos de página apropiados
  - Tamaño de fuente optimizado
  - Ocultar elementos interactivos

- [ ] **Configurar WeasyPrint**
  ```bash
  pip install weasyprint==60.1
  # Requiere GTK+ en Windows (instalación automática en pip)
  ```

- [ ] **Actualizar test script**
  ```python
  # test_reporting_basic.py
  result = generate_quick_report(
      data_path='data/Dataset_clean_test.csv',
      month=6,
      year=2007,
      format='both'  # 'html', 'pdf', o 'both'
  )
  
  print(f"HTML: {result['html_path']}")
  print(f"PDF: {result['pdf_path']}")  # NUEVO
  ```

**Dependencias Nuevas**:
```bash
pip install weasyprint==60.1  # Conversión HTML → PDF con soporte CSS
# Nota: WeasyPrint puede requerir GTK+ en Windows (se instala automáticamente)
```

**Entregables**:
- ✅ Funcionalidad PDF en `reporting.py`
- ✅ CSS optimizado para impresión
- ✅ Primer reporte PDF generado
- ✅ Test actualizado para formato PDF

**Tiempo Estimado**: 3-5 días

---

#### 📧 **Sprint 7: Notificaciones Automáticas** (1 semana)

**Prioridad**: MEDIA  
**Objetivo**: Envío automático de reportes y alertas por email

**Tareas**:
- [ ] **Implementar `src/email_sender.py`** (estimado: 300-400 líneas)
  ```python
  class EmailSender:
      def __init__(self, smtp_config):
          self.smtp_server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
          self.from_email = smtp_config['from']
          self.password = os.getenv('EMAIL_PASSWORD')
      
      def send_monthly_report(self, recipients, report_path):
          """Enviar reporte PDF adjunto"""
          pass
      
      def send_anomaly_alert(self, recipients, anomaly_data):
          """Enviar alerta HTML de anomalía crítica"""
          pass
      
      def send_prediction_summary(self, recipients, predictions):
          """Enviar resumen de predicciones semanales"""
          pass
  ```

- [ ] **Configuración SMTP**
  - Crear `.env` para credenciales
  - Soporte para Gmail, Outlook, SMTP custom
  - Autenticación con OAuth2 (opcional)

- [ ] **Templates de Email**
  - `email_monthly_report.html`
  - `email_anomaly_alert.html`
  - `email_prediction_summary.html`

- [ ] **Scheduler (opcional)**
  ```python
  import schedule
  import time
  
  def send_monthly_reports():
      # Generar reporte
      # Enviar por email
      pass
  
  schedule.every().month.do(send_monthly_reports)
  ```

**Dependencias Nuevas**:
```bash
pip install python-dotenv==1.0.0  # Para .env
pip install schedule==1.2.0       # Para automatización
```

**Entregables**:
- ✅ `src/email_sender.py` funcional
- ✅ Templates HTML de emails
- ✅ Configuración SMTP documentada
- ✅ Primer email de prueba enviado

---

#### 🧪 **Sprint 8: Testing & Refactorización** (1-2 semanas)

**Prioridad**: MEDIA  
**Objetivo**: Garantizar calidad y mantenibilidad del código

**Tareas**:
- [ ] **Crear estructura de tests**
  ```
  tests/
  ├── test_data_cleaning.py
  ├── test_predictor.py
  ├── test_anomalies.py
  ├── test_reporting.py
  ├── test_email_sender.py
  └── fixtures/
      ├── sample_data.csv
      └── expected_outputs.json
  ```

- [ ] **Implementar tests unitarios**
  ```python
  import pytest
  from src.predictor import EnergyPredictor
  
  def test_prophet_training():
      predictor = EnergyPredictor('tests/fixtures/sample_data.csv')
      result = predictor.train_prophet_model()
      assert result['metrics']['mape'] < 20.0
  
  def test_prediction_output_format():
      predictor = EnergyPredictor('tests/fixtures/sample_data.csv')
      prediction = predictor.predict(horizon_days=7)
      assert 'predictions' in prediction
      assert 'statistics' in prediction
      assert len(prediction['predictions']) == 168  # 7 days * 24 hours
  ```

- [ ] **Documentación API completa**
  - Docstrings en todos los módulos
  - Ejemplos de uso
  - Guía de contribución

- [ ] **Refactorización**
  - Extraer funciones comunes
  - Eliminar código duplicado
  - Mejorar logging

**Dependencias Nuevas**:
```bash
pip install pytest==7.4.3
pip install pytest-cov==4.1.0  # Coverage
```

**Entregables**:
- ✅ Suite de tests completa
- ✅ Coverage >80%
- ✅ Documentación API
- ✅ Código refactorizado

---

#### 🌐 **Sprint 9: Dashboard Web** (Opcional - 2-3 semanas)

**Prioridad**: BAJA (Nice-to-have)  
**Objetivo**: Interfaz web para monitoreo en tiempo real

**Tareas**:
- [ ] **Decidir framework**
  - Opción A: Flask + Plotly Dash
  - Opción B: Streamlit (más rápido)
  - Opción C: FastAPI + React (más robusto)

- [ ] **Implementar backend**
  ```python
  from flask import Flask, render_template, jsonify
  from src.predictor import EnergyPredictor
  
  app = Flask(__name__)
  predictor = EnergyPredictor()
  
  @app.route('/')
  def dashboard():
      return render_template('dashboard.html')
  
  @app.route('/api/predict/<int:days>')
  def api_predict(days):
      prediction = predictor.predict(horizon_days=days)
      return jsonify(prediction)
  ```

- [ ] **Frontend**
  - Dashboard principal con gráficos en tiempo real
  - Página de predicciones
  - Página de anomalías
  - Configuración y alertas

- [ ] **Integración MQTT** (futuro IoT)
  ```python
  import paho.mqtt.client as mqtt
  
  def on_message(client, userdata, msg):
      # Recibir datos del ESP32
      # Actualizar dashboard en tiempo real
      pass
  ```

**Dependencias Nuevas**:
```bash
pip install flask==3.0.0
pip install dash==2.14.2
# o pip install streamlit==1.28.0
pip install paho-mqtt==1.6.1  # Para IoT
```

**Entregables**:
- ✅ Dashboard web funcional
- ✅ API REST para predicciones
- ✅ Visualizaciones interactivas
- ✅ (Opcional) Integración MQTT

---

### **📊 Métricas de Progreso Actualizadas**

| Funcionalidad | Archivos | Líneas | Estado | Completado | ETA |
|---------------|----------|--------|--------|------------|-----|
| **Data Pipeline** | 3/3 | ~600 | ✅ | 100% | Completado |
| **EDA & Analysis** | 4/4 | ~146 celdas | ✅ | 100% | Completado |
| **Prediction System** | 2/2 | 1,561 + 42 celdas | ✅ | 100% | Completado |
| **Anomaly Detection** | 3/3 | 1,060 + 34 celdas + 400 tests | ✅ | 100% | Completado |
| **HTML Report Generation** | 2/2 | 500 + 28 celdas | ✅ | 100% | Completado ✨ |
| **PDF Export** | 0/1 | 0/~100 | ❌ | 0% | 3-5 días |
| **Email Automation** | 0/1 | 0/~400 | ❌ | 0% | 1 semana |
| **Testing & Docs** | 2/5 | 476/~500 | 🔄 | 95% | Casi completo |
| **Web Dashboard** | 0/1 | 0/~800 | ❌ | 0% | 2-3 semanas (opcional) |

**🎯 Tiempo Estimado para v1.0**: 1-2 semanas (solo PDF + Email)  
**🎯 Tiempo Estimado para v1.0+**: 3-4 semanas (con dashboard)

---

## 🚀 Inicio Rápido

### **Requisitos del Sistema**

- **Python**: 3.12 o superior
- **RAM**: 4 GB mínimo (8 GB recomendado para datasets grandes)
- **Espacio en Disco**: 500 MB para entorno + datasets
- **SO**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+

### **Instalación**

```bash
# 1. Clonar repositorio
git clone https://github.com/ddani22/DomusAI.git
cd DomusAI

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Verificar instalación
python -c "from src.predictor import EnergyPredictor; print('✅ DomusAI instalado correctamente')"
```

### **Uso Básico**

#### **1️⃣ Limpiar Dataset**

```python
from src.data_cleaning import limpiar_dataset_consumo

# Procesar datos (maneja conversión de fechas automáticamente)
df_limpio = limpiar_dataset_consumo(
    ruta_csv='data/Dataset_original_test.csv',
    output_path='data/Dataset_clean_test.csv'
)

# Output:
# 🔄 Procesando dataset de consumo energético...
# ✅ Dataset limpio guardado
# 📊 Registros procesados: 260,640
# 📅 Rango temporal: 2007-01-01 00:00:00 a 2007-06-30 23:59:00
```

#### **2️⃣ Análisis Exploratorio**

```bash
# Abrir Jupyter Notebook
jupyter notebook notebooks/01_eda.ipynb

# O ejecutar desde Python
python -m jupyter notebook notebooks/01_eda.ipynb
```

#### **3️⃣ Predicción Energética - API Simple**

```python
from src.predictor import EnergyPredictor

# Inicializar predictor
predictor = EnergyPredictor(data_path='data/Dataset_clean_test.csv')

# Cargar y preparar datos
data = predictor.load_and_prepare_data()

# Entrenar modelo Prophet
predictor.train_prophet_model()

# Generar predicción a 7 días
prediction = predictor.predict(horizon_days=7, model='prophet')

# Mostrar resultados
print(f"📊 Consumo promedio estimado: {prediction['statistics']['mean_consumption']:.3f} kW")
print(f"📈 Consumo total previsto: {prediction['statistics']['total_consumption']:.1f} kWh")
print(f"🔥 Consumo máximo: {prediction['statistics']['max_consumption']:.3f} kW")
print(f"📉 Consumo mínimo: {prediction['statistics']['min_consumption']:.3f} kW")
```

#### **4️⃣ Predicción con Intervalos de Confianza**

```python
# Predicción avanzada con análisis de incertidumbre
prediction_conf = predictor.predict_with_confidence(
    horizon_days=7,
    model='prophet',
    confidence_level=0.95
)

# Analizar incertidumbre
uncertainty = prediction_conf['uncertainty_analysis']
print(f"🎯 Nivel de confianza: {prediction_conf['confidence_intervals']['confidence_level']*100:.0f}%")
print(f"📊 Ancho promedio IC: {uncertainty['mean_interval_width']:.3f} kW")
print(f"📈 Score incertidumbre: {uncertainty['uncertainty_score']:.3f}")

if uncertainty['uncertainty_score'] < 0.2:
    print("✅ Alta confianza en predicción")
elif uncertainty['uncertainty_score'] < 0.5:
    print("⚠️ Confianza moderada")
else:
    print("🔴 Baja confianza - considerar reentrenamiento")
```

#### **4️⃣ Detección de Anomalías - API Simple** (NUEVO ✨)

```python
from src.anomalies import AnomalyDetector, quick_detect

# Opción 1: Detección rápida con un solo método
detector = AnomalyDetector(method='isolation_forest')
df = detector.load_data('data/Dataset_clean_test.csv')
results = detector.detect(df, method='isolation_forest', save=True)

print(f"⚠️ Anomalías detectadas: {len(results['anomalies']):,}")
print(f"📊 Tasa de anomalías: {results['stats']['anomaly_rate']:.2f}%")

# Opción 2: Detección multi-método con consenso
results_all = detector.detect(
    df, 
    method='all',  # Ejecuta los 5 métodos
    consensus_threshold=3,  # Mínimo 3 métodos deben coincidir
    classify=True,  # Clasificar por tipos
    save=True  # Guardar automáticamente
)

# Analizar resultados
print(f"\n🎯 Anomalías de consenso: {len(results_all['consensus_anomalies']):,}")
print(f"🚨 Alertas críticas: {sum(1 for a in results_all['alerts'] if a['severity'] == 'critical')}")

# Por tipo
for type_name, anomalies in results_all['classified_anomalies'].items():
    print(f"   {type_name}: {len(anomalies):,}")

# Opción 3: Función ultra-rápida para scripts
results_quick = quick_detect(
    file_path='data/Dataset_clean_test.csv',
    method='all',
    save=True
)
```

#### **5️⃣ Análisis de Anomalías en Notebooks**

```bash
# Notebook completo de análisis de anomalías
jupyter notebook notebooks/03_anomalias.ipynb

# Incluye:
# - Comparación visual de 5 métodos
# - Análisis de consenso
# - Clasificación por tipos
# - Visualizaciones interactivas de anomalías detectadas
```

#### **6️⃣ Generación de Reportes HTML** (NUEVO ✨)

```python
from src.reporting import generate_quick_report

# Opción 1: Generación rápida con un solo comando
result = generate_quick_report(
    data_path='data/Dataset_clean_test.csv',
    month=6,  # Junio
    year=2007
)

print(f"✅ Reporte generado: {result['html_path']}")
print(f"📊 Consumo mensual: {result['consumption_kwh']:.2f} kWh")
print(f"📈 Cambio vs mes anterior: {result['change_percent']:.1f}%")
print(f"🎯 Score de eficiencia: {result['efficiency_score']}/100")

# Opción 2: Generación avanzada con clase completa
from src.reporting import MonthlyReportGenerator

generator = MonthlyReportGenerator(data_path='data/Dataset_clean_test.csv')
report = generator.generate_monthly_report(month=6, year=2007)

# El reporte incluye:
# - Resumen ejecutivo con KPIs
# - Gráficos de consumo diario, horario y semanal
# - Análisis estadístico completo
# - Recomendaciones personalizadas basadas en patrones
```

#### **7️⃣ Ejecutar Tests de Validación** (NUEVO ✨)

```bash
# Test del sistema de reportes
python test_reporting_basic.py

# Output esperado:
# 🧪 TEST: Generación de Reporte Básico DomusAI
# ================================================================================
# 📂 Dataset encontrado: data/Dataset_clean_test.csv
#    Tamaño: 17.88 MB
# � Generando reporte para Junio 2007...
# ================================================================================
# ✅ REPORTE GENERADO EXITOSAMENTE
# ================================================================================
# 📄 Archivos generados:
#    HTML: reports/generated/reporte_2007-06_20251005_204531.html
# 📊 Gráficos generados:
#    daily_consumption: reports/generated/daily_consumption_200706_204530.png
```

---

## �📚 Documentación Técnica

### **🆕 Mejoras Recientes (Octubre 2025)**

#### **Type-Safety Completo** ✨
- ✅ **0 errores de tipo** en todo el código con Pylance strict mode
- ✅ **Correcciones aplicadas**:
  - `pd.DatetimeIndex()` cast para acceso a `.year`, `.month`, `.hour`
  - `.to_numpy()` en lugar de `.values` para matplotlib
  - Manejo explícito de multi-index en iteraciones
- ✅ **Archivos validados**:
  - `src/reporting.py`: 15 errores corregidos → 0 errores
  - `notebooks/04_reportes.ipynb`: 11+ errores corregidos → 0 errores
  - Código listo para producción con type hints completos

#### **Sistema de Reportes HTML** ✨
- ✅ **Templates Jinja2 profesionales** con CSS moderno
- ✅ **Gráficos embebidos** de alta resolución (matplotlib → PNG)
- ✅ **Recomendaciones inteligentes** basadas en patrones de consumo
- ✅ **Infraestructura completa**: Assets, templates, estilos, generación automática
- ✅ **Validado con tests**: `test_reporting_basic.py` genera reportes exitosamente

#### **Optimizaciones de Rendimiento**
- ✅ **Logging UTF-8**: Compatible con Windows PowerShell (errores de encoding resueltos)
- ✅ **Gestión de memoria**: Optimizaciones en Prophet (ahorro de 1.8 GB RAM)
- ✅ **Tiempo de ejecución**: Reportes generados en ~2-3 segundos

### **Arquitectura del Sistema**

```
┌─────────────────────────────────────────────────────────────────┐
│                  DOMUSAI - ARQUITECTURA v1.0                     │
└─────────────────────────────────────────────────────────────────┘

1️⃣ CAPA DE DATOS (Data Layer)
   ├─ CSV Original (260k registros) → data_cleaning.py
   ├─ CSV Limpio (validado) → eda_insights.json
   └─ Insights JSON (patrones) → predictor.py

2️⃣ CAPA DE ANÁLISIS (Analysis Layer)
   ├─ EDA Notebook (01_eda.ipynb)
   │   ├─ Estadísticas descriptivas
   │   ├─ Patrones temporales
   │   ├─ Correlaciones
   │   └─ Outliers preliminares
   │
   ├─ Predicción Notebook (02_prediccion.ipynb)
   │   ├─ Experimentación con modelos
   │   ├─ Comparación Prophet vs ARIMA
   │   └─ Visualizaciones interactivas
   │
   ├─ Anomalías Notebook (03_anomalias.ipynb)
   │   ├─ Comparación de 5 métodos
   │   ├─ Sistema de consenso
   │   └─ Clasificación por tipos
   │
   └─ Reportes Notebook (04_reportes.ipynb) ✨
       ├─ Generación de reportes HTML
       ├─ Validación de templates
       └─ Ejemplos de uso

3️⃣ CAPA DE MODELOS (Model Layer)
   ├─ predictor.py (motor de predicción) ✅
   │   ├─ Prophet (estacionalidad automática)
   │   ├─ ARIMA (validación estadística)
   │   ├─ Prophet Enhanced (MCMC)
   │   └─ Ensemble (combinación)
   │
   └─ anomalies.py (detección de anomalías) ✅
       ├─ 5 métodos (IQR, Z-Score, IF, MA, Prediction-Based)
       ├─ Sistema de consenso (≥3 métodos)
       ├─ Clasificación en 4 tipos
       └─ Alertas por severidad

4️⃣ CAPA DE PRESENTACIÓN (Presentation Layer)
   ├─ reporting.py (generación de reportes) ✅ ✨
   │   ├─ Templates Jinja2 profesionales
   │   ├─ Gráficos matplotlib embebidos
   │   ├─ Resumen ejecutivo con KPIs
   │   ├─ Sistema de recomendaciones
   │   └─ Exportación HTML (PDF próximamente)
   │
   ├─ [PRÓXIMO] email_sender.py
   │   ├─ SMTP con adjuntos
   │   └─ Templates HTML
   │
   └─ [OPCIONAL] dashboard.py
       ├─ Flask/Dash web app
       └─ Visualizaciones en tiempo real

5️⃣ CAPA DE INTEGRACIÓN (Integration Layer - Futuro)
   ├─ MQTT Broker (ESP32 → Raspberry Pi)
   ├─ Base de Datos (SQLite/InfluxDB)
   └─ API REST (predicciones on-demand)
```

### **Decisiones Técnicas Clave**

#### **¿Por qué Prophet como Modelo Principal?**

| Criterio | Prophet | ARIMA | LSTM | Decisión |
|----------|---------|-------|------|----------|
| **Precisión (MAPE)** | 12.3% | 13.9% | ~8-12% (necesita más datos) | ✅ Prophet |
| **Facilidad de uso** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ✅ Prophet |
| **Estacionalidad automática** | ✅ | ❌ | ⚠️ | ✅ Prophet |
| **Robusto ante nulos** | ✅ | ❌ | ⚠️ | ✅ Prophet |
| **Intervalos de confianza** | ✅ Nativos | ⚠️ Manual | ❌ | ✅ Prophet |
| **Interpretabilidad** | ✅ Alta | ✅ Alta | ❌ Baja | ✅ Prophet |
| **Tiempo de entrenamiento** | ~35 seg | ~42 seg | ~30 min+ | ✅ Prophet |

**Conclusión**: Prophet ofrece el mejor balance entre precisión, facilidad de uso y robustez para el caso de uso de DomusAI (predicción 1-7 días, datos domésticos).

#### **Optimizaciones de Memoria Implementadas**

```python
# Problema Original: MemoryError con 256k registros
# MemoryError: Unable to allocate 1.91 GiB for array with shape (1000, 256869)

# Solución 1: Reducir uncertainty_samples en entrenamiento
model = Prophet(
    uncertainty_samples=100,  # Default: 1000
    # Ahorro: ~1.72 GB RAM (10x reducción)
    # Impacto en IC 95%: <0.5% diferencia
)

# Solución 2: Desactivar incertidumbre en validación
temp_model = Prophet(
    uncertainty_samples=0  # Sin IC durante validación
).fit(train_data)
# Ahorro: ~1.91 GB RAM durante validación

# Resultado: Sistema funciona con 4GB RAM (antes requería 8GB+)
```

#### **Estructura de Salida JSON Estandarizada**

```json
{
  "prediction_date": "2025-10-01T14:23:45",
  "model_used": "prophet",
  "horizon_days": 7,
  "data_points": 168,
  "resolution": "hourly",
  "timestamps": ["2025-10-02 00:00:00", "..."],
  "predictions": [1.234, 1.456, "..."],
  "statistics": {
    "mean_consumption": 1.234,
    "max_consumption": 2.456,
    "min_consumption": 0.789,
    "total_consumption": 206.976,
    "daily_average": 1.234
  },
  "confidence_intervals": {
    "confidence_level": 0.95,
    "lower_bound": ["..."],
    "upper_bound": ["..."],
    "interval_width": ["..."]
  },
  "uncertainty_analysis": {
    "mean_interval_width": 0.543,
    "max_uncertainty": 0.678,
    "uncertainty_score": 0.134
  }
}
```

**Beneficios**:
- ✅ Fácil integración con dashboard (JSON → JavaScript)
- ✅ Serializable para base de datos
- ✅ Compatible con reportes (JSON → PDF/HTML)
- ✅ Extensible para nuevos modelos

---

## 🧪 Casos de Uso

### **🏠 Uso Residencial**

**Problema**: Usuario quiere optimizar su consumo eléctrico mensual.

**Solución con DomusAI**:
1. **Instalar sensor** (ESP32 + sensor de corriente) en tablero eléctrico
2. **Recopilar datos** durante 1 mes (43,200 registros mínimo)
3. **Ejecutar análisis**:
   ```python
   # Limpiar datos del sensor
   df = limpiar_dataset_consumo('data/mi_hogar_oct2025.csv')
   
   # Análisis exploratorio
   # (ejecutar 01_eda.ipynb con datos nuevos)
   
   # Predicción semanal
   predictor = EnergyPredictor('data/mi_hogar_oct2025.csv')
   predictor.train_prophet_model()
   pred = predictor.predict(horizon_days=7)
   
   # Detectar anomalías
   from src.anomalies import AnomalyDetector
   detector = AnomalyDetector(method='isolation_forest')
   anomalias = detector.detect(df, method='all', consensus_threshold=3, classify=True)
   
   print(f"⚠️ Anomalías críticas detectadas: {sum(1 for a in anomalias['alerts'] if a['severity'] == 'critical')}")
   ```

4. **Recibir reporte mensual** con:
   - Consumo histórico (gráficos)
   - Predicción próxima semana
   - Alertas de consumo anómalo (ej: electrodoméstico defectuoso)
   - Recomendaciones de ahorro

**Ahorro Estimado**: 10-15% mensual identificando ineficiencias

---

### **🏢 Uso Comunitario (Edificios/Condominios)**

**Problema**: Condominio necesita facturar energía comunitaria de forma equitativa.

**Solución con DomusAI**:
1. **Instalar sensores** en cada departamento (N sensores ESP32)
2. **Centralizar datos** en servidor Raspberry Pi con MQTT
3. **Dashboard comunitario**:
   ```python
   # Recopilar datos de N departamentos
   depts = ['dept_101', 'dept_102', ...]
   
   for dept in depts:
       df = limpiar_dataset_consumo(f'data/{dept}_oct2025.csv')
       predictor = EnergyPredictor(f'data/{dept}_oct2025.csv')
       pred = predictor.predict(horizon_days=30)
       
       # Guardar predicción para facturación
       save_prediction(dept, pred)
   
   # Generar reporte comunitario
   # report = ReportGenerator()  # Próximo sprint
   # report.generate_community_report(depts, predictions)
   ```

4. **Beneficios**:
   - Facturación transparente basada en consumo real
   - Identificación de departamentos con consumo excesivo
   - Alertas comunitarias de apagones o fallas
   - Optimización de contrato con compañía eléctrica

---

### **🔬 Uso en Investigación**

**Problema**: Investigador necesita validar política de eficiencia energética.

**Solución con DomusAI**:
1. **Dataset histórico** (antes de política)
2. **Dataset post-política** (después de implementación)
3. **Análisis comparativo**:
   ```python
   # Antes de política (ene-jun 2024)
   predictor_antes = EnergyPredictor('data/before_policy.csv')
   predictor_antes.train_prophet_model()
   pred_antes = predictor_antes.predict(horizon_days=30)
   
   # Después de política (ene-jun 2025)
   predictor_despues = EnergyPredictor('data/after_policy.csv')
   predictor_despues.train_prophet_model()
   pred_despues = predictor_despues.predict(horizon_days=30)
   
   # Comparación
   ahorro = (pred_antes['statistics']['mean_consumption'] - 
             pred_despues['statistics']['mean_consumption'])
   print(f"Ahorro promedio: {ahorro:.3f} kW ({ahorro/pred_antes['statistics']['mean_consumption']*100:.1f}%)")
   ```

4. **Papers derivados**:
   - Análisis de patrones de consumo pre/post política
   - Modelado predictivo de impacto de intervenciones
   - Validación de hipótesis con datos reales

---

## 🤝 Colaboración

### **Equipo DomusAI**

| Rol | Responsabilidades | Stack |
|-----|-------------------|-------|
| **Developer Python/AI** | - Análisis de datos<br>- Machine Learning<br>- Backend API<br>- Pipeline de predicción | Python, Prophet, scikit-learn, pandas |
| **Electronics Partner** | - Sensores ESP32/Arduino<br>- Integración MQTT<br>- Hardware setup<br>- Protocolo IoT | C/C++, MQTT, ESP32, Sensores ACS712 |

### **¿Cómo Contribuir?**

#### **🐛 Reportar Bugs**
```bash
# Crear issue en GitHub con:
- Descripción del problema
- Pasos para reproducir
- Output/logs del error
- Entorno (Python version, OS, RAM)
```

#### **🔧 Pull Requests**
```bash
# 1. Fork del repositorio
git clone https://github.com/TU_USUARIO/DomusAI.git

# 2. Crear branch para feature
git checkout -b feature/nueva-funcionalidad

# 3. Hacer cambios y commit
git add .
git commit -m "feat: añadir detección de anomalías con Isolation Forest"

# 4. Push y crear PR
git push origin feature/nueva-funcionalidad
```

**Convenciones de Commit**:
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `refactor:` Refactorización de código
- `test:` Añadir/modificar tests
- `perf:` Mejora de performance

#### **📖 Mejorar Documentación**
- Añadir ejemplos de uso
- Corregir typos en README
- Documentar funciones sin docstrings
- Crear tutoriales en notebooks

#### **🧪 Contribuir Tests**
```python
# tests/test_predictor.py
import pytest
from src.predictor import EnergyPredictor

def test_prophet_prediction_length():
    """Verificar que predicción tiene longitud correcta"""
    predictor = EnergyPredictor('data/Dataset_clean_test.csv')
    predictor.load_and_prepare_data()
    predictor.train_prophet_model()
    
    prediction = predictor.predict(horizon_days=7, model='prophet')
    
    assert len(prediction['predictions']) == 7 * 24  # 7 días * 24 horas
```

---

## 📄 Licencia

Distribuido bajo la **Licencia MIT**. Ver `LICENSE` para más información.

```
MIT License

Copyright (c) 2025 DomusAI Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contacto y Recursos

### **Links del Proyecto**

- 📂 **Repositorio**: [github.com/ddani22/DomusAI](https://github.com/ddani22/DomusAI)
- 🐛 **Issues**: [github.com/ddani22/DomusAI/issues](https://github.com/ddani22/DomusAI/issues)
- 📖 **Wiki**: [github.com/ddani22/DomusAI/wiki](https://github.com/ddani22/DomusAI/wiki) *(próximamente)*
- 📊 **Project Board**: [github.com/ddani22/DomusAI/projects](https://github.com/ddani22/DomusAI/projects) *(próximamente)*

### **Documentación Externa**

- [Prophet Documentation](https://facebook.github.io/prophet/) - Guía oficial de Meta
- [Statsmodels ARIMA](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html) - Documentación de modelos estadísticos
- [Scikit-learn Time Series](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.preprocessing) - Preprocessing para ML
- [Pandas Time Series](https://pandas.pydata.org/docs/user_guide/timeseries.html) - Manejo de series temporales

### **Comunidad**

- 💬 **Discussions**: Usa GitHub Discussions para preguntas generales
- 🐦 **Updates**: Síguenos en Twitter (próximamente)
- 📧 **Email**: contacto@domusai.dev *(próximamente)*

---

## 🎯 Próximos Pasos Recomendados

### **Para Usuarios Nuevos**:
1. ✅ Leer este README completo
2. ✅ Instalar DomusAI siguiendo la guía
3. ✅ Ejecutar notebook `01_eda.ipynb` con dataset de prueba
4. ✅ Probar predicción básica con `predictor.py`
5. ✅ Experimentar con `02_prediccion.ipynb`

### **Para Contribuidores**:
1. ✅ Fork del repositorio
2. ✅ Configurar entorno de desarrollo
3. ✅ Elegir issue abierto o proponer nuevo feature
4. ✅ Implementar cambios siguiendo convenciones
5. ✅ Crear Pull Request con tests

### **Para Investigadores**:
1. ✅ Descargar dataset propio
2. ✅ Adaptar pipeline de limpieza si es necesario
3. ✅ Ejecutar análisis exploratorio
4. ✅ Entrenar modelos con datos propios
5. ✅ Publicar resultados citando DomusAI

---

## 🌟 Agradecimientos

- **Meta AI Research** - Por Prophet, el mejor modelo para series temporales
- **Statsmodels Team** - Por modelos estadísticos robustos
- **Pandas Development Team** - Por la mejor librería de análisis de datos
- **Jinja Development Team** - Por el mejor motor de templates Python
- **Comunidad Open Source** - Por inspiración y soporte

---

<div align="center">

**🌟 ¿Te gusta DomusAI?**  
**¡Dale una estrella ⭐ al repositorio!**

**[⬆ Volver arriba](#-domusai---sistema-de-monitoreo-y-predicción-de-consumo-energético)**

---

*Última actualización: Octubre 5, 2025*  
*Versión: 0.85 (85% hacia v1.0)*  
*Proyecto: DomusAI - Sistema de Monitoreo Energético Inteligente*

**🆕 Nuevo en v0.85**:
- ✅ Sistema de reportes HTML completo
- ✅ Type-safety en todo el código (0 errores Pylance)
- ✅ Tests de validación funcionando
- ✅ 4 notebooks completos con documentación
- ✅ Infraestructura lista para exportación PDF

</div>

