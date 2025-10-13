# 🔗 DomusAI - Sprint 8: Integración IoT Hardware

## 📋 Plan Detallado de Integración IoT

**Objetivo**: Transformar DomusAI de un sistema de análisis de datos históricos a un **sistema de monitoreo en tiempo real** completamente autónomo con sensores ESP32.

**Fecha Inicio**: Octubre 13, 2025  
**Duración Estimada**: 2-3 semanas (11-17 días)  
**Prioridad**: 🔥 CRÍTICA - Completa DomusAI v1.0  
**Budget**: $29-45 USD

---

## 🎯 Visión del Sprint 8

### **Estado Actual (Sprint 7 Completado)**
```
Datos CSV históricos → Análisis Python → Reportes PDF → Email automático
     ↑                     ↑              ↑            ↑
  Manual          Automático      Automático    Automático
```

### **Estado Final (Sprint 8 - DomusAI v1.0)**
```
ESP32 Sensor → MQTT → Base Datos → Análisis Automático → Email Automático
     ↑          ↑         ↑              ↑                    ↑
  Tiempo Real  Tiempo Real  Tiempo Real  Cada 1h           Crítico/Diario
```

---

## 📦 FASE 1: Adquisición y Preparación de Hardware (2-3 días)

### **Checklist 1.1: Compra de Componentes** ⏱️ 2-4 horas

#### **Componentes Principales**
- [ ] **ESP32 DevKit C/V4** (38 pines) - $12-15 USD
  - Marca recomendada: DOIT DevKit, HiLetgo, TTGO
  - WiFi integrado, Bluetooth
  - GPIO suficientes para expansión
  - Link sugerido: Amazon/AliExpress "ESP32 DevKit"

- [ ] **Sensor ACS712-30A** Hall Effect - $5-8 USD
  - Rango: 0-30A (suficiente para hogar)
  - Salida analógica compatible ESP32
  - Tolerancia: ±1.5% precisión
  - Link sugerido: "ACS712 30A module"

#### **Componentes Adicionales**
- [ ] **Breadboard** 830 puntos - $3 USD
- [ ] **Cables Dupont** M-M (40 unidades) - $2 USD  
- [ ] **Cables Dupont** M-F (40 unidades) - $2 USD
- [ ] **Resistencias** 10kΩ (pack 20) - $1 USD
- [ ] **Capacitor** 100µF 25V - $1 USD
- [ ] **LED indicador** + resistencia 220Ω - $1 USD

#### **Opcional para Futuro**
- [ ] PCB prototipo 7x5cm - $2 USD
- [ ] Caja plástica proyecto 10x6x3cm - $3 USD
- [ ] Fuente 5V 2A MicroUSB - $4 USD

**💰 Total Estimado: $25-35 USD**  
**🛍️ Dónde Comprar**: Amazon, AliExpress, MercadoLibre, tienda local electrónica  
**⏰ Tiempo Entrega**: 1-3 días (local), 1-2 semanas (online)

---

### **Checklist 1.2: Instalación Arduino IDE + ESP32** ⏱️ 1 hora

- [ ] **Paso 1**: Descargar Arduino IDE
  - Ir a: https://www.arduino.cc/en/software
  - Descargar Arduino IDE 2.x (más moderno)
  - Instalar en el sistema

- [ ] **Paso 2**: Configurar ESP32 en Arduino IDE
  - File → Preferences → Additional Board Manager URLs
  - Añadir: `https://dl.espressif.com/dl/package_esp32_index.json`
  - Tools → Board → Boards Manager
  - Buscar "ESP32" → Instalar "ESP32 by Espressif Systems"

- [ ] **Paso 3**: Instalar Librerías Necesarias
  - Sketch → Include Library → Manage Libraries
  - Buscar e instalar:
    - [ ] "PubSubClient" by Nick O'Leary (MQTT)
    - [ ] "ArduinoJson" by Benoit Blanchon (JSON parsing)
    - [ ] "WiFi" (ya incluida con ESP32)
    - [ ] "EmonLib" (opcional para cálculos energía)

- [ ] **Paso 4**: Test Inicial
  - Tools → Board → ESP32 Dev Module
  - Tools → Port → Seleccionar puerto COM
  - File → Examples → WiFi → WiFiScan
  - Upload y verificar que detecta redes WiFi
  - ✅ **Criterio de éxito**: ESP32 escanea y muestra redes WiFi disponibles

---

### **Checklist 1.3: Crear Circuito Básico** ⏱️ 2 horas

#### **Esquema de Conexiones**
```
ESP32 DevKit        ACS712 Sensor        Componentes Extra
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VIN (5V)     ────→  VCC               
GND          ────→  GND               
GPIO34 (ADC) ────→  OUT (Analog)      
             
GPIO2        ────→                    LED indicador (+)
GND          ────→                    LED indicador (-) + resistencia 220Ω

ALIMENTACIÓN DE LÍNEA:
L (Fase)     ────→  ACS712 Terminal IN
N (Neutro)   ────→  Directo (NO pasa por sensor)
ACS712 OUT   ────→  Hacia carga (electrodomésticos)
```

#### **Tareas de Montaje**
- [ ] Conectar ESP32 a breadboard
- [ ] Conectar sensor ACS712 a breadboard
- [ ] Realizar conexiones según esquema
- [ ] Conectar LED indicador en GPIO2
- [ ] Añadir capacitor de desacople (opcional)
- [ ] Verificar todas las conexiones visualmente
- [ ] Documentar conexiones con foto
- [ ] Crear archivo `hardware/schemas/circuit_diagram.txt`

#### **⚠️ IMPORTANTE SEGURIDAD**
- [ ] NUNCA tocar cables de línea con equipo encendido
- [ ] Usar multímetro para verificar voltajes
- [ ] Instalar con disyuntor apagado
- [ ] Pedir ayuda a electricista si no tienes experiencia
- [ ] Usar guantes aislantes si es necesario
- [ ] Mantener área de trabajo seca

---

### **Checklist 1.4: Test Hardware Básico** ⏱️ 1-2 horas

#### **Tests de Validación**
- [ ] **Test 1: LED Blink**
  - File → Examples → 01.Basics → Blink
  - Cambiar LED_BUILTIN a 2 (GPIO2)
  - Upload y verificar parpadeo
  - ✅ LED debe parpadear cada segundo

- [ ] **Test 2: WiFi Scan**
  - File → Examples → WiFi → WiFiScan
  - Upload y abrir Serial Monitor (115200 baud)
  - ✅ Debe mostrar lista de redes WiFi

- [ ] **Test 3: Lectura ADC Básica**
  - Crear sketch simple leyendo GPIO34
  - Mostrar valores por Serial Monitor
  - Sin carga: valor ~2048 (mitad del rango 0-4095)
  - ✅ Valores deben estar entre 0-4095

- [ ] **Test 4: Sensor ACS712 Sin Carga**
  - Conectar sensor según esquema
  - Leer GPIO34 con carga apagada
  - ✅ Corriente debe ser ≈ 0.0A

- [ ] **Test 5: Sensor ACS712 Con Carga**
  - Encender una lámpara o dispositivo conocido
  - Leer GPIO34 con carga encendida
  - ✅ Corriente debe ser > 0A (coherente con dispositivo)

#### **Documentación**
- [ ] Anotar todos los resultados de tests
- [ ] Tomar fotos del circuito funcionando
- [ ] Guardar logs de Serial Monitor
- [ ] Documentar problemas encontrados
- [ ] Crear archivo `hardware/docs/setup_log.md`

---

## 📡 FASE 2: Configuración MQTT Broker (1 día)

### **Checklist 2.1: Instalación Mosquitto MQTT Broker** ⏱️ 1-2 horas

#### **Para Windows 10/11**
- [ ] Descargar Mosquitto
  - Ir a: https://mosquitto.org/download/
  - Descargar "mosquitto-2.0.18-install-windows-x64.exe"
  - Ejecutar como administrador

- [ ] Crear archivo de configuración
  - Abrir PowerShell como Administrador
  - `cd "C:\Program Files\mosquitto"`
  - Crear `mosquitto.conf` con configuración básica

- [ ] Configurar servicio Windows
  - Ejecutar: `mosquitto install`
  - Iniciar servicio: `net start mosquitto`
  - Verificar: `sc query mosquitto`

- [ ] Test básico
  - Terminal 1: `mosquitto_sub -h localhost -t test`
  - Terminal 2: `mosquitto_pub -h localhost -t test -m "Hello DomusAI"`
  - ✅ Terminal 1 debe mostrar "Hello DomusAI"

#### **Para Linux (Ubuntu/Debian)**
- [ ] Instalar Mosquitto
  - `sudo apt update`
  - `sudo apt install mosquitto mosquitto-clients`

- [ ] Configurar broker
  - `sudo nano /etc/mosquitto/mosquitto.conf`
  - Añadir: `listener 1883` y `allow_anonymous true`

- [ ] Iniciar servicio
  - `sudo systemctl enable mosquitto`
  - `sudo systemctl start mosquitto`
  - `sudo systemctl status mosquitto`

- [ ] Test básico
  - Terminal 1: `mosquitto_sub -h localhost -t test`
  - Terminal 2: `mosquitto_pub -h localhost -t test -m "Hello DomusAI"`
  - ✅ Verificar recepción de mensaje

#### **Para macOS**
- [ ] Instalar con Homebrew
  - `brew install mosquitto`

- [ ] Configurar broker
  - Editar `/usr/local/etc/mosquitto/mosquitto.conf`
  - Añadir configuración básica

- [ ] Iniciar servicio
  - `brew services start mosquitto`

- [ ] Test básico
  - Realizar mismo test que Linux
  - ✅ Verificar funcionamiento

---

### **Checklist 2.2: Configuración MQTT Avanzada** ⏱️ 30 min - 1 hora

- [ ] **Configurar firewall**
  - Abrir puerto 1883 en firewall del sistema
  - Windows: Firewall → Reglas de entrada → Nueva regla
  - Linux: `sudo ufw allow 1883/tcp`
  - ✅ Verificar con `telnet localhost 1883`

- [ ] **Obtener IP local**
  - Windows: `ipconfig` → IPv4
  - Linux/Mac: `ifconfig` o `ip addr`
  - Anotar IP (ej: 192.168.1.100)
  - Verificar que es IP estática o configurar reserva en router

- [ ] **Configurar logging**
  - Crear directorio: `C:\mosquitto\logs` (Windows)
  - Crear directorio: `/var/log/mosquitto` (Linux)
  - Añadir en config: `log_dest file [ruta_logs]/mosquitto.log`
  - Verificar que se crean logs

- [ ] **Configurar tópicos DomusAI**
  - Topics base: `domusai/energy/data`
  - Topics status: `domusai/energy/status`
  - Topics commands: `domusai/energy/commands`
  - Documentar estructura en `services/mqtt_broker/topics.md`

---

### **Checklist 2.3: Herramientas de Testing MQTT** ⏱️ 30 min

- [ ] **Instalar MQTT Explorer** (recomendado)
  - Descargar de: http://mqtt-explorer.com/
  - Instalar aplicación
  - Configurar conexión a localhost:1883
  - Explorar tópicos y mensajes
  - ✅ Debe conectar y mostrar todos los tópicos

- [ ] **Instalar cliente Python paho-mqtt**
  - Activar entorno virtual: `.venv\Scripts\Activate.ps1`
  - `pip install paho-mqtt`
  - Verificar: `pip show paho-mqtt`

- [ ] **Script de test Python**
  - Crear `scripts/test_mqtt_connection.py`
  - Script básico pub/sub para validar
  - Ejecutar y verificar funcionamiento
  - ✅ Debe publicar y recibir mensajes

- [ ] **Documentar configuración**
  - Crear `services/mqtt_broker/README.md`
  - Incluir IP, puerto, credenciales
  - Comandos útiles para troubleshooting
  - Procedimiento de reinicio

---

## ⚡ FASE 3: Programación del ESP32 (2-3 días)

### **Checklist 3.1: Configuración Base WiFi + MQTT** ⏱️ 3-4 horas

- [ ] **Crear proyecto ESP32**
  - Crear directorio `hardware/esp32_sensor/`
  - Crear archivo `esp32_energy_monitor.ino`
  - Crear archivo `config.h` para credenciales
  - Estructura básica con setup() y loop()

- [ ] **Implementar conexión WiFi**
  - Función `connectWiFi()` con retry logic
  - Timeout de 20 segundos máximo
  - LED indicador de estado WiFi
  - Logging por Serial Monitor
  - ✅ Debe conectar a red WiFi configurada

- [ ] **Implementar cliente MQTT**
  - Función `connectMQTT()` con reconexión
  - Configurar callbacks: onConnect, onMessage, onDisconnect
  - Client ID único basado en MAC address
  - ✅ Debe conectar al broker configurado

- [ ] **Implementar sistema de tópicos**
  - Publicación en `domusai/energy/data`
  - Publicación en `domusai/energy/status`
  - Suscripción a `domusai/energy/commands`
  - ✅ Verificar con MQTT Explorer

- [ ] **Test de conectividad completo**
  - WiFi + MQTT funcionando simultáneamente
  - Reconexión automática si se pierde conexión
  - LED indicando estado (fijo=OK, parpadeando=error)
  - ✅ Sistema estable por 10+ minutos

---

### **Checklist 3.2: Integración Sensor ACS712** ⏱️ 3-4 horas

- [ ] **Calibración inicial del sensor**
  - Función `calibrateSensor()` al inicio
  - Promediar 1000 lecturas sin carga
  - Guardar valor de offset (punto cero)
  - Mostrar resultado en Serial Monitor
  - ✅ Offset debe estar cerca de 2048 (±100)

- [ ] **Implementar lectura de corriente**
  - Función `readCurrent()` con muestreo múltiple
  - Convertir valores ADC a voltaje
  - Convertir voltaje a corriente usando sensibilidad ACS712
  - Calcular corriente RMS
  - ✅ Con carga apagada: I ≈ 0.0A

- [ ] **Implementar cálculo de potencia**
  - Función `calculatePower(current)`
  - Fórmula: P = V × I
  - Voltaje fijo: 230V (o 110V según país)
  - Mostrar en watts y kilowatts
  - ✅ Valores coherentes con dispositivos conocidos

- [ ] **Implementar filtrado y suavizado**
  - Media móvil de últimas 10 lecturas
  - Detección de valores espurios
  - Límites físicos (0-30A, 0-7kW)
  - ✅ Lecturas estables sin saltos bruscos

- [ ] **Validación con multímetro**
  - Comparar lecturas ESP32 vs multímetro real
  - Error aceptable: ±5%
  - Ajustar calibración si es necesario
  - Documentar precisión obtenida
  - ✅ Precisión dentro del rango aceptable

---

### **Checklist 3.3: Lógica de Envío de Datos** ⏱️ 2-3 horas

- [ ] **Implementar sampling periódico**
  - Lectura cada 30 segundos (configurable)
  - Timer no bloqueante (millis())
  - Buffer local para 10 últimas lecturas
  - ✅ Timing consistente ±1 segundo

- [ ] **Crear estructura JSON de datos**
  - Campos: device_id, timestamp, voltage, current, power
  - Campos adicionales: energy_total, rssi, uptime
  - Estadísticas: max_power, min_power, reading_number
  - ✅ JSON válido verificado en MQTT Explorer

- [ ] **Implementar envío MQTT**
  - Función `sendDataToMQTT()`
  - Publicar en topic `domusai/energy/data`
  - QoS = 1 (at least once delivery)
  - Retain = false (datos en tiempo real)
  - ✅ Datos visibles en MQTT Explorer

- [ ] **Implementar buffer de pérdidas**
  - Array circular para últimas 50 lecturas
  - Si MQTT falla, guardar en buffer
  - Reenviar cuando reconecte
  - ✅ No se pierden datos en desconexiones cortas

- [ ] **Implementar heartbeat**
  - Enviar status cada 5 minutos
  - Topic: `domusai/energy/status`
  - Incluir: uptime, free_heap, wifi_rssi
  - ✅ Status visible en MQTT Explorer

---

### **Checklist 3.4: Funciones de Diagnóstico** ⏱️ 1-2 horas

- [ ] **Sistema de LED indicadores**
  - WiFi + MQTT OK: LED encendido fijo
  - WiFi OK, MQTT fallo: parpadeo lento (500ms)
  - WiFi fallo: parpadeo rápido (100ms)
  - Lectura enviada: parpadeo único
  - ✅ Estados claramente diferenciables

- [ ] **Modo debug por Serial**
  - Logging detallado de eventos
  - Formato timestamp + nivel + mensaje
  - Configurar nivel: INFO, DEBUG, ERROR
  - ✅ Fácil troubleshooting desde Serial Monitor

- [ ] **Comandos remotos MQTT**
  - Comando `calibrate`: recalibrar sensor
  - Comando `reset_stats`: reiniciar estadísticas
  - Comando `status`: enviar info del sistema
  - Comando `reboot`: reiniciar ESP32
  - ✅ Comandos responden correctamente

- [ ] **Estadísticas de funcionamiento**
  - Contador de lecturas enviadas
  - Contador de reconexiones WiFi/MQTT
  - Tiempo online total (uptime)
  - Máxima/mínima potencia registrada
  - ✅ Estadísticas accesibles vía comando

- [ ] **Watchdog timer**
  - Configurar watchdog de 60 segundos
  - Reset automático si sistema se cuelga
  - Log de resets por watchdog
  - ✅ Sistema se recupera de cuelgues

---

## 🐍 FASE 4: Sistema de Ingesta Python (2-3 días)

### **Checklist 4.1: Módulo MQTT Ingester** ⏱️ 4-5 horas

- [ ] **Crear archivo `src/mqtt_ingester.py`**
  - Estructura básica de clase
  - Docstrings completos
  - Type hints en funciones
  - Logging configurado

- [ ] **Implementar clase MQTTIngester**
  - Constructor con parámetros configurables
  - Atributos: broker_host, port, client, database
  - Estado: connected, running, total_messages
  - ✅ Clase instanciable sin errores

- [ ] **Configurar cliente MQTT Python**
  - Usar librería paho-mqtt
  - Callbacks: on_connect, on_message, on_disconnect
  - QoS = 0 para recepción
  - ✅ Se conecta al broker correctamente

- [ ] **Implementar suscripción a tópicos**
  - Suscribirse a `domusai/energy/data`
  - Suscribirse a `domusai/energy/status`
  - Suscribirse a `domusai/+/+/data` (wildcard)
  - ✅ Recibe mensajes de todos los tópicos

- [ ] **Implementar parser de JSON**
  - Función `_process_energy_data()`
  - Validar campos requeridos
  - Conversión de tipos (str→float)
  - Manejo de errores de parsing
  - ✅ Procesa JSON del ESP32 correctamente

- [ ] **Implementar sistema de logging**
  - Log a archivo: `logs/mqtt_ingester.log`
  - Log a consola simultáneamente
  - Formato: timestamp + nivel + mensaje
  - Rotación de logs (max 10MB)
  - ✅ Logs legibles y útiles

- [ ] **Implementar threading**
  - Loop MQTT en thread separado
  - Thread daemon para cierre limpio
  - Métodos: start(), stop(), get_status()
  - ✅ Sistema corre en background sin bloquear

---

### **Checklist 4.2: Base de Datos Tiempo Real** ⏱️ 3-4 horas

- [ ] **Crear archivo `src/realtime_database.py`**
  - Clase `EnergyDatabase`
  - Constructor con path configurable
  - Docstrings y type hints completos

- [ ] **Diseñar esquema SQLite**
  - Tabla `energy_readings`:
    - id (INTEGER PRIMARY KEY AUTOINCREMENT)
    - timestamp (DATETIME DEFAULT CURRENT_TIMESTAMP)
    - device_id (TEXT NOT NULL)
    - voltage (REAL)
    - current (REAL)
    - power (REAL NOT NULL)
    - energy_total (REAL)
    - raw_data (TEXT - JSON completo)
  - Tabla `device_status`:
    - Similar estructura para status
  - Índices en timestamp y device_id
  - ✅ Esquema optimizado para consultas temporales

- [ ] **Implementar funciones de inserción**
  - `insert_reading()` - inserción rápida
  - `insert_bulk()` - inserción por lotes
  - `insert_device_status()` - status de dispositivos
  - Transacciones para atomicidad
  - ✅ Inserciones < 10ms

- [ ] **Implementar funciones de consulta**
  - `get_recent_data(hours=24)` - últimas N horas
  - `get_data_range(start, end)` - rango temporal
  - `get_device_data(device_id)` - por dispositivo
  - `get_statistics(period)` - estadísticas agregadas
  - ✅ Consultas optimizadas con índices

- [ ] **Implementar sistema de archivado**
  - Archivar datos > 30 días a tabla separada
  - Función `archive_old_data()`
  - Ejecutar automáticamente cada semana
  - ✅ Database no crece indefinidamente

- [ ] **Implementar backup automático**
  - Backup diario de database
  - Guardar en `data/real_time/backup/`
  - Mantener últimos 7 backups
  - Función `backup_database()`
  - ✅ Backups ejecutándose correctamente

---

### **Checklist 4.3: Validación y Limpieza Tiempo Real** ⏱️ 2-3 horas

- [ ] **Implementar validación de rangos**
  - Función `_validate_readings()`
  - Rangos: 0-10kW, 0-50A, 200-250V
  - Coherencia: P ≈ V × I (±20%)
  - Rechazar valores fuera de rango
  - ✅ Solo datos válidos en database

- [ ] **Implementar detección de valores anómalos**
  - Función `_check_critical_anomalies()`
  - Umbrales: power > 5kW, current > 30A
  - Voltaje: <200V o >250V
  - Trigger de alertas inmediatas
  - ✅ Anomalías críticas detectadas al instante

- [ ] **Implementar flags de calidad**
  - Campo `quality_flag` en database
  - Valores: 'good', 'suspect', 'bad'
  - Basado en validaciones
  - ✅ Calidad de datos rastreable

- [ ] **Implementar interpolación simple**
  - Para gaps < 5 minutos
  - Interpolación lineal
  - Flag como 'interpolated'
  - ✅ Continuidad de datos mejorada

- [ ] **Implementar alertas de conectividad**
  - Detectar si no hay datos > 5 minutos
  - Enviar email de "Device offline"
  - Log de eventos de conectividad
  - ✅ Administrador notificado de problemas

---

### **Checklist 4.4: Pipeline de Análisis Automatizado** ⏱️ 2-3 horas

- [ ] **Integrar con AnomalyDetector**
  - Importar clase `AnomalyDetector`
  - Análisis cada 5 minutos de buffer
  - Método rápido: Isolation Forest
  - ✅ Detección funcionando en tiempo real

- [ ] **Implementar análisis horario**
  - Cada hora: analizar últimas 24h
  - Ejecutar predicción si hay datos suficientes
  - Actualizar estadísticas
  - ✅ Análisis automático sin intervención

- [ ] **Implementar trigger de alertas**
  - Integrar con `EmailReporter`
  - Alertas críticas: inmediatas
  - Alertas warning: agrupadas (max 1/hora)
  - ✅ Emails de alerta funcionando

- [ ] **Implementar actualización de modelos**
  - Re-entrenar predictor semanalmente
  - Usar datos más recientes
  - Mantener versiones de modelos
  - ✅ Modelos siempre actualizados

- [ ] **Implementar generación de reportes**
  - Reporte diario automático
  - Reporte semanal los lunes
  - Reporte mensual el día 1
  - ✅ Reportes automáticos funcionando

---

## 🔄 FASE 5: Integración con Sistema Existente (1-2 días)

### **Checklist 5.1: Modificación de Módulos** ⏱️ 3-4 horas

- [ ] **Actualizar `src/predictor.py`**
  - Añadir método `load_from_realtime_db()`
  - Adaptar para datos tiempo real
  - Función `predict_next_hours(hours=24)`
  - ✅ Predictor funciona con datos tiempo real

- [ ] **Actualizar `src/anomalies.py`**
  - Añadir método `analyze_realtime_buffer()`
  - Análisis continuo no bloqueante
  - Buffer circular de últimas 100 lecturas
  - ✅ Detección continua funcionando

- [ ] **Actualizar `src/reporting.py`**
  - Añadir función `generate_realtime_report()`
  - Incluir métricas tiempo real
  - Gráficos de últimas 24h
  - ✅ Reportes con datos tiempo real

- [ ] **Actualizar `src/email_sender.py`**
  - Template para alertas IoT
  - Incluir info de dispositivo
  - Estado de conectividad
  - ✅ Emails con contexto IoT

---

### **Checklist 5.2: Configuración y Variables** ⏱️ 1 hora

- [ ] **Actualizar `.env`**
  - Añadir `MQTT_BROKER_HOST`
  - Añadir `MQTT_BROKER_PORT`
  - Añadir `MQTT_USERNAME` (opcional)
  - Añadir `MQTT_PASSWORD` (opcional)
  - Añadir `REALTIME_DB_PATH`
  - Añadir `CRITICAL_POWER_THRESHOLD`

- [ ] **Crear `.env.example`**
  - Template con valores de ejemplo
  - Documentar cada variable
  - Instrucciones de configuración

- [ ] **Actualizar `requirements.txt`**
  - Añadir `paho-mqtt>=1.6.1`
  - Versiones específicas
  - ✅ `pip install -r requirements.txt` funciona

- [ ] **Crear archivo de configuración**
  - `data/config/iot_config.json`
  - Parámetros: sampling_interval, thresholds
  - Documentar estructura
  - ✅ Sistema carga configuración correctamente

---

### **Checklist 5.3: Sistema de Monitoreo** ⏱️ 2-3 horas

- [ ] **Crear script de monitoreo**
  - `scripts/real_time_monitor.py`
  - Loop principal 24/7
  - Integración con scheduler
  - ✅ Script corre indefinidamente sin errores

- [ ] **Implementar health checks**
  - Verificar conectividad MQTT
  - Verificar última lectura ESP32
  - Verificar espacio en disco
  - Verificar uso de memoria
  - ✅ Sistema detecta problemas automáticamente

- [ ] **Implementar dashboard básico**
  - Script simple con print() de métricas
  - Actualización cada 10 segundos
  - Mostrar: último valor, promedio, anomalías
  - ✅ Dashboard funcional en consola

- [ ] **Implementar logging centralizado**
  - Todos los logs en `logs/`
  - Formato consistente
  - Rotación automática
  - ✅ Logs organizados y mantenibles

---

## 🧪 FASE 6: Testing y Validación (1-2 días)

### **Checklist 6.1: Tests de Hardware** ⏱️ 4-6 horas

- [ ] **Test de estabilidad 24h**
  - Dejar ESP32 corriendo 24h continuas
  - Monitorear reconexiones
  - Verificar drift de calibración
  - ✅ Sistema estable sin intervención

- [ ] **Test de precisión**
  - Comparar vs multímetro profesional
  - Medir con cargas conocidas
  - Calcular error promedio
  - Documentar precisión real
  - ✅ Error < 5% en cargas normales

- [ ] **Test de reconexión WiFi**
  - Apagar router 2 minutos
  - Verificar reconexión automática
  - Verificar reenvío de datos buffereados
  - ✅ Reconexión exitosa sin pérdida datos

- [ ] **Test de reconexión MQTT**
  - Detener broker 2 minutos
  - Verificar reconexión automática
  - Verificar buffer funciona
  - ✅ Datos recuperados tras reconexión

- [ ] **Test de pérdida de alimentación**
  - Desconectar y reconectar USB
  - Verificar reinicio limpio
  - Verificar recalibración automática
  - ✅ Sistema se recupera correctamente

- [ ] **Test de calibración**
  - Recalibrar sensor remotamente
  - Verificar mejora de precisión
  - Documentar procedimiento
  - ✅ Calibración remota funciona

---

### **Checklist 6.2: Tests del Sistema Completo** ⏱️ 3-4 horas

- [ ] **Test end-to-end básico**
  - ESP32 → MQTT → Python → Database
  - Verificar flujo completo de datos
  - Verificar timing (< 2 segundos total)
  - ✅ Pipeline completo funcional

- [ ] **Test de detección de anomalías**
  - Simular consumo alto (>5kW)
  - Verificar detección inmediata
  - Verificar email de alerta
  - ✅ Alerta recibida en < 1 minuto

- [ ] **Test de generación de reportes**
  - Ejecutar reporte con datos tiempo real
  - Verificar gráficos e incluyen últimas 24h
  - Verificar estadísticas correctas
  - ✅ Reporte generado correctamente

- [ ] **Test de alertas críticas**
  - Simular sobrecorriente (>30A)
  - Simular sobrevoltaje (>250V)
  - Verificar emails múltiples
  - ✅ Todas las alertas funcionando

- [ ] **Test de performance**
  - Medir latencia end-to-end
  - Medir uso de CPU/RAM
  - Medir velocidad de inserciones DB
  - Documentar métricas
  - ✅ Performance dentro de límites aceptables

---

### **Checklist 6.3: Tests de Robustez** ⏱️ 2-3 horas

- [ ] **Test de fallos de red**
  - Desconectar red 30 minutos
  - Verificar buffer funciona
  - Verificar recuperación al reconectar
  - ✅ No se pierden datos

- [ ] **Test de cortes de luz**
  - Simular corte de luz 5 minutos
  - Verificar database no se corrompe
  - Verificar sistema reinicia correctamente
  - ✅ Sistema resiliente a cortes

- [ ] **Test de integridad de datos**
  - Verificar no hay duplicados en DB
  - Verificar timestamps son correctos
  - Verificar no hay gaps inesperados
  - ✅ Datos íntegros y consistentes

- [ ] **Test de concurrencia**
  - Conectar 2 ESP32 simultáneos (si disponible)
  - Verificar ambos envían datos
  - Verificar no hay conflictos
  - ✅ Sistema soporta múltiples sensores

- [ ] **Test de stress**
  - Enviar 1000 mensajes en 1 minuto
  - Verificar broker maneja carga
  - Verificar Python procesa todo
  - ✅ Sistema maneja picos de tráfico

---

## 📊 FASE 7: Automatización y Deployment (1 día)

### **Checklist 7.1: Scripts de Automatización** ⏱️ 2-3 horas

- [ ] **Script de inicio automático**
  - `scripts/start_domusai_iot.py`
  - Iniciar MQTT ingester
  - Iniciar scheduler
  - Iniciar monitor
  - ✅ Un comando inicia todo el sistema

- [ ] **Script de monitoreo de procesos**
  - Verificar procesos están corriendo
  - Reiniciar si alguno falla
  - Enviar alerta si fallo persiste
  - ✅ Auto-recovery funcional

- [ ] **Script de mantenimiento DB**
  - Vacuum de SQLite mensual
  - Limpiar datos >90 días
  - Optimizar índices
  - ✅ Database se mantiene optimizada

- [ ] **Script de backup automático**
  - Backup diario a las 3am
  - Mantener últimos 30 días
  - Comprimir backups antiguos
  - ✅ Backups automáticos funcionando

- [ ] **Configurar auto-start en boot**
  - Windows: Task Scheduler
  - Linux: systemd service
  - macOS: LaunchAgent
  - ✅ Sistema inicia con el OS

---

### **Checklist 7.2: Documentación de Deployment** ⏱️ 2-3 horas

- [ ] **Crear `hardware/docs/setup_guide.md`**
  - Guía paso a paso instalación hardware
  - Fotos del circuito
  - Esquemas de conexión
  - Troubleshooting común

- [ ] **Crear `hardware/docs/calibration_guide.md`**
  - Procedimiento de calibración inicial
  - Calibración periódica
  - Verificación de precisión
  - Ajustes finos

- [ ] **Crear `hardware/docs/troubleshooting.md`**
  - Problemas comunes y soluciones
  - Códigos de error LED
  - Cómo leer logs
  - Contactos de soporte

- [ ] **Actualizar README.md principal**
  - Sección Sprint 8 completado
  - Instrucciones de uso IoT
  - Arquitectura actualizada
  - Screenshots del sistema

- [ ] **Crear video/GIF demo**
  - Sistema funcionando end-to-end
  - Dashboard en tiempo real
  - Recepción de alerta
  - Subir a repositorio

---

### **Checklist 7.3: Optimización Final** ⏱️ 1-2 horas

- [ ] **Tuning de parámetros**
  - Ajustar intervalos de muestreo
  - Optimizar umbrales de alertas
  - Configurar timeouts
  - ✅ Sistema optimizado

- [ ] **Optimización de memoria**
  - Limpiar buffers no usados
  - Configurar garbage collection
  - Limitar tamaño de logs
  - ✅ Uso de memoria estable

- [ ] **Configurar logs rotativos**
  - Máximo 50MB por log file
  - Comprimir logs antiguos
  - Mantener últimos 7 días
  - ✅ Logs no crecen indefinidamente

- [ ] **Setup de monitoreo de recursos**
  - Script que monitorea CPU/RAM
  - Alertas si uso > 80%
  - Log de métricas de sistema
  - ✅ Monitoreo funcionando

- [ ] **Validar backup/recovery**
  - Test de restauración de backup
  - Verificar todos los datos
  - Documentar procedimiento
  - ✅ Recovery procedure validado

---

## 📚 FASE 8: Documentación Final y Release (1 día)

### **Checklist 8.1: Documentación Completa** ⏱️ 3-4 horas

- [ ] **Actualizar README.md**
  - Sección "Sistema IoT Tiempo Real"
  - Arquitectura completa con diagramas
  - Instrucciones de instalación
  - Screenshots y demos
  - ✅ README refleja estado actual

- [ ] **Documentar API tiempo real**
  - Endpoints de consulta
  - Estructura de datos
  - Ejemplos de uso
  - ✅ API documentada completamente

- [ ] **Crear diagramas de arquitectura**
  - Diagrama de flujo de datos
  - Diagrama de componentes
  - Diagrama de despliegue
  - Guardar en `docs/architecture/`

- [ ] **Guía de usuario final**
  - Cómo instalar sistema completo
  - Cómo calibrar sensores
  - Cómo interpretar reportes
  - Cómo resolver problemas

- [ ] **Documentar casos de uso**
  - Monitoreo hogar individual
  - Monitoreo edificio/comunidad
  - Integración con automatización
  - Expansión futura

---

### **Checklist 8.2: Suite de Tests Final** ⏱️ 2-3 horas

- [ ] **Crear `tests/test_mqtt_ingester.py`**
  - Tests unitarios de MQTTIngester
  - Mocks para broker MQTT
  - Coverage > 80%

- [ ] **Crear `tests/test_realtime_database.py`**
  - Tests de todas las funciones DB
  - Tests de integridad
  - Tests de performance

- [ ] **Crear `tests/test_iot_pipeline.py`**
  - Tests de integración completa
  - Tests end-to-end
  - Tests de recovery

- [ ] **Test de carga completo**
  - Simular 24h de datos
  - Verificar no hay memory leaks
  - Verificar performance estable
  - ✅ Sistema pasa test de carga

- [ ] **Validar métricas finales**
  - Latencia < 2s end-to-end
  - Precisión ±5% vs multímetro
  - Uptime > 99.5%
  - ✅ Métricas dentro de objetivos

---

### **Checklist 8.3: Preparación para Release** ⏱️ 1-2 horas

- [ ] **Checklist de deployment**
  - Todos los tests pasando
  - Documentación completa
  - Backups configurados
  - Monitoreo activo
  - ✅ Sistema production-ready

- [ ] **Configurar alertas de sistema**
  - Alerta si proceso cae
  - Alerta si disco lleno
  - Alerta si sensor offline
  - ✅ Alertas configuradas

- [ ] **Plan de escalabilidad**
  - Cómo añadir más sensores
  - Cómo escalar análisis
  - Consideraciones de red
  - Documentado en `docs/scaling.md`

- [ ] **Plan de mantenimiento**
  - Calendario de calibraciones
  - Calendario de backups
  - Procedimientos de actualización
  - Documentado en `docs/maintenance.md`

- [ ] **Documentar troubleshooting**
  - Top 10 problemas comunes
  - Soluciones paso a paso
  - Logs a revisar
  - Contactos de soporte

---

## 📅 Cronograma y Milestones

### **Semana 1**
- **Días 1-3**: Fases 1-2 (Hardware + MQTT Broker)
  - ✅ Milestone 1: Hardware funcionando, broker configurado
  - Deliverable: ESP32 conectándose a MQTT

- **Días 4-5**: Fase 3.1-3.2 (Programación ESP32 básica)
  - ✅ Milestone 2: ESP32 enviando datos reales
  - Deliverable: Datos visibles en MQTT Explorer

### **Semana 2**
- **Días 6-7**: Fase 3.3-3.4 + Fase 4.1 (ESP32 completo + Python inicio)
  - ✅ Milestone 3: Sistema básico funcionando
  - Deliverable: Python recibiendo datos del ESP32

- **Días 8-9**: Fase 4.2-4.4 (Database + validación)
  - ✅ Milestone 4: Pipeline de datos completo
  - Deliverable: Datos almacenados en database

- **Día 10**: Fase 5 (Integración)
  - ✅ Milestone 5: Sistema integrado con módulos existentes
  - Deliverable: Alertas automáticas funcionando

### **Semana 3**
- **Días 11-12**: Fase 6 (Testing completo)
  - ✅ Milestone 6: Sistema validado y robusto
  - Deliverable: Todos los tests pasando

- **Día 13**: Fase 7 (Automatización)
  - ✅ Milestone 7: Sistema productizado
  - Deliverable: Auto-start configurado

- **Día 14**: Fase 8 (Documentación final)
  - ✅ Milestone 8: Sistema documentado
  - Deliverable: README.md actualizado

- **Día 15**: Buffer y release
  - ✅ **DomusAI v1.0 RELEASE** 🎉
  - Deliverable: Release notes y sistema en producción

---

## 🎯 Criterios de Éxito

### **Objetivos Mínimos (DomusAI v1.0)** ✅ REQUERIDOS
- [x] ESP32 enviando datos cada 30 segundos vía MQTT
- [x] Python recibiendo y almacenando datos en SQLite
- [x] Detección de anomalías automática en tiempo real
- [x] Alertas de email por anomalías críticas (< 1 min)
- [x] Sistema funcionando 24h sin intervención manual
- [x] Precisión ±5% vs multímetro
- [x] Uptime > 95%

### **Objetivos Deseables (DomusAI v1.1)** 🌟 OPCIONAL
- [ ] Dashboard web tiempo real básico
- [ ] Soporte para 2+ sensores ESP32 simultáneos
- [ ] API REST para consultas externas
- [ ] Sistema de backup automático diario
- [ ] Métricas de performance detalladas
- [ ] Mobile-responsive dashboard

### **Objetivos Aspiracionales (DomusAI v2.0)** 🚀 FUTURO
- [ ] InfluxDB para series temporales optimizadas
- [ ] Dashboard Grafana profesional
- [ ] Sistema distribuido (múltiples brokers)
- [ ] Machine Learning adaptativo continuo
- [ ] App móvil Android/iOS
- [ ] Integración con Home Assistant

---

## 💰 Presupuesto y ROI

### **Inversión Total**
| Componente | Precio (USD) | Cantidad | Total |
|------------|--------------|----------|-------|
| ESP32 DevKit | $8-12 | 2 unidades | $16-24 |
| Sensor ACS712 30A | $3-5 | 2 unidades | $6-10 |
| Breadboard + cables | $5-8 | 1 kit | $5-8 |
| Resistencias + LED | $2-3 | 1 pack | $2-3 |
| **SUBTOTAL HARDWARE** | | | **$29-45** |
| Software (Python, etc.) | $0 | Open Source | $0 |
| **TOTAL PROYECTO** | | | **$29-45** |

### **Comparación con Alternativas**
- **Solución Comercial IoT**: $200-500 USD
- **Smart Meter Profesional**: $150-300 USD  
- **Sistema Enterprise**: $1000+ USD

**🎯 ROI de DomusAI**: Sistema completo por **< $50 USD** (ahorro 80-95%)

### **Ahorro Energético Estimado**
- Identificación de consumos fantasma: **5-10%** ahorro mensual
- Optimización horarios: **10-15%** ahorro mensual
- Detección de ineficiencias: **5-10%** ahorro mensual
- **Total estimado**: **20-35%** reducción de factura eléctrica

Si factura mensual = $100 USD → Ahorro $20-35/mes → **ROI en 2-3 meses**

---

## 📞 Soporte y Recursos

### **Documentación Técnica**
- **ESP32**: https://docs.espressif.com/projects/esp-idf/
- **MQTT Protocol**: https://mqtt.org/
- **Mosquitto**: https://mosquitto.org/documentation/
- **Paho MQTT Python**: https://pypi.org/project/paho-mqtt/
- **ACS712 Datasheet**: [Buscar en Google "ACS712 datasheet"]

### **Comunidades**
- **ESP32 Forum**: https://esp32.com/
- **MQTT Community**: https://mqtt.org/community/
- **Arduino Forum**: https://forum.arduino.cc/
- **Stack Overflow**: Tag `esp32`, `mqtt`, `iot`

### **Contacto del Proyecto**
- **GitHub**: https://github.com/ddani22/DomusAI
- **Issues**: https://github.com/ddani22/DomusAI/issues
- **Discussions**: https://github.com/ddani22/DomusAI/discussions

---

## 📝 Notas Importantes

### **⚠️ Advertencias de Seguridad**
1. **NUNCA** trabajes con cables de línea energizados
2. **SIEMPRE** apaga el disyuntor antes de instalar
3. **USA** guantes aislantes y herramientas aisladas
4. **CONSULTA** a un electricista si no tienes experiencia
5. **VERIFICA** voltajes con multímetro antes de tocar

### **💡 Tips para Éxito**
1. **Empieza simple**: Primero haz funcionar lo básico
2. **Documenta todo**: Toma fotos, guarda logs, anota problemas
3. **Testea incremental**: Valida cada componente antes de integrar
4. **Usa Git**: Commitea cambios frecuentemente
5. **Pide ayuda**: La comunidad IoT es muy colaborativa

### **🔄 Siguientes Pasos Post-Sprint 8**
- **Sprint 9**: Dashboard Web Profesional (Grafana/Plotly Dash)
- **Sprint 10**: Machine Learning Adaptativo
- **Sprint 11**: App Móvil (React Native)
- **Sprint 12**: Integración con Home Automation (Home Assistant)

---

## ✅ Checklist General de Sprint 8

### **Preparación**
- [ ] Hardware comprado y recibido
- [ ] Arduino IDE instalado y configurado
- [ ] MQTT Broker instalado y funcionando
- [ ] Entorno Python configurado

### **Desarrollo**
- [ ] ESP32 programado y funcionando
- [ ] Datos fluyendo por MQTT
- [ ] Python recibiendo datos
- [ ] Database almacenando correctamente

### **Integración**
- [ ] Sistema integrado con módulos existentes
- [ ] Alertas automáticas funcionando
- [ ] Reportes incluyendo datos tiempo real
- [ ] Pipeline completo end-to-end

### **Testing**
- [ ] Tests de hardware pasando
- [ ] Tests de software pasando
- [ ] Test de 24h estabilidad exitoso
- [ ] Precisión validada vs multímetro

### **Deployment**
- [ ] Scripts de automatización creados
- [ ] Auto-start configurado
- [ ] Backups automáticos funcionando
- [ ] Monitoreo activo

### **Documentación**
- [ ] README.md actualizado
- [ ] Guías de usuario completadas
- [ ] Troubleshooting documentado
- [ ] Release notes escritas

### **Release**
- [ ] Todos los criterios de éxito cumplidos
- [ ] Sistema funcionando en producción
- [ ] **DomusAI v1.0 RELEASED** 🎉

---

**🎉 ¡Comencemos el Sprint 8 y completemos DomusAI v1.0!**

**Fecha de inicio objetivo**: Octubre 13, 2025  
**Fecha de finalización objetivo**: Noviembre 3, 2025  
**Duración**: 3 semanas

**Estado actual**: ✅ Sprint 7 completado → 🚀 Listo para Sprint 8

---

*Última actualización: Octubre 13, 2025*  
*Documento: SPRINT_8_PLAN.md*  
*Versión: 1.0*  
*Proyecto: DomusAI - Sistema de Monitoreo Energético Inteligente*
