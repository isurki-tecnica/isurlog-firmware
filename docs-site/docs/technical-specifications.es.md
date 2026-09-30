# Ficha Técnica

Referencia de una sola página con las especificaciones de hardware del ISURLOG. Para saber cómo cablear, configurar o programar cualquiera de estos elementos, ver [1. Conexión de Sensores](sensor-connections.md) en adelante.

## Física

| | |
| :--- | :--- |
| **Dimensiones** | 144 × 145 × 80 mm |
| **Peso** | ~540 g (sin baterías ni accesorios de montaje DIN) |
| **Carcasa** | Impresa en 3D en PETG, **IP66** |
| **Montaje** | Pared (patrón de agujeros 125 × 125 mm) o carril DIN — ver [4.2. Montaje Físico](installation-commissioning.md#42-montaje-fisico) |
| **Temperatura de funcionamiento** | -20 °C a +60 °C |
| **Certificación** | CE. Diseñado siguiendo los requisitos del Cyber Resilience Act (CRA) |

## Alimentación

| | |
| :--- | :--- |
| **Corriente en reposo profundo** | Hasta ~20 µA (sistema completo, módem incluido y conectado a red) — ver [1. Gráficos de Consumo](consumption-graphs.md) |
| **Baterías** | 1–5× Li-Ion 18650 (recargables, hasta 17000 mAh en total), o hasta 2× Li-SOCl2 no recargables (hasta 38000 mAh en total, requiere PCB v3.3+) |
| **Entradas de carga** | TEG de 0.3V, panel solar micro, panel solar de 5V completo, o cargador USB — cargador de recolección de energía integrado (solo con Li-Ion; no se usa con Li-SOCl2) |
| **Salidas de alimentación para sensores** | Regulador configurable por software, 9–24 V; más un regulador fijo de 5 V independiente |

## Conectividad

Un módulo de conectividad por unidad, fijado en fábrica:

| | |
| :--- | :--- |
| **Celular** | NB-IoT / LTE-M, satélite (NTN), y DECT NR+ (compatible a nivel de chip vía el nRF9151; el soporte por firmware está planeado, todavía no disponible — ver la [Hoja de ruta](index.md#hoja-de-ruta)). |
| **LoRaWAN** | Clase A (Clase B/C soportadas, no recomendadas para uso a batería) |
| **Wi-Fi** | 802.11 b/g/n, 2.4 GHz (ESP32) |
| **Bluetooth (BLE)** | Bluetooth v4.2 BR/EDR + BLE (ESP32). Bajo demanda, activado por imán — ver [1.8. Sensores Internos y Diagnóstico](sensor-connections.md#18-sensores-internos-y-diagnostico) |
| **eSIM** | Integrada, 500 MB o 5 años (lo que ocurra antes) — ver [1. Piezas y Accesorios](parts-and-accessories.md) |
| **Slot Nano SIM** | También disponible un slot externo para Nano-SIM (p. ej. para servicio satelital/NTN con una SIM de terceros) |

## Entradas y Salidas

### Entradas

| Entrada | Especificación |
| :--- | :--- |
| **Analógica (4-20 mA)** | 4 canales (AIN0–AIN3), resolución de ADC de 16 bits, compatible con sensores pasivos (alimentados por el ISURLOG) y activos (alimentación externa) — ver [1.1. Entradas Analógicas (4-20mA)](sensor-connections.md#11-entradas-analogicas-4-20ma) |
| **Digital** | 1 canal, tipo contacto seco (el ISURLOG entrega la señal positiva, el sensor la devuelve) — lectura de estado o contador de pulsos, ancho de pulso mínimo 200 ms — ver [1.2. Entrada Digital (Estado y Contador de Pulsos)](sensor-connections.md#12-entrada-digital-estado-y-contador-de-pulsos) |
| **E/S digital adicional** | 3 canales de propósito general (GP3–GP5), a través del expansor de E/S integrado — lectura de estado, no contador de pulsos por ULP como la entrada digital principal — ver [1.7. Conector AUX-IO](sensor-connections.md#17-conector-aux-io) |
| **Modbus (RS485)** | Hasta 32 sensores, resistencia de terminación de 120 Ω integrada. Velocidades soportadas en firmware estándar: 9600 / 19200 / 38400 / 57600 / 115200 — ver [1.3. Entrada Modbus (RS485)](sensor-connections.md#13-entrada-modbus-rs485) |
| **PT100 / PT1000** | 1 canal, resolución de ADC de 15 bits, resolución nominal ~0.03125 °C (varía según la no linealidad de la RTD), precisión total máxima ±0.5 °C (0.05% del fondo de escala) en todas las condiciones de funcionamiento — ver [1.4. Entrada para Sensor de Temperatura PT100](sensor-connections.md#14-entrada-para-sensor-de-temperatura-pt100) |
| **I2C (QWIIC)** | Entrada I2C para sensores de expansión conectables, conector QWIIC estándar — ver [1.6. Puerto I2C QWIIC](sensor-connections.md#16-puerto-i2c-qwiic) |
| **Temperatura y humedad interna** | Integrado, dentro de la carcasa — aviso temprano de entrada de agua o sobrecalentamiento — ver [1.8. Sensores Internos y Diagnóstico](sensor-connections.md#18-sensores-internos-y-diagnostico) |
| **Acelerómetro** | Integrado, detección de manipulación/vandalismo con umbrales de alarma configurables — ver [1.8. Sensores Internos y Diagnóstico](sensor-connections.md#18-sensores-internos-y-diagnostico) |

### Salidas

| Salida | Especificación |
| :--- | :--- |
| **Relé (bloque de terminales principal)** | 1× relé de estado sólido, normalmente abierto (COM0/NO0), máx. 60 V / 2 A — ver [1.5. Salida Digital (Relé)](sensor-connections.md#15-salida-digital-rele) |
| **Relés (AUX-IO)** | 2× relés de estado sólido adicionales, normalmente abiertos, máx. 60 V / 500 mA por canal — ver [1.7. Conector AUX-IO](sensor-connections.md#17-conector-aux-io) |

## Software

| | |
| :--- | :--- |
| **Firmware** | MicroPython, código abierto (GPL-3.0) — [GitHub](https://github.com/isurki-tecnica/isurlog-firmware) |
| **Plataforma en la nube** | [IsurDASH](https://isurdash.isurki.com) — gratuita, almacenamiento de datos ilimitado, sin coste por dispositivo |
| **Acceso a datos** | Histórico (InfluxDB) y en tiempo real (MQTT) — ver [1. Resumen de Acceso a Datos](data-access-overview.md) |
