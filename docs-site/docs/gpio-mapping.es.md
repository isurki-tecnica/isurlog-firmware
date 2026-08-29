# 4. Mapeo de GPIO (Hardware-Software)

Esta sección detalla los pines usados por el datalogger **ISURLOG** en el ESP32 y sus funciones específicas, sirviendo de interfaz entre el firmware MicroPython y los periféricos de la placa.

## 4.1 Controles de Alimentación y Habilitación

Estos GPIO controlan los reguladores de alimentación principales y los módulos de comunicación, permitiendo al dispositivo optimizar el consumo de energía durante los modos de reposo profundo.

| Pin | Función | Descripción |
| :--- | :--- | :--- |
| **GPIO5** | Habilitar nRF9160 | Controla la alimentación del módulo de comunicación NB-IoT. Pull-down. |
| **GPIO18** | Habilitar VDC | Activa el convertidor elevador de 6-24V. Esta alimentación se usa para los sensores conectados al terminal de presión VDC. Corriente máxima de 2A. Pull-down. |
| **GPIO13** | Habilitar 5V | Activa el convertidor elevador fijo de 5V. Corriente máxima de 150mA. Pull-down. |

## 4.2 Entradas Analógicas y Digitales

| Pin | Función | Descripción |
| :--- | :--- | :--- |
| **GPIO39** | Entrada Digital 0 | Entrada digital 0, contacto libre de potencial. |
| **GPIO35** | Despertar desde el Módulo NB-IoT | Entrada digital usada para despertar el ESP32 cuando el módulo NB-IoT está en modo eDRX y recibe un paquete de datos. |
| **GPIO26** | Despertar al Módulo NB-IoT | Salida digital usada por el ESP32 para despertar el módulo NB-IoT cuando este está en modo de reposo. |
| **GPIO36** | Despertar desde el Interruptor Magnético | Entrada digital usada para despertar el ESP32 cuando el interruptor magnético de bajo consumo detecta un campo magnético cercano. |
| **GPIO34** | Despertar desde el MCP23008 | Entrada digital usada para despertar el ESP32 cuando el MCP23008 genera un evento de interrupción. |

## 4.3 Salida Digital a Relé

| Pin | Función | Descripción |
| :--- | :--- | :--- |
| **GPIO25** | Habilitar SD0 | Activa el relé de estado sólido del **ISURLOG**. Conmutación máxima de 2A. |

## 4.4 Interfaces de Comunicación Serie

### RS485 (mediante Conversor MAX485)

| Pin | Función | Descripción |
| :--- | :--- | :--- |
| **GPIO23** | DI MAX485 | Conectado al pin DI del conversor MAX485. |
| **GPIO14** | RO MAX485 | Conectado al pin RO del conversor MAX485. |
| **GPIO33** | RE/DE MAX485 | Conectado al pin RE/DE del conversor MAX485. |

### Línea UART Compartida (Módems NB-IoT y LoRaWAN)

| Pin | Función | Descripción |
| :--- | :--- | :--- |
| **GPIO2** | RX nRF9160/RAK3172 | Pin RX para el módem NB-IoT/LoRaWAN. |
| **GPIO4** | TX nRF9160/RAK3172 | Pin TX para el módem NB-IoT/LoRaWAN. |

### Línea SPI (para MAX31865)

| Pin | Función | Descripción |
| :--- | :--- | :--- |
| **GPIO19** | MOSI | Pin MOSI del módulo MAX31865. |
| **GPIO27** | MISO | Pin MISO del módulo MAX31865. |
| **GPIO12** | SCK | Pin SCK del módulo MAX31865. |
| **GPIO15** | NSS | Selección de chip (chip select) del módulo MAX31865. |

### Línea I2C (Compartida entre RV-3028, ADS1115, MAX17048, LIS2DH12, 24LC1025, MCP23008, MCP4017 y SHT30)

| Pin | Función | Descripción |
| :--- | :--- | :--- |
| **GPIO21** | I2C SDA | Pin SDA del I2C. |
| **GPIO22** | I2C SCL | Pin SCL del I2C. |

## 4.5 Pinout del Expansor de I/O MCP23008

El MCP23008 (accesible a través del bus I2C compartido de arriba) añade 8 pines GPIO adicionales (GP0-GP7), conectados de la siguiente forma:

| Pin MCP | Función | Descripción |
| :--- | :--- | :--- |
| **INT** | Salida de interrupción | Va al **GPIO34** del ESP32 — ver **[4.2 Entradas Analógicas y Digitales](#42-entradas-analogicas-y-digitales)** ("Despertar desde el MCP23008"). |
| **GP0** | Interrupción RV3028 | Conectado a la salida de interrupción del RTC RV3028. |
| **GP1** | Habilitar SSR 1 | Habilita el primer relé del relé de estado sólido doble (GAQW212GEH). |
| **GP2** | Habilitar SSR 2 | Habilita el segundo relé del relé de estado sólido doble (GAQW212GEH). |
| **GP3** | AUX-IO — Pin 6 | Conectado directamente al pin 6 del conector AUX-IO del ISURLOG. |
| **GP4** | AUX-IO — Pin 7 | Conectado directamente al pin 7 del conector AUX-IO del ISURLOG. |
| **GP5** | AUX-IO — Pin 8 | Conectado directamente al pin 8 del conector AUX-IO del ISURLOG. |
| **GP6** | LIS2DH12 INT1 | Conectado a la salida de interrupción INT1 del acelerómetro. |
| **GP7** | LIS2DH12 INT2 | Conectado a la salida de interrupción INT2 del acelerómetro. |
