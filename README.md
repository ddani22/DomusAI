# ⚡ Sistema de Monitoreo y Predicción de Consumo Energético Comunitario

## 🎯 Objetivo
Este proyecto busca crear una herramienta que permita:
- Monitorear el consumo eléctrico en una vivienda o comunidad.
- Procesar los datos con Python para analizar patrones y predecir consumos futuros.
- Detectar anomalías en el consumo energético.
- Generar reportes automáticos (PDF/HTML) con gráficos, predicciones y alertas.
- Enviar dichos reportes por correo electrónico a los vecinos.

---

## 🔧 Tecnologías y librerías principales
- **Python (backend de procesamiento de datos)**
- **Pandas / Numpy** → Limpieza y manipulación de datos.
- **Matplotlib / Seaborn / Plotly** → Visualización de datos.
- **Statsmodels / Prophet / Scikit-learn / TensorFlow (LSTM)** → Modelos de predicción de consumo.
- **Scikit-learn / Isolation Forest / Autoencoders** → Detección de anomalías.
- **SQLite o InfluxDB** → Almacenamiento de datos.
- **smtplib / yagmail** → Envío de correos con reportes.
- **Reportlab / WeasyPrint** → Generación de reportes PDF/HTML.
- **Flask / Dash (opcional)** → Dashboard web para visualización en tiempo real.

---

## 📂 Estructura del proyecto
proyecto-energia/
│── data/ # Datasets originales y limpios
│ ├── Dataset_original_test.csv
│ ├── Dataset_clean_test.csv
│
│── notebooks/ # Jupyter Notebooks de pruebas y EDA
│ ├── 01_eda.ipynb
│ ├── 02_prediccion.ipynb
│ ├── 03_anomalias.ipynb
│
│── src/ # Código principal en Python
│ ├── data_cleaning.py # Limpieza y preparación de datos
│ ├── eda.py # Funciones de análisis exploratorio
│ ├── prediction.py # Modelos de predicción
│ ├── anomalies.py # Detección de anomalías
│ ├── reporting.py # Generación de reportes
│ ├── email_sender.py # Envío de correos automáticos
│
│── reports/ # Reportes generados (PDF/HTML)
│ ├── reporte_2025-01.pdf
│
│── README.md # Descripción del proyecto
│── requirements.txt # Dependencias de Python

markdown
Copiar código

---

## 🚀 Flujo de trabajo
1. **Limpieza de datos** → preparar dataset (`data_cleaning.py`).
2. **EDA (análisis exploratorio)** → gráficas y patrones básicos (`eda.py`).
3. **Modelado predictivo** → entrenar modelos de series temporales (`prediction.py`).
4. **Detección de anomalías** → identificar consumos anormales (`anomalies.py`).
5. **Generación de reportes** → PDF/HTML con gráficas y predicciones (`reporting.py`).
6. **Envío automático de reportes** → correo electrónico (`email_sender.py`).
7. (Opcional) **Dashboard web** → monitoreo en tiempo real.

---

## 🛠️ Estado actual
- [x] Dataset de prueba cargado.
- [ ] Limpieza de datos.
- [ ] Exploración inicial y visualizaciones.
- [ ] Primer modelo de predicción.
- [ ] Detección de anomalías básica.
- [ ] Reportes automáticos en PDF.
- [ ] Envío de correos.
- [ ] Dashboard web.

---

## 🤝 Colaboradores
- **Tú (programación Python + IA)** → procesamiento, predicción y software.
- **Compañero (electrónica)** → sensores, ESP32/Arduino, comunicación MQTT.

---

## 📌 Notas para GitHub Copilot
- Los scripts deben seguir este flujo de trabajo.
- La prioridad actual es **limpiar los datos y realizar un análisis exploratorio inicial**.
- Después se deben implementar modelos de predicción y detección de anomalías.
- El código debe ser modular, cada archivo en `src/` debe encargarse de una parte específica.