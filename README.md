# 🏠 DomusAI - Sistema Inteligente de Monitoreo y Predicción Energética

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Prophet](https://img.shields.io/badge/Prophet-1.1.5-green)
![Status](https://img.shields.io/badge/Status-Production_Operational-brightgreen)
![License](https://img.shields.io/badge/License-Not_Specified-lightgrey)
![Progress](https://img.shields.io/badge/Progress-100%25-brightgreen)

**DomusAI** es un sistema completo de análisis predictivo de consumo energético doméstico y comunitario que combina técnicas avanzadas de *machine learning*, detección automatizada de anomalías, generación de reportes profesionales, notificaciones por email automáticas y sistema de scheduler 24/7. Diseñado para optimizar el uso de energía mediante predicciones de series temporales con Prophet, clasificación inteligente de patrones anómalos y automatización completa de reportes periódicos.

> 🎯 **Estado Actual**: ✅ **Sistema 100% Completo - Operacional en Producción** | **Versión:** v1.0 | **Sistema End-to-End**: ESP32 → Railway MySQL → Python AI

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

### ✅ **Implementadas**

#### 📊 **Análisis de Datos Completo**
- ✅ **Procesamiento automatizado** de datasets de consumo eléctrico
- ✅ **Limpieza inteligente** con manejo de valores faltantes y conversión de formatos de fecha
- ✅ **Análisis exploratorio completo** (EDA) con identificación de patrones temporales
- ✅ **Exportación de insights** a JSON para reutilización en pipeline
- ✅ **Generador de datos sintéticos ultra-realista**: 4 años de datos (2.1M registros) calibrados para España

#### 🔮 **Sistema de Predicción Avanzado**
- ✅ **Modelos múltiples**: Prophet (principal), ARIMA (validación), Prophet Enhanced
- ✅ **Predicciones escalables**: 1 hora hasta 30 días
- ✅ **Intervalos de confianza**: 95% configurables con análisis de incertidumbre
- ✅ **Optimización de memoria**: Reducción de 1.8 GB RAM en datasets grandes
- ✅ **Validación temporal robusta**: Split 80/20 con métricas MAE, RMSE, MAPE, R²
- ✅ **Validación física**: Clamp a 0.05 kW mínimo (100% predicciones válidas)
- ✅ **Test scripts optimizados**: test_prediction_fast.py (0.04s vs 240s)
- ✅ **API modular**: Integración fácil con otros sistemas

#### ⚠️ **Sistema de Detección de Anomalías**
- ✅ **Detección multi-método**: 5 algoritmos (IQR, Z-Score, Isolation Forest, Moving Average, Prediction-Based)
- ✅ **Consenso inteligente**: Reduce falsos positivos combinando ≥3 métodos
- ✅ **Clasificación por tipos**: 4 categorías (Consumo Alto, Bajo, Temporal, Fallo Sensor)
- ✅ **Sistema de alertas**: Severidad automática (crítico, medio, bajo)
- ✅ **Exportación automática**: CSV + JSON con timestamp
- ✅ **Notebook completo**: 34 celdas de experimentación y validación
- ✅ **Producción lista**: Módulo robusto de 1,060+ líneas con logging UTF-8

#### 📋 **Sistema de Reportes HTML/PDF** ✨
- ✅ **Generación HTML automática**: Templates Jinja2 profesionales con CSS moderno
- ✅ **Resumen ejecutivo**: KPIs principales, cambio mensual, score de eficiencia
- ✅ **Visualizaciones embebidas**: Gráficos matplotlib en PNG de alta resolución
- ✅ **Análisis temporal completo**: Consumo diario, horario, distribución semanal
- ✅ **Recomendaciones inteligentes**: Sistema de sugerencias basado en patrones
- ✅ **Exportación PDF**: Conversión HTML→PDF optimizada para impresión (340 KB típico)
- ✅ **Infraestructura completa**: Assets (logos, iconos), templates, CSS profesional
- ✅ **Producción lista**: Módulo de 968+ líneas con logging completo y exportación PDF
- ✅ **Validado**: Tests generan reportes HTML+PDF exitosamente (~1.5s)

#### 📧 **Sistema de Email Automático** ✨
- ✅ **EmailReporter completo**: Clase robusta de 700+ líneas con SMTP/TLS
- ✅ **Templates HTML profesionales**: 
  - 📊 **Reporte Mensual**: 330 líneas HTML responsive, PDF adjunto
  - 🚨 **Alerta de Anomalía**: 350+ líneas, diseño urgente por severidad
  - 📈 **Reportes Diario/Semanal**: Templates optimizados
  - 🔄 **Notificación Reentrenamiento**: Métricas de modelos
- ✅ **Métodos especializados**:
  - `send_monthly_report()`: PDFs adjuntos, estadísticas completas
  - `send_anomaly_alert()`: Alertas críticas con recomendaciones
- ✅ **Configuración segura**: Variables .env, SMTP con autenticación Gmail
- ✅ **Sistema de logging**: UTF-8 compatible, timestamps, debugging completo
- ✅ **Integración completa**: `generate_and_send_monthly_report()` - pipeline end-to-end
- ✅ **Multi-destinatario**: Envío simultáneo a múltiples emails
- ✅ **Validado en producción**: Tests reales confirman entrega exitosa (3-4s típico)

#### 🤖 **Sistema de Auto-Training y Scheduler** ✅ (Sprint 8)
- ✅ **Scheduler 24/7**: APScheduler con 5 jobs automáticos configurados
- ✅ **Job #1 - Detección Horaria**: Anomalías cada 60 minutos con Railway MySQL
- ✅ **Job #2 - Re-entrenamiento**: Diario 3 AM, ejecución cada 7 días
  - Prophet + Isolation Forest re-training automático
  - Validación con últimos 30 días de datos
  - Backup automático de modelos previos con versionado
  - Comparación inteligente: Solo actualiza producción si mejora métricas
  - Notificación por email con métricas (MAE, RMSE, R²)
- ✅ **Job #3 - Reporte Diario**: 8 AM, HTML con últimas 24h
- ✅ **Job #4 - Reporte Semanal**: Lunes 9 AM, análisis semanal completo
- ✅ **Job #5 - Reporte Mensual**: Día 1 del mes 10 AM, HTML+PDF con adjuntos
- ✅ **Inicialización automática**: `initialize_models.py` crea modelos iniciales
- ✅ **Configuración YAML**: `config/scheduler_config.yaml` editable
- ✅ **Windows Task Scheduler**: XML para arranque automático con sistema
- ✅ **Logging centralizado**: Todos los jobs escriben a logs/scheduler.log
- ✅ **Testing acelerado**: `test_scheduler_fast.py` valida jobs en 10 minutos

#### 🔌 **Integración IoT ESP32 → Python** ✅ (Sprint 9)
- ✅ **Hardware ESP32 completo**: Sensores ACS712 calibrados y operacionales
- ✅ **Envío a Railway MySQL**: ESP32 inserta lecturas directamente cada 60s
- ✅ **Lectura automática**: Scheduler Python consume datos de Railway en tiempo real
- ✅ **Pipeline end-to-end**: ESP32 → Railway → Prophet → Alertas → Email
- ✅ **Sistema operacional**: Funcionando 24/7 con datos reales de sensores
- ✅ **Railway MySQL Integration**: Queries automáticas a base de datos en producción

#### 🧪 **Testing y Validación** ✨
- ✅ **test_prediction_fast.py**: Predicciones optimizadas (0.04s, loads pre-trained models)
- ✅ **test_send_real_email.py**: Validación completa de email con datos sintéticos
- ✅ **test_anomalies_railway.py**: Tests de detección con Railway MySQL
- ✅ **test_predictor_railway.py**: Tests de Prophet con datos de producción
- ✅ **test_reporting_railway.py**: Tests de generación HTML/PDF
- ✅ **test_auto_trainer.py**: Validación de re-entrenamiento automático
- ✅ **test_scheduler_jobs.py**: Tests de todos los jobs del scheduler
- ✅ **test_email_templates.py**: Validación de templates Jinja2

#### 📈 **Visualización y Análisis**
- ✅ **Gráficos interactivos** con Plotly (notebooks)
- ✅ **Análisis temporal**: Patrones diarios, semanales y estacionales
- ✅ **Correlaciones energéticas** entre variables del sistema
- ✅ **Componentes de estacionalidad** visualizables (Prophet)
- ✅ **Visualización de anomalías** por método y tipo

#### � **Documentación Completa** ✨ (NUEVO)
- ✅ **README.md**: Guía completa de instalación, uso y arquitectura
- ✅ **ARCHITECTURE.md**: Documentación detallada del sistema de producción
  - 950 líneas de documentación técnica
  - Flujos completos de los 5 jobs del scheduler
  - Estructura de archivos con tamaños y propósitos
  - Diagramas de flujo de datos en ASCII
  - Timeline de 24 horas de operación
  - Comandos de producción y monitoreo
- ✅ **copilot-instructions.md**: Guía para asistentes AI sobre el proyecto
- ✅ **synthetic_data_generator/README.md**: Documentación del generador de datos

---

## 🔧 Stack Tecnológico

### **Core Analytics & Data Processing**
```python
pandas==2.3.2          # Manipulación de series temporales
numpy==2.3.3           # Computación numérica de alto rendimiento  
matplotlib==3.10.6     # Visualización base para reportes
seaborn==0.13.2        # Visualización estadística avanzada
plotly==5.15.0         # Gráficos interactivos en notebooks
jinja2==3.1.6          # Templates HTML para reportes y emails ✨
xhtml2pdf==0.2.16      # Conversión HTML → PDF ✨
```

### **Machine Learning & Forecasting**
```python
scikit-learn==1.7.2    # Algoritmos ML (IsolationForest), métricas y validación
prophet==1.1.5         # Series temporales con estacionalidad automática (Meta/Facebook)
statsmodels==0.14.5    # Modelos estadísticos clásicos (ARIMA, SARIMAX)
joblib==1.5.2          # Serialización eficiente de modelos (3-10x más rápido que pickle)
```

### **Email & Automation** ✨
```python
python-dotenv==1.0.0   # Variables de entorno para credenciales SMTP
APScheduler==3.10.4    # Scheduler avanzado para jobs automáticos (5 jobs configurados) ✨
smtplib                # Protocolo SMTP nativo (incluido en Python)
email.mime             # Composición de emails con adjuntos (incluido en Python)
```

### **Database & IoT**
```python
mysql-connector-python==9.2.0  # Conector Railway MySQL para producción ✨
paho-mqtt==1.6.1              # Protocolo MQTT para ESP32 (próximo sprint)
```

### **Optimization & Performance**
```python
optuna==4.5.0          # Optimización automática de hiperparámetros (futuro)
memory-profiler==0.61.0 # Profiling de memoria para datasets grandes
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
holidays==0.81                # Días festivos españoles para variables exógenas
pyyaml==6.0.2                 # Configuración YAML para scheduler ✨
```

---

## 📂 Estructura del Proyecto

### **Directorio Actual** (Octubre 2025)

```
DomusAI/
│
├── 📁 .github/                      # Configuración de GitHub
│   └── copilot-instructions.md          # ✅ Instrucciones completas para AI assistants (Sprint 8)
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
│   ├── 04_reportes.ipynb                # ✅ Sistema de reportes (28 celdas)
│   └── logs/                            # 📝 Logs de ejecución de notebooks
│       └── predictions.log
│
├── 📁 src/                          # ✅ COMPLETO (8/8 módulos) ✨
│   ├── data_cleaning.py                 # ✅ Sistema de limpieza completo (312 líneas)
│   │                                    #    - Conversión fechas 2→4 dígitos
│   │                                    #    - Manejo de '?' y nulos
│   │                                    #    - Validación de datos
│   │
│   ├── predictor.py                     # ✅ Motor de predicción (1,561 líneas)
│   │                                    #    - Prophet (modelo principal, MAE=0.179 kW)
│   │                                    #    - ARIMA (validación)
│   │                                    #    - Prophet Enhanced (mejorado)
│   │                                    #    - Validación temporal automática
│   │                                    #    - Intervalos de confianza
│   │                                    #    - Optimización de memoria (ahorra 1.8 GB)
│   │                                    #    - Validación física (clamp 0.05 kW mínimo)
│   │
│   ├── anomalies.py                     # ✅ Sistema de detección de anomalías (1,060 líneas)
│   │                                    #    - 5 métodos (IQR, Z-Score, IF, MA, Prediction-Based)
│   │                                    #    - Consenso multi-método (≥3 para alta confianza)
│   │                                    #    - Clasificación en 4 tipos
│   │                                    #    - Sistema de alertas por severidad
│   │                                    #    - Exportación automática CSV + JSON
│   │
│   ├── reporting.py                     # ✅ Generador de reportes HTML/PDF (968 líneas) ✨
│   │                                    #    - Templates Jinja2 profesionales
│   │                                    #    - Resumen ejecutivo con KPIs
│   │                                    #    - Gráficos matplotlib embebidos
│   │                                    #    - Sistema de recomendaciones
│   │                                    #    - Exportación HTML + PDF (340 KB típico)
│   │                                    #    - Integración con email_sender.py
│   │
│   ├── email_sender.py                  # ✅ Sistema de email automático (702 líneas) ✨
│   │                                    #    - EmailReporter class con SMTP/TLS
│   │                                    #    - send_monthly_report() con PDF adjunto
│   │                                    #    - send_anomaly_alert() por severidad
│   │                                    #    - Templates HTML profesionales integrados
│   │                                    #    - Configuración .env segura
│   │                                    #    - Multi-destinatario simultáneo
│   │
│   ├── auto_trainer.py                  # ✅ Sistema de auto-training (500+ líneas) ✨
│   │                                    #    - Re-entrenamiento automático Prophet + IF
│   │                                    #    - Validación con últimos 30 días
│   │                                    #    - Backup automático de modelos
│   │                                    #    - Notificación por email con métricas
│   │
│   ├── config.py                        # ✅ Configuración centralizada (400+ líneas) ✨
│   │                                    #    - PathConfig: Rutas centralizadas
│   │                                    #    - MLConfig: Hiperparámetros optimizados
│   │                                    #    - DatabaseConfig: Railway MySQL credentials
│   │                                    #    - EnergyConstants: Dominio español (230V, IDAE)
│   │
│   ├── database.py                      # ✅ Conexión Railway MySQL (300+ líneas) ✨
│   │                                    #    - Query builder para energy_readings
│   │                                    #    - Connection pooling
│   │                                    #    - Fallback a CSV si DB vacía
│   │
│   ├── setup_railway_db.py              # ✅ Script de inicialización DB ✨
│   ├── validators.py                    # ✅ Validadores de datos (200+ líneas) ✨
│   ├── exceptions.py                    # ✅ Excepciones personalizadas ✨
│   └── __pycache__/                     # Cache de Python (ignorado en Git)
│
├── 📁 logs/                         # ✅ Sistema de logging UTF-8 activo
│   ├── predictions.log                  # Registro de predicciones y errores
│   ├── anomalies.log                    # Registro de detección de anomalías
│   ├── reporting.log                    # Registro de generación de reportes ✨
│   ├── email_sender.log                 # Registro de envío de emails ✨
│   ├── scheduler.log                    # Registro del scheduler 24/7 ✨ (NUEVO)
│   └── metrics_history.json             # Historial de métricas de modelos ✨ (NUEVO)
│
├── 📁 models/                       # ✅ Modelos ML pre-entrenados ✨ (NUEVO)
│   ├── best_prophet.pkl                 # Prophet v20251102_163825 (204 MB, MAE=0.179 kW)
│   ├── best_isolation_forest.pkl        # IsolationForest (1.48 MB, 100 estimators)
│   ├── training_history.json            # Historial de entrenamiento con métricas
│   └── backups/                         # Backups automáticos de modelos previos
│
├── 📁 reports/                      # ✅ INFRAESTRUCTURA COMPLETA ✨
│   ├── templates/                       # ✅ Plantillas Jinja2
│   │   ├── monthly_report.html          # Template principal de reporte
│   │   └── sections/                    # Secciones reutilizables
│   ├── styles/                          # ✅ Estilos CSS profesionales
│   │   └── report_styles.css            # CSS moderno con variables
│   ├── assets/                          # ✅ Recursos estáticos
│   │   ├── fonts/                       # Fuentes personalizadas
│   │   └── icons/                       # Iconos SVG
│   ├── email_templates/                 # ✅ 5 Templates de email ✨
│   │   ├── monthly_report_email.html    # 📊 Reporte mensual (330 líneas)
│   │   ├── email_weekly_report.html     # 📈 Reporte semanal ✨
│   │   ├── email_daily_report.html      # 📅 Reporte diario ✨
│   │   ├── email_model_retrained.html   # 🔄 Notificación reentrenamiento ✨
│   │   └── anomaly_alert_email.html     # 🚨 Alerta crítica (350+ líneas)
│   └── generated/                       # ✅ Reportes y emails generados
│       ├── reporte_*.html               # Reportes HTML (220 KB típico)
│       └── reporte_*.pdf                # Reportes PDF (340 KB típico) ✨
│
├── 📁 scripts/                      # ✅ Scripts de automatización ✨ (ACTUALIZADO)
│   ├── initialize_models.py             # ✅ Inicialización de modelos (one-time setup)
│   ├── auto_training_scheduler.py       # ✅ Scheduler 24/7 con 5 jobs automáticos ✨
│   ├── domusai_scheduler_task.xml       # ✅ Config Windows Task Scheduler ✨
│   ├── validate_config.py               # ✅ Validación scheduler_config.yaml
│   └── validate_email_config.py         # ✅ Validación configuración email
│
├── 📁 tests/                        # ✅ Suite de tests completa ✨ (ACTUALIZADO)
│   ├── test_prediction_fast.py          # ✅ Tests predicción optimizados (0.04s) ✨
│   ├── test_send_real_email.py          # ✅ Tests email con datos sintéticos ✨
│   ├── test_anomalies_railway.py        # ✅ Tests detección anomalías + Railway
│   ├── test_predictor_railway.py        # ✅ Tests predictor con Railway
│   ├── test_reporting_railway.py        # ✅ Tests sistema reportes
│   ├── test_auto_trainer.py             # ✅ Tests auto-training ✨
│   ├── test_scheduler_jobs.py           # ✅ Tests scheduler 5 jobs ✨
│   └── test_email_templates.py          # ✅ Tests templates email
│
├── 📁 synthetic_data_generator/     # ✅ Generador datos ultra-realista ✨ (MEJORADO)
│   ├── README.md                        # Documentación completa generador
│   ├── ANALYSIS_4YEARS.md               # ✅ Análisis de 4 años de datos ✨
│   ├── config.yaml                      # Configuración patrones españoles
│   ├── generate_consumption_data.py     # Generador principal (949 líneas)
│   │                                    #    - 4 años de datos (2.1M registros, 131 MB)
│   │                                    #    - Patrones vacaciones españolas
│   │                                    #    - Calibrado IDAE (0.40-0.52 kW promedio)
│   │                                    #    - Sub-metering coherente
│   │                                    #    - Validaciones físicas (Ley de Ohm)
│   ├── visualize_data.ipynb             # Notebook visualización
│   ├── examples/
│   │   └── insert_to_railway.py         # Script inserción Railway MySQL
│   └── output/                          # CSVs generados
│       └── synthetic_1460days_*.csv     # Dataset 4 años (131 MB) ✨
│
├── 📁 config/                       # ✅ Configuración del sistema ✨
│   └── scheduler_config.yaml            # Configuración 5 jobs automáticos
│
├── 📁 .venv/                        # 🐍 Entorno virtual Python (ignorado)
│
├── 📄 .env                          # ✅ Variables de entorno (SMTP, Railway MySQL) ✨
├── 📄 .env.example                  # ✅ Template configuración
├── 📄 .gitignore                    # ✅ Configuración Git
├── 📄 README.md                     # ✅ Documentación completa (este archivo) ✨
├── 📄 ARCHITECTURE.md               # ✅ Arquitectura de producción (950 líneas) ✨ (NUEVO)
└── 📄 requirements.txt              # ✅ Dependencias actualizadas (30+ paquetes) ✨
```

### **Progreso por Componente**

| Componente | Archivos | Estado | Líneas | Completado | Prioridad |
|------------|----------|--------|--------|------------|-----------|
| **📊 Data Pipeline** | 3 archivos | ✅ | ~600 | 100% | ✅ Alta |
| **📓 EDA Notebooks** | 4/4 archivos | ✅ | ~146 celdas | 100% | ✅ Alta |
| **🔮 Predictor** | 1 archivo | ✅ | 1,561 | 100% | ✅ Alta |
| **⚠️ Anomalías** | 2/2 archivos | ✅ | 1,060 + 34 celdas | 100% | ✅ Alta |
| **📋 Reportes HTML/PDF** | 1 archivo | ✅ | 968 + 28 celdas | 100% | ✅ Alta |
| **📧 Email Automation** | 1 archivo | ✅ | 702 | 100% | ✅ Alta |
| **🤖 Auto-Training** | 2 archivos | ✅ | ~1000 | 100% | ✅ Alta |
| **🔄 Scheduler 24/7** | 1 archivo | ✅ | ~500 | 100% | ✅ Alta |
| **🗄️ Railway MySQL** | 2 archivos | ✅ | ~400 | 100% | ✅ Alta |
| **🧪 Testing Suite** | 8 archivos | ✅ | ~1200 | 100% | 🔵 Alta |
| **📁 Config System** | 1 archivo | ✅ | ~400 | 100% | ✅ Alta |
| **🔌 IoT Hardware (ESP32)** | Hardware | ✅ | N/A | 100% | ✅ Alta |
| **🔌 IoT Integration** | Python↔ESP32 | ✅ | ~200 | 100% | ✅ Alta |

**📊 Progreso Total: 100/100%** - DomusAI v1.0 Completo

**Sprint 9 (Completado)**: Integración Final IoT (ESP32 → Railway MySQL → Python AI)

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
████████████████████████████████████████████ 95% Completado

Fases:
✅ Data Cleaning        [████████████████████] 100%
✅ EDA & Analysis       [████████████████████] 100%
✅ Prediction Models    [████████████████████] 100%
✅ Anomaly Detection    [████████████████████] 100%
✅ HTML Reports         [████████████████████] 100%
✅ PDF Export           [████████████████████] 100%
✅ Email Automation     [████████████████████] 100%
✅ Auto-Training System [████████████████████] 100%
✅ Scheduler 24/7       [████████████████████] 100%
✅ Railway MySQL        [████████████████████] 100%
✅ Synthetic Data Gen   [████████████████████] 100%
✅ Testing & Validation [████████████████████] 100%
✅ Documentation        [████████████████████] 100%
✅ IoT Hardware (ESP32) [████████████████████] 100% ← Electronics Partner Completado
✅ IoT Integration      [████████████████████] 100% ← Sprint 9 Completado 🎉
```

### **✅ Hitos Completados**

- [x] **Sprint 0: Configuración del Proyecto** (Semana 1)
  - [x] Estructura de carpetas
  - [x] Entorno virtual Python 3.12
  - [x] Dependencias instaladas (30+ paquetes)
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
  - [x] Validación temporal automática (80/20 split)
  - [x] Intervalos de confianza del 95%
  - [x] Optimización de memoria (ahorro 1.8 GB RAM)
  - [x] Validación física: clamp 0.05 kW mínimo (100% predicciones válidas)
  - [x] Test script optimizado: test_prediction_fast.py (0.04s ejecución)
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
  - [x] Logging UTF-8 compatible con Windows PowerShell
  - [x] Parámetros óptimos validados experimentalmente

- [x] **Sprint 5: Sistema de Reportes HTML** (Semana 8)
  - [x] Infraestructura completa de reportes creada
  - [x] Módulo `reporting.py` (968 líneas) - Generación HTML
  - [x] Templates Jinja2 profesionales con CSS moderno
  - [x] Resumen ejecutivo con KPIs (consumo, cambio mensual, eficiencia)
  - [x] Gráficos matplotlib embebidos (PNG de alta resolución)
  - [x] Sistema de recomendaciones inteligentes basado en patrones
  - [x] Notebook `04_reportes.ipynb` (28 celdas) - Experimentación completa
  - [x] Type-safety completo (0 errores Pylance)
  - [x] Logging UTF-8 compatible con Windows
  - [x] Assets (logos, iconos SVG, CSS)
  - [x] Test validado: Reporte junio 2007 generado exitosamente (~2s)

- [x] **Sprint 6: Sistema de Exportación PDF** (Semana 9)
  - [x] Integración xhtml2pdf para conversión HTML→PDF
  - [x] Optimización CSS para impresión (media queries)
  - [x] Función `generate_monthly_report_with_pdf()` 
  - [x] CSS específico para saltos de página apropiados
  - [x] Metadatos PDF automáticos (título, autor, fecha)
  - [x] Test de generación: PDF de 340 KB funcional
  - [x] Tiempo de generación optimizado (~1.5s HTML+PDF)

- [x] **Sprint 7: Sistema de Email Automático** (Semanas 10-11)
  - [x] Clase `EmailReporter` (702 líneas) con SMTP/TLS seguro
  - [x] Templates HTML profesionales para emails:
    - [x] `monthly_report_email.html` (330 líneas) - Reporte mensual responsive
    - [x] `anomaly_alert_email.html` (350+ líneas) - Alertas críticas por severidad
    - [x] `email_daily_report.html` - Reporte diario
    - [x] `email_weekly_report.html` - Reporte semanal
    - [x] `email_model_retrained.html` - Notificación reentrenamiento
  - [x] Métodos especializados de envío:
    - [x] `send_monthly_report()` - PDF adjunto + estadísticas completas
    - [x] `send_anomaly_alert()` - Alertas por severidad (critical/warning/medium)
    - [x] `quick_send_test_email()` - Pruebas de configuración
  - [x] Configuración segura con variables .env (SMTP Gmail)
  - [x] Sistema de logging UTF-8 completo (`email_sender.log`)
  - [x] Integración con `reporting.py`:
    - [x] `generate_and_send_monthly_report()` - Pipeline end-to-end
    - [x] `send_anomaly_alert_pipeline()` - Alertas automáticas
  - [x] Multi-destinatario simultáneo desde configuración
  - [x] Suite de tests completa:
    - [x] `test_email_templates.py` - Validación de templates HTML
    - [x] `test_send_real_email.py` - Tests con emails reales (220 KB HTML + 340 KB PDF)
  - [x] Validación en producción: **Emails enviados exitosamente**

- [x] **Sprint 8: Auto-Training y Scheduler 24/7** (Semanas 12-14) ✨
  - [x] **Inicialización de Modelos**:
    - [x] Script `initialize_models.py` para setup inicial
    - [x] Bug fixes: Path handling + quality validation
    - [x] Modelos creados: best_prophet.pkl (204 MB), best_isolation_forest.pkl (1.48 MB)
    - [x] Métricas: MAE=0.179 kW, RMSE=0.252 kW, R²=0.660
  - [x] **Sistema de Auto-Training**:
    - [x] Módulo `auto_trainer.py` (500+ líneas)
    - [x] Re-entrenamiento automático Prophet + Isolation Forest
    - [x] Validación con últimos 30 días de datos Railway
    - [x] Backup automático de modelos previos con timestamp
    - [x] Notificación por email con métricas de performance
    - [x] Fallback a CSV si Railway MySQL vacía
  - [x] **Scheduler APScheduler**:
    - [x] Script `auto_training_scheduler.py` (500+ líneas)
    - [x] **Job #1**: Detección de anomalías horaria (cada 60 min)
    - [x] **Job #2**: Re-entrenamiento diario 3 AM (ejecución cada 7 días)
    - [x] **Job #3**: Reporte diario 8 AM (HTML con últimas 24h)
    - [x] **Job #4**: Reporte semanal lunes 9 AM (análisis completo)
    - [x] **Job #5**: Reporte mensual día 1 del mes 10 AM (HTML+PDF+Email)
    - [x] Configuración YAML: `config/scheduler_config.yaml`
    - [x] Windows Task Scheduler: `domusai_scheduler_task.xml`
    - [x] Logging centralizado: `logs/scheduler.log` UTF-8
  - [x] **Railway MySQL Integration**:
    - [x] Módulo `database.py` con connection pooling
    - [x] Schema `energy_readings` optimizado para ESP32
    - [x] Query builder para análisis temporal
    - [x] Fallback automático a CSV si DB vacía
    - [x] Tests: `test_anomalies_railway.py`, `test_predictor_railway.py`
  - [x] **Testing Completo**:
    - [x] `test_auto_trainer.py` - Validación re-entrenamiento
    - [x] `test_scheduler_jobs.py` - Tests de 5 jobs
    - [x] `test_prediction_fast.py` - Predicciones optimizadas (0.04s)
    - [x] `test_send_real_email.py` - Email con datos sintéticos
  - [x] **Generador de Datos Sintéticos Mejorado**:
    - [x] 4 años de datos (2,102,400 registros, 131 MB)
    - [x] Calibrado para España: 0.40-0.52 kW promedio (IDAE)
    - [x] Patrones vacaciones españolas (Agosto, Navidad, Semana Santa)
    - [x] Sub-metering coherente (Cocina 25%, Lavandería 8%, HVAC 30%)
    - [x] Validaciones físicas (Ley de Ohm, voltaje 225-238V)
    - [x] Análisis completo: `ANALYSIS_4YEARS.md`
  - [x] **Configuración y Utilidades**:
    - [x] Módulo `config.py` centralizado (400+ líneas)
    - [x] PathConfig, MLConfig, DatabaseConfig, EnergyConstants
    - [x] Módulo `validators.py` para validación de datos
    - [x] Módulo `exceptions.py` con excepciones personalizadas
  - [x] **Documentación Completa**:
    - [x] `ARCHITECTURE.md` (950 líneas) - Sistema de producción
    - [x] Flujos de los 5 jobs del scheduler
    - [x] Timeline de 24 horas de operación
    - [x] Comandos de producción y monitoreo
    - [x] `.github/copilot-instructions.md` actualizado

**Resultados Sprint 8**:
```python
# Sistema completamente operacional:
✅ Scheduler ejecutándose 24/7 con 5 jobs automáticos
✅ Auto-training cada 7 días con métricas y email
✅ Reportes diarios/semanales/mensuales automáticos
✅ Detección de anomalías horaria con Railway MySQL
✅ Datos sintéticos ultra-realistas (4 años, 2.1M registros)
✅ Testing completo: 8 archivos, ~1200 líneas
✅ Documentación técnica completa (README + ARCHITECTURE)
✅ Sistema 95% completo - Production Ready
```

### **📋 Roadmap Detallado**

### **🔄 Sprint Actual**

#### ✅ **Sprint 9: Integración Final IoT** - **COMPLETADO** 🎉

**Prioridad**: ALTA  
**Objetivo**: Conectar hardware ESP32 con sistema Python automático → ✅ **CUMPLIDO**

**Estado Hardware ESP32** ✅:
- ✅ ESP32 con sensores ACS712 configurado y funcional
- ✅ Código Arduino/C++ completado por Electronics Partner
- ✅ Lectura de potencia, voltaje, corriente operacional
- ✅ Tests de precisión hardware validados

**Integración Completada** ✅:
- ✅ **ESP32 → Railway MySQL**: Envío directo cada 60s
- ✅ **Scheduler Python Operacional**: Lee datos de Railway en tiempo real
- ✅ **Pipeline End-to-End Funcional**:
  ```
  ESP32 (Sensores ACS712)
      ↓ [60s intervals]
  Railway MySQL (INSERT)
      ↓ [Scheduler queries]
  Python AI (Prophet + Anomalies)
      ↓ [Auto-detection]
  Email Alerts (SMTP)
  ```
- ✅ **Sistema 24/7**: Operacional con datos reales de sensores
- ✅ **Validación Completa**: Flujo probado exitosamente

**Resultado**: Sistema completo operando en producción 🚀

---

## 🚀 Inicio Rápido

### **Requisitos del Sistema**

- **Python**: 3.12 o superior
- **RAM**: 4 GB mínimo (8 GB recomendado para datasets grandes)
- **Espacio en Disco**: 1 GB para entorno + datasets + modelos
- **SO**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Base de Datos**: Railway MySQL (opcional, configurado en `.env`)

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

# 4. Instalar dependencias (30+ paquetes)
pip install -r requirements.txt

# 5. Configurar variables de entorno
# Copiar .env.example a .env y configurar:
# - SMTP_EMAIL y SMTP_PASSWORD (para emails)
# - MYSQL_* variables (para Railway MySQL)
# - DEFAULT_RECIPIENTS (emails separados por coma)

# 6. Verificar instalación
python -c "from src.predictor import EnergyPredictor; from src.config import PATHS; print('✅ DomusAI instalado correctamente')"
```

### **Setup Inicial de Modelos** ✨ (NUEVO)

```bash
# IMPORTANTE: Ejecutar una vez antes del scheduler
python scripts/initialize_models.py

# Este script:
# 1. Busca el CSV sintético más reciente (synthetic_data_generator/output/)
# 2. Entrena Prophet + Isolation Forest
# 3. Guarda modelos en models/:
#    - best_prophet.pkl (204 MB)
#    - best_isolation_forest.pkl (1.48 MB)
# 4. Genera training_history.json con métricas
# 5. Tiempo: ~10-15 minutos

# Output esperado:
# ✅ Prophet entrenado: MAE=0.179 kW, RMSE=0.252 kW, R²=0.660
# ✅ IsolationForest entrenado: 100 estimators, 5% contamination
# ✅ Modelos guardados en models/
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

#### **3️⃣ Predicción Energética - Test Rápido** ✨ (NUEVO)

```bash
# Usar script optimizado (0.04s con modelos pre-entrenados)
python test_prediction_fast.py

# Output:
# ✅ Modelo Prophet cargado desde: models/best_prophet.pkl
# ✅ Predicción completada en 0.04 segundos
# 📊 Próximas 24 horas:
#    - Promedio: 0.512 kW
#    - Máximo: 0.972 kW (19:00)
#    - Mínimo: 0.134 kW (04:00)
# ✅ 100% predicciones físicamente válidas (≥0.05 kW)
```

#### **4️⃣ Predicción Energética - API Completa**

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

#### **5️⃣ Predicción con Intervalos de Confianza**

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

#### **6️⃣ Detección de Anomalías - API Simple**

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

#### **7️⃣ Generación de Reportes HTML/PDF** ✨

```python
from src.reporting import generate_and_send_monthly_report

# Opción 1: Solo generación (sin envío de email)
result = generate_and_send_monthly_report(
    data_path='data/Dataset_clean_test.csv',
    month=6,  # Junio
    year=2007,
    include_pdf=True,
    auto_send=False  # Solo generar reportes
)

print(f"✅ HTML generado: {result['html_path']}")
print(f"✅ PDF generado: {result['pdf_path']}")
print(f"📊 Consumo mensual: {result['consumption_kwh']:.2f} kWh")
print(f"📈 Cambio vs mes anterior: {result['change_percent']:.1f}%")
print(f"🎯 Score de eficiencia: {result['efficiency_score']}/100")

# Opción 2: Pipeline completo (generación + envío automático)
result = generate_and_send_monthly_report(
    data_path='data/Dataset_clean_test.csv',
    month=6,
    year=2007,
    include_pdf=True,
    auto_send=True  # Generar Y enviar por email
)

print(f"📧 Email enviado: {result['email_sent']}")
print(f"👥 Destinatarios: {len(result['email_recipients'])}")
print(f"⏱️ Tiempo total: {result['total_time']:.2f}s")

# El reporte incluye:
# - Resumen ejecutivo con KPIs
# - Gráficos de consumo diario embebidos
# - Análisis estadístico completo
# - Recomendaciones personalizadas automáticas
# - PDF de alta calidad (340 KB) adjunto al email
```

#### **8️⃣ Sistema de Email Automático** ✨

```python
from src.email_sender import EmailReporter
from src.reporting import send_anomaly_alert_pipeline

# Opción 1: Reporte mensual por email (ya mostrado arriba)
# Ver función generate_and_send_monthly_report()

# Opción 2: Alerta crítica de anomalía
anomaly_data = {
    'timestamp': '08/10/2025 14:30',
    'consumption_value': 5.234,
    'normal_average': 1.156,
    'deviation_percent': 352.8,
    'anomaly_type': 'tipo_1_consumo_alto',
    'confidence': 'Alta (96.7%)',
    'recommended_actions': [
        '🔌 ACCIÓN INMEDIATA: Verificar electrodomésticos',
        '⚡ Revisar cuadro eléctrico: interruptores',
        '📞 Si persiste >6h, contactar técnico'
    ]
}

result = send_anomaly_alert_pipeline(
    anomalies_data=anomaly_data,
    severity='critical'  # 'critical', 'warning', 'medium'
)

print(f"🚨 Alerta enviada: {result['email_sent']}")
print(f"👥 Destinatarios: {len(result['email_recipients'])}")

# Opción 3: Configuración manual de EmailReporter
emailer = EmailReporter()

# Email básico de prueba
success = emailer.quick_send_test_email('tu_email@example.com')

# Email con PDF personalizado
success = emailer.send_monthly_report(
    recipients=['destinatario@example.com'],
    pdf_path='reports/generated/mi_reporte.pdf',
    month=10, year=2025,
    summary_stats={
        'consumption_kwh': 450.25,
        'change_percent': -12.5,
        'efficiency_score': 85
    },
    recommendations=['Consejo 1', 'Consejo 2']
)
```

#### **9️⃣ Scheduler 24/7 - Automatización Completa** ✨ (NUEVO)

```bash
# PASO 1: Inicializar modelos (una vez)
python scripts/initialize_models.py

# PASO 2: Iniciar scheduler (mantener ejecutando)
python scripts/auto_training_scheduler.py

# El scheduler ejecuta automáticamente:
# ⏰ Cada hora:    Detección de anomalías (Railway MySQL)
# ⏰ Diario 3 AM:  Re-entrenamiento (cada 7 días)
# ⏰ Diario 8 AM:  Reporte diario (HTML con últimas 24h)
# ⏰ Lunes 9 AM:   Reporte semanal (análisis completo)
# ⏰ Día 1, 10 AM: Reporte mensual (HTML+PDF+Email)

# Logs en tiempo real:
# logs/scheduler.log       # Todos los jobs
# logs/predictions.log     # Predicciones
# logs/anomalies.log       # Anomalías detectadas
# logs/email_sender.log    # Emails enviados
```

**Configurar Windows Task Scheduler** (arranque automático con sistema):

```bash
# 1. Abrir Task Scheduler (taskschd.msc)
# 2. Importar XML: scripts/domusai_scheduler_task.xml
# 3. Editar rutas en el XML:
#    - Cambiar "C:\path\to\DomusAI" por tu ruta real
# 4. Credenciales: Tu usuario Windows
# 5. Trigger: Al iniciar sistema
# 6. ✅ Scheduler arrancará automáticamente con Windows
```

#### **🔟 Generar Datos Sintéticos** ✨ (NUEVO)

```bash
cd synthetic_data_generator

# Generar 4 años de datos (2.1M registros, 131 MB)
python generate_consumption_data.py --days 1460 --profile medium --start-date 2025-10-30

# Parámetros:
# --days: Cantidad de días (1460 = 4 años)
# --profile: low, medium, high (medium = hogar 3-4 personas)
# --start-date: Fecha inicial (formato YYYY-MM-DD)
# --validate: Validar datos generados

# Output: synthetic_data_generator/output/synthetic_1460days_TIMESTAMP.csv

# Características de los datos:
# ✅ Promedio 0.40-0.52 kW (calibrado IDAE España)
# ✅ Vacaciones españolas (Agosto, Navidad, Semana Santa)
# ✅ Horarios españoles (comidas 8h, 14h, 21h)
# ✅ Sub-metering coherente (Cocina, Lavandería, HVAC)
# ✅ Validación física completa (Ley de Ohm, voltaje 225-238V)
```

#### **1️⃣1️⃣ Ejecutar Tests de Validación** ✨

```bash
# Test 1: Predicción rápida (0.04s con modelo pre-entrenado)
python test_prediction_fast.py

# Test 2: Email real con datos sintéticos
python tests/test_send_real_email.py

# Test 3: Detección de anomalías + Railway MySQL
python tests/test_anomalies_railway.py

# Test 4: Predictor con Railway MySQL
python tests/test_predictor_railway.py

# Test 5: Sistema de reportes HTML/PDF
python tests/test_reporting_railway.py

# Test 6: Auto-training system
python tests/test_auto_trainer.py

# Test 7: Scheduler jobs (5 jobs)
python tests/test_scheduler_jobs.py

# Test 8: Templates de email
python tests/test_email_templates.py

# Output esperado:
# ✅ Todos los tests PASS
# ✅ Modelos cargados correctamente
# ✅ Emails enviados (si configurado)
# ✅ Railway MySQL conectado (si configurado)
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

| Rol | Responsabilidades | Stack | Estado |
|-----|-------------------|-------|---------|
| **Developer Python/AI** | - Análisis de datos<br>- Machine Learning<br>- Backend API<br>- Pipeline de predicción<br>- Scheduler 24/7 | Python, Prophet, scikit-learn, pandas, APScheduler | ✅ 100% Completo |
| **Electronics Partner** | - Hardware ESP32<br>- Sensores ACS712<br>- Código Arduino/C++<br>- Protocolo MQTT<br>- Integración Railway | C/C++, MQTT, ESP32, Sensores | ✅ 100% Completo |

**Estado Colaboración**: 
- ✅ Python backend completado
- ✅ Hardware ESP32 completado
- ✅ Integración ESP32 ↔ Railway MySQL completada
- ✅ Sistema end-to-end operacional 24/7

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

### **Documentación Externa**

- [Prophet Documentation](https://facebook.github.io/prophet/) - Guía oficial de Meta
- [Statsmodels ARIMA](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html) - Documentación de modelos estadísticos
- [Scikit-learn Time Series](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.preprocessing) - Preprocessing para ML
- [Pandas Time Series](https://pandas.pydata.org/docs/user_guide/timeseries.html) - Manejo de series temporales

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


<div align="center">

**🌟 ¿Te gusta DomusAI?**  
**¡Dale una estrella ⭐ al repositorio!**

**[⬆ Volver arriba](#-domusai---sistema-de-monitoreo-y-predicción-de-consumo-energético)**

---

**🆕 Nuevo en v0.95 - Sistema de Producción Completo**:
- ✅ **Scheduler 24/7** con 5 jobs automáticos (APScheduler)
- ✅ **Auto-training system** cada 7 días con backup de modelos
- ✅ **Modelos pre-entrenados**: Prophet (204 MB) + IsolationForest (1.48 MB)
- ✅ **Railway MySQL integration** con fallback automático a CSV
- ✅ **Test scripts optimizados**: test_prediction_fast.py (0.04s)
- ✅ **Generador de datos sintéticos** ultra-realista (4 años, 2.1M registros)
- ✅ **Email automation** con 5 templates profesionales
- ✅ **Configuración centralizada**: config.py con PathConfig, MLConfig, DatabaseConfig
- ✅ **Documentation completa**: README.md + ARCHITECTURE.md (950 líneas)
- ✅ **Windows Task Scheduler** XML para arranque automático
- ✅ **Suite de tests completa**: 8 archivos, ~1200 líneas de validación
- ✅ **Type-safety 100%**: 0 errores Pylance en todo el código
- ✅ **Hardware IoT ESP32**: Completado por Electronics Partner

**🎯 DomusAI v1.0 - Producción Operacional**: Sistema completo de automatización energética funcionando 24/7 end-to-end. Hardware ESP32 integrado con Python AI. Pipeline: Sensores → Railway MySQL → Prophet → Alertas → Email.

**📖 Ver Documentación Completa**: [ARCHITECTURE.md](ARCHITECTURE.md) - Sistema de producción detallado (950 líneas)

</div>