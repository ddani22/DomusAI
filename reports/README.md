# 📋 Sistema de Reportes - DomusAI

Este directorio contiene todo lo necesario para la generación automática de reportes de consumo energético.

## 📁 Estructura de Directorios

```
reports/
│
├── templates/                    # Templates Jinja2 para HTML
│   ├── monthly_report.html          # Template principal del reporte mensual
│   ├── sections/                    # Secciones modulares del reporte
│   │   ├── executive_summary.html   # Resumen ejecutivo con KPIs
│   │   ├── historical_analysis.html # Análisis de datos históricos
│   │   ├── predictions.html         # Sección de predicciones
│   │   ├── anomalies.html           # Anomalías detectadas
│   │   ├── submetering.html         # Análisis por áreas
│   │   └── recommendations.html     # Recomendaciones personalizadas
│   │
│   └── styles/                      # Estilos CSS
│       └── report_styles.css        # Estilos principales del reporte
│
├── assets/                       # Recursos estáticos
│   ├── logo_domusai.png             # Logo del proyecto
│   ├── icons/                       # Iconos SVG para el reporte
│   │   ├── warning.svg              # Icono de alerta
│   │   ├── check.svg                # Icono de éxito
│   │   ├── chart.svg                # Icono de gráfico
│   │   └── energy.svg               # Icono de energía
│   │
│   └── fonts/                       # Fuentes personalizadas
│       └── Roboto/                  # Fuente Roboto (opcional)
│
└── generated/                    # Reportes generados automáticamente
    ├── .gitignore                   # Ignora reportes generados en Git
    └── reporte_YYYY-MM_timestamp.*  # Reportes en PDF/HTML
```

## 🎯 Uso del Sistema de Reportes

### **Generación de Reporte Mensual**

```python
from src.reporting import ReportGenerator

# Inicializar generador
generator = ReportGenerator()

# Generar reporte completo
report = generator.generate_monthly_report(
    data=df_consumo,
    predictions=predicciones,
    anomalies=anomalias,
    month=10,
    year=2025
)

print(f"✅ Reporte PDF: {report['pdf_path']}")
print(f"✅ Reporte HTML: {report['html_path']}")
```

### **Generación Rápida**

```python
from src.reporting import generate_quick_report

# Una sola línea para generar reporte del último mes
report = generate_quick_report('data/Dataset_clean_test.csv')
```

## 📊 Secciones del Reporte

### 1️⃣ **Resumen Ejecutivo**
- Consumo total del período
- Comparación con mes anterior
- Score de eficiencia (0-100)
- Total de anomalías detectadas

### 2️⃣ **Análisis Histórico**
- Gráfico de consumo diario (línea temporal)
- Heatmap de consumo por hora y día
- Patrones semanales
- Top 5 días con mayor consumo

### 3️⃣ **Predicciones**
- Forecast próximos 7 días con intervalos de confianza
- Consumo estimado próximo mes
- Estimación de factura
- Alertas de días con consumo alto previsto

### 4️⃣ **Detección de Anomalías**
- Total de anomalías por tipo
- Gráfico de distribución (pie chart)
- Top 10 anomalías críticas (tabla)
- Timeline de anomalías

### 5️⃣ **Análisis por Áreas**
- Consumo por sub-metering (cocina, lavandería, A/C)
- Porcentaje de contribución de cada área
- Gráfico de barras comparativo

### 6️⃣ **Recomendaciones**
- Acciones sugeridas para optimización
- Potencial de ahorro estimado
- Consejos personalizados basados en patrones detectados

### 7️⃣ **Datos Técnicos**
- Métricas del modelo (MAE, RMSE, R²)
- Confiabilidad de predicciones
- Información del sistema

## 🎨 Personalización

### **Templates HTML**

Los templates usan Jinja2 para renderizado dinámico:

```html
<div class="kpi-card">
    <h3>Consumo Total</h3>
    <p class="kpi-value">{{ summary.total_consumption }} kWh</p>
    <p class="kpi-change {{ 'increase' if summary.change_pct > 0 else 'decrease' }}">
        {{ summary.change_pct }}% vs mes anterior
    </p>
</div>
```

### **Estilos CSS**

Modificar `templates/styles/report_styles.css` para cambiar:
- Colores del tema
- Tipografía
- Espaciado y layout
- Tamaño de gráficos

### **Logo Personalizado**

Reemplazar `assets/logo_domusai.png` con tu propio logo (recomendado: 200x200px, PNG transparente).

## 📦 Dependencias

El sistema de reportes requiere:

```bash
pip install jinja2==3.1.4        # Templates HTML
pip install weasyprint==62.3     # Conversión HTML → PDF
pip install pillow==10.4.0       # Manejo de imágenes
pip install matplotlib==3.10.6   # Generación de gráficos
pip install seaborn==0.13.2      # Visualizaciones avanzadas
```

## 🔧 Configuración

### **Variables de Entorno** (opcional)

```bash
# .env
REPORT_OUTPUT_DIR=reports/generated
REPORT_LOGO_PATH=reports/assets/logo_domusai.png
REPORT_TARIFA_KWH=0.15  # Tarifa eléctrica por kWh (para estimación de factura)
```

## 📝 Ejemplos de Reportes

Ver directorio `reports/generated/` para ejemplos de reportes generados (ignorados en Git).

## 🚀 Próximas Mejoras

- [ ] Soporte para reportes semanales
- [ ] Comparación anual (año sobre año)
- [ ] Exportación a Excel
- [ ] Dashboard interactivo embebido
- [ ] Envío automático por email
- [ ] Multi-idioma (ES/EN)

---

**Autor**: DomusAI Team  
**Versión**: 1.0  
**Última actualización**: Octubre 2025
