# 📊 Análisis del Dataset Sintético - 4 Años (España)

## Características Generadas

### 🗓️ Información General
- **Período**: 2025-10-30 → 2029-10-28 (4 años)
- **Registros totales**: 2,102,400 (1 minuto de frecuencia)
- **Tamaño del archivo**: 130.5 MB
- **Perfil**: Hogar mediano español

### 📈 Estadísticas de Consumo
- **Promedio**: 1.951 kW
- **Mínimo**: 0.100 kW (consumo base nocturno)
- **Máximo**: 31.905 kW (anomalías o picos excepcionales)
- **Desviación estándar**: 2.092 kW

### ⚡ Voltaje (Estándar Español)
- **Promedio**: 230.0 V
- **Rango**: 225-238 V (fluctuación realista ±3%)

### 🏖️ Períodos de Vacaciones Generados (13 períodos)

#### Agosto (Vacaciones de Verano - 100% fuera)
- 2025: 30 Oct - 17 Nov (ajustado por fecha inicio)
- 2026: 1-19 Agosto (18 días)
- 2027: 1-18 Agosto (17 días)
- 2028: 1-21 Agosto (20 días)
- 2029: 1-19 Agosto (18 días)

#### Navidad (50% fuera / 50% en casa con familia)
- 2025: 23 Dic - 7 Ene
- 2026: 23 Dic - 7 Ene
- 2027: 23 Dic - 7 Ene
- 2028: 23 Dic - 7 Ene

#### Semana Santa (50% fuera / 50% en casa)
- 2026: 8-15 Abril
- 2027: 8-15 Abril
- 2028: 8-15 Abril
- 2029: 8-15 Abril

### 🌉 Puentes Festivos (4 identificados)
- 2026-12-04 → 2026-12-11 (Constitución/Inmaculada)
- 2027-10-08 → 2027-10-15 (Hispanidad)
- 2028-10-10 → 2028-10-15 (Hispanidad)
- 2029-04-27 → 2029-05-04 (1 Mayo)

### 📅 Variación Mensual Aleatoria
| Mes | Factor | Observación |
|-----|--------|-------------|
| Enero | 0.92x | Consumo reducido |
| Febrero | 1.09x | Consumo aumentado |
| Marzo | 1.02x | Normal |
| Abril | 1.01x | Normal |
| Mayo | 1.05x | Ligeramente alto |
| Junio | 1.01x | Normal |
| **Julio** | **0.83x** | **Reducción notable** (vacaciones) |
| Agosto | 0.93x | Bajo (vacaciones) |
| Septiembre | 1.09x | Consumo aumentado |
| Octubre | 1.08x | Consumo aumentado |
| Noviembre | 0.98x | Normal |
| **Diciembre** | **1.11x** | **Aumento notable** (fiestas, calefacción) |

## 🔌 Patrones Implementados

### Ciclo Diario (Días Laborables)
- **00:00-06:00**: Consumo base mínimo (0.2x - nevera, standby)
- **06:00-09:00**: Pico matutino (0.9x - duchas, desayuno, luces)
- **09:00-17:00**: Consumo bajo (0.3x - casa vacía o teletrabajo)
- **17:00-23:00**: **Pico máximo del día (1.2x - cocina, TV, lavadora)**

### Ciclo Semanal (Fines de Semana)
- **25%**: Fin de semana FUERA (consumo 0.15x)
- **35%**: Fin de semana EN CASA (consumo alto con picos en comida 14h y cena 21h)
- **40%**: Fin de semana NORMAL (patrón desplazado, despertar 10h)

### Estacionalidad (España)
- **Invierno (Dic-Feb)**: +10% consumo base, +30% calefacción (Sub_metering_3)
- **Verano (Jun-Ago)**: -5% consumo base, +20% aire acondicionado (picos 14-18h)
- **Primavera/Otoño**: Consumo moderado, HVAC mínimo

## 🏠 Sub-Medidores (Patrones Españoles)

### Sub_metering_1: Cocina
- **Picos claros**: 8h (desayuno), 14h (comida), 21h (cena)
- **Base continua**: Nevera siempre encendida (0.05 kW)
- **Variación**: ±20% por preparación de alimentos

### Sub_metering_2: Lavandería
- **Patrón esporádico**: 8% probabilidad días laborables
- **Pico fin de semana**: 30% probabilidad sábados 10-13h
- **Consumo típico**: 20% del total cuando activa

### Sub_metering_3: Clima/Agua
- **Componente estacional**: Fuerte dependencia invierno/verano
- **Duchas matutinas**: Pico 7-9h
- **HVAC verano**: Máximo 14-18h (pico de calor)
- **HVAC invierno**: Activo 6-23h (calefacción continua)

## 🚨 Anomalías Inyectadas
- **Total**: 31,536 registros (1.5% del dataset)
- **HIGH**: 10,305 (consumos >5 kW excepcionales)
- **MEDIUM**: 10,473 (picos 2-3x normales)
- **LOW**: 10,758 (variaciones 1.5-2x normales)

## 🔬 Relaciones Físicas

### Voltaje
- Fluctuación gaussiana alrededor de 230V
- Rango: 225-238V (±3.5%)

### Potencia Reactiva
- Factor de potencia simulado: 0.85-0.95
- Q = P × tan(arccos(FP)) + ruido ±10%

### Intensidad
- Ley de Ohm: I = (P × 1000) / (V × 0.9)
- Factor 0.9 asume FP promedio
- Ruido gaussiano ±0.05A

## ✅ Validaciones
- ✅ **No NaN**: Sin valores faltantes
- ✅ **No Duplicates**: Timestamps únicos
- ✅ **Voltage Range**: 225-238V cumplido
- ✅ **Power Positive**: Sin valores negativos
- ✅ **Submetering Coherent**: Sum ≤ 75% del total (resto consumo no medido)
- ⚠️ **Ohms Law**: Error menor esperado por ruido realista

## 📂 Archivo Generado
```
Ubicación: synthetic_data_generator/output/synthetic_1460days_20251101_185203.csv
Tamaño: 130.5 MB
Formato: CSV con 8 columnas
Encoding: UTF-8
```

## 🎯 Uso Recomendado
Este dataset es ideal para:
- Entrenar modelos Prophet (4 años de datos históricos)
- Detección de anomalías (31K ejemplos etiquetados)
- Análisis de estacionalidad española
- Predicción de consumo considerando vacaciones y festivos
- Simulación de sistema completo DomusAI

---
*Generado el 2025-11-01 por DomusAI v2.0.0*
