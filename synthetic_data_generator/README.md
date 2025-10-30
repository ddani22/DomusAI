# 📊 Generador de Datos Sintéticos de Consumo Energético

## 🎯 Propósito

Este módulo genera datos sintéticos de consumo energético **altamente realistas** que imitan patrones de consumo doméstico real. Útil para:

- ✅ Desarrollo y testing del sistema DomusAI sin esperar datos del ESP32
- ✅ Entrenamiento de modelos preliminares
- ✅ Demos y presentaciones
- ✅ Pruebas de carga del sistema
- ✅ Validación del pipeline completo

## 📁 Estructura

```
synthetic_data_generator/
├── README.md                           # Este archivo
├── generate_consumption_data.py        # Script principal
├── config.yaml                         # Configuración de patrones
├── output/                             # CSVs generados
│   ├── synthetic_30days_YYYYMMDD.csv
│   └── synthetic_90days_YYYYMMDD.csv
└── examples/                           # Ejemplos de uso
    └── insert_to_railway.py            # Script para insertar en Railway
```

## 🚀 Uso Rápido

### **Generar 30 días de datos**:
```bash
python generate_consumption_data.py --days 30
```

### **Generar 90 días con fecha específica**:
```bash
python generate_consumption_data.py --days 90 --start-date 2025-10-01
```

### **Generar y subir directamente a Railway**:
```bash
python generate_consumption_data.py --days 30 --upload-railway
```

### **Perfil de consumo específico**:
```bash
# Hogar pequeño (1-2 personas)
python generate_consumption_data.py --days 30 --profile small

# Hogar mediano (3-4 personas) [DEFAULT]
python generate_consumption_data.py --days 30 --profile medium

# Hogar grande (5+ personas)
python generate_consumption_data.py --days 30 --profile large
```

## ⚙️ Parámetros Disponibles

| Parámetro | Descripción | Default | Ejemplo |
|-----------|-------------|---------|---------|
| `--days` | Días de datos a generar | 30 | `--days 90` |
| `--start-date` | Fecha de inicio (YYYY-MM-DD) | Hoy - N días | `--start-date 2025-10-01` |
| `--profile` | Perfil de consumo | `medium` | `--profile large` |
| `--frequency` | Frecuencia de muestreo | `1min` | `--frequency 30s` |
| `--anomalies` | Inyectar anomalías (%) | 1.5 | `--anomalies 2.0` |
| `--output` | Directorio de salida | `output/` | `--output ../data/` |
| `--upload-railway` | Subir a Railway MySQL | False | `--upload-railway` |
| `--validate` | Solo validar datos generados | False | `--validate` |

## 📊 Patrones Implementados

### **1. Estacionalidad Diaria (24h)**

```
🌙 Noche (00:00-06:00)
   Consumo: 0.3-0.8 kW
   Patrón: Electrodomésticos en standby, refrigerador

🌅 Mañana (06:00-09:00)
   Consumo: 1.5-3.5 kW (PICO MATUTINO)
   Patrón: Ducha, desayuno, electrodomésticos

☀️ Día (09:00-18:00)
   Consumo: 0.8-1.5 kW
   Patrón: Refrigerador, carga de dispositivos

🌆 Tarde (18:00-23:00)
   Consumo: 2.0-4.5 kW (PICO NOCTURNO)
   Patrón: Cocina, TV, iluminación, lavadora
```

### **2. Estacionalidad Semanal**

```
📅 Lunes-Viernes
   Mayor consumo en horarios 7-9 AM y 18-21 PM
   
📅 Fin de Semana
   Consumo más distribuido durante el día
   Picos menos pronunciados
```

### **3. Variaciones Aleatorias**

- Ruido gaussiano (±10-20% sobre patrón base)
- Spikes ocasionales (electrodomésticos potentes)
- Micro-variaciones realistas (±5% cada minuto)

### **4. Anomalías Controladas** (Opcional)

- 🔴 **HIGH**: Consumo excesivo (>5 kW por 10+ minutos)
- 🟡 **MEDIUM**: Picos inusuales (4-5 kW fuera de horas pico)
- 🟢 **LOW**: Variaciones menores del patrón normal

## 🔬 Variables Generadas

| Columna | Descripción | Rango | Método |
|---------|-------------|-------|--------|
| `Datetime` | Timestamp cada 1 min | Configurable | Secuencial |
| `Global_active_power` | Potencia activa (kW) | 0.2-6.0 | Patrones + ruido |
| `Global_reactive_power` | Potencia reactiva (kVAr) | 10-20% de activa | Calculada |
| `Voltage` | Voltaje (V) | 220-245 | Normal(235, 5) |
| `Global_intensity` | Intensidad (A) | Calculada | P/V × 1000 |
| `Sub_metering_1` | Cocina (kW) | 0-40% total | Proporcional |
| `Sub_metering_2` | Lavandería (kW) | 0-30% total | Proporcional |
| `Sub_metering_3` | Agua/Clima (kW) | 0-30% total | Proporcional |

## ✅ Validaciones Implementadas

El script valida automáticamente:

1. ✅ **Rango de voltaje**: 220V ≤ Voltage ≤ 245V
2. ✅ **Potencia positiva**: Global_active_power ≥ 0
3. ✅ **Ley de Ohm**: Global_intensity = Global_active_power / Voltage × 1000
4. ✅ **Sub-metering coherente**: Sub_1 + Sub_2 + Sub_3 ≤ Global_active_power
5. ✅ **No timestamps duplicados**: Secuencia temporal válida
6. ✅ **No valores NaN**: Todas las columnas completas

## 📈 Perfiles de Consumo

### **Small (Hogar Pequeño)**
- 1-2 personas
- Consumo promedio: ~1.2 kW
- Picos: 2.0-3.0 kW
- Uso: Apartamentos, estudios

### **Medium (Hogar Mediano)** [DEFAULT]
- 3-4 personas
- Consumo promedio: ~1.8 kW
- Picos: 3.0-4.5 kW
- Uso: Casas familiares estándar

### **Large (Hogar Grande)**
- 5+ personas
- Consumo promedio: ~2.5 kW
- Picos: 4.5-6.0 kW
- Uso: Familias grandes, casas con múltiples sistemas

## 🔄 Integración con Railway

### **Opción 1: Generar CSV y usar pipeline existente**
```bash
# Generar CSV
python generate_consumption_data.py --days 30

# Usar el sistema de DomusAI para insertar
# (asumiendo que tienes un script de insert)
```

### **Opción 2: Subida directa**
```bash
# Incluye credenciales en .env del proyecto principal
python generate_consumption_data.py --days 30 --upload-railway
```

### **Opción 3: Script personalizado**
```python
from generate_consumption_data import SyntheticDataGenerator
from examples.insert_to_railway import insert_to_railway

# Generar datos
generator = SyntheticDataGenerator(days=30, profile='medium')
df = generator.generate()

# Subir a Railway
insert_to_railway(df, batch_size=1000)
```

## 📊 Ejemplo de Salida

### **Estadísticas del Dataset Generado**:
```
✅ GENERACIÓN COMPLETADA EXITOSAMENTE
════════════════════════════════════════════════════════════════════
📊 Estadísticas del Dataset:
   Total registros:       43,200
   Rango de fechas:       2025-09-29 00:00:00 → 2025-10-29 23:59:00
   Días generados:        30.0
   Frecuencia:            1 minuto
   
📈 Consumo Energético:
   Consumo promedio:      1.847 kW
   Consumo mínimo:        0.234 kW
   Consumo máximo:        5.123 kW
   Desviación estándar:   0.892 kW
   
⚡ Voltaje:
   Promedio:              235.2 V
   Rango:                 [220.1, 244.9] V
   
🔍 Anomalías Inyectadas:
   Total:                 648 registros (1.5%)
   HIGH:                  216 (33.3%)
   MEDIUM:                216 (33.3%)
   LOW:                   216 (33.3%)
   
✅ Validaciones:
   ✅ Sin valores NaN
   ✅ Sin timestamps duplicados
   ✅ Voltaje en rango válido
   ✅ Potencia no negativa
   ✅ Sub-metering coherente
   ✅ Ley de Ohm verificada (error < 0.1%)
   
💾 Archivo guardado:
   output/synthetic_30days_20251029.csv
════════════════════════════════════════════════════════════════════
```

## 🛠️ Requisitos

```bash
pip install pandas numpy scipy pyyaml
```

O si usas el entorno del proyecto principal:
```bash
# Ya están instaladas en .venv
```

## 🎓 Casos de Uso

### **Caso 1: Desarrollo Local**
```bash
# Generar datos para probar el sistema sin Railway
python generate_consumption_data.py --days 7 --output ../data/
```

### **Caso 2: Entrenamiento de Modelos**
```bash
# Generar 90 días para entrenar Prophet
python generate_consumption_data.py --days 90 --upload-railway
# Luego ejecutar AutoTrainer
```

### **Caso 3: Testing de Anomalías**
```bash
# Generar con muchas anomalías para probar detección
python generate_consumption_data.py --days 30 --anomalies 5.0
```

### **Caso 4: Demo para Cliente**
```bash
# Generar datos "limpios" sin anomalías
python generate_consumption_data.py --days 30 --anomalies 0.0 --profile large
```

## ⚠️ Notas Importantes

1. **No reemplaza datos reales**: Los datos sintéticos son para desarrollo. Para producción, usar datos del ESP32.

2. **Modelos aprenden patrones**: Si entrenas con datos sintéticos, los modelos aprenderán esos patrones específicos.

3. **Re-entrenamiento necesario**: Cuando tengas datos reales, re-entrena los modelos.

4. **Validación visual**: Siempre revisa las gráficas generadas para verificar que los patrones se ven realistas.

## 📝 Changelog

- **v1.0.0** (2025-10-29): Versión inicial con patrones diarios/semanales, 3 perfiles, validaciones completas

## 🤝 Contribuir

Para mejorar el generador:
1. Ajustar patrones en `config.yaml`
2. Añadir nuevos perfiles de consumo
3. Implementar patrones estacionales (verano/invierno)
4. Añadir más tipos de anomalías

## 📧 Soporte

Para dudas o problemas:
- Ver documentación del proyecto principal
- Revisar ejemplos en `examples/`
- Ejecutar con `--validate` para verificar datos generados
