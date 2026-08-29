# 7. Referencia de Parámetros de Configuración

Esta sección detalla el significado de cada parámetro configurable en un **ISURLOG** a través de la plataforma IsurDASH.

## 7.1. Parámetros Generales

Estos parámetros afectan al comportamiento global del datalogger.

### Tiempo de latencia (min)

* **Descripción:** define la frecuencia con la que el **ISURLOG** sale del modo de reposo profundo para realizar un ciclo completo de lectura de sensores.
* **Valores:** actualmente configurable en intervalos predefinidos de 5, 10, 15, 30, 60 o 120 minutos. (El propio firmware admite hasta 255 minutos — el rango de IsurDASH se actualizará para igualarlo en una futura versión.)
* **Ejemplo:** un valor de **60** hace que el dispositivo tome una muestra de datos cada hora.

### Tensión de alimentación sensores (Voltios)

!!! note "Nota de hardware"
    Disponible solo en **ISURLOG v3.0 y posteriores**.

* **Descripción:** configura la tensión de alimentación entregada a los sensores a través de los terminales de presión marcados como **VDC**.
* **Valores:** 9, 12, 18 o 24 V.

### Modo de registro

* **Descripción:** determina la lógica que usa el **ISURLOG** para decidir cuándo debe transmitir los datos acumulados. Este parámetro es fundamental para la gestión de alarmas.
* **Opciones:**
    * **Fijo:** en este modo, el **ISURLOG** transmite datos únicamente cuando se completa el número de ciclos definido en el **Acumulador de registros**. Las alarmas que puedan generarse se guardan en el registro, pero no fuerzan un envío inmediato.
    * **Condicional:** en este modo, el **ISURLOG** transmite si se cumple cualquiera de estas dos condiciones: 1) se ha completado el recuento de ciclos del **Acumulador de registros**, o 2) se ha detectado una condición de alarma en alguno de los sensores. Este modo garantiza que los eventos críticos se notifiquen al instante.

### Tamaño del payload (bytes)

* **Descripción:** define el tamaño del paquete de datos (payload) que transmite el ISURLOG. Este valor debe ajustarse para asegurar que sea lo bastante grande como para acomodar todos los sensores activados actualmente. Elegir un tamaño de payload menor es más eficiente, ya que permite al dispositivo acumular un mayor número de registros en su RAM interna antes de subirlos a la nube. Actualmente se puede elegir entre 32, 64 o 128 bytes. Para optimizar el tamaño del payload, consultar la siguiente tabla:

| Nombre del Sensor | Tamaño (caracteres hex) |
| :--- | :--- |
| **Entrada Digital** | 6 |
| **Entrada Analógica** | 8 |
| **Entrada Modbus** | 8 |
| **Temperatura PT100** | 8 |
| **Temperatura Interna** | 8 |
| **Humedad Interna** | 6 |
| **Tensión de Batería** | 8 |
| **Marca de Tiempo Unix** | 12 |

* **Ejemplo:** si el datalogger está configurado con 2 entradas analógicas (2*8), 2 entradas modbus (2*8), la tensión de batería (1*8) y la marca de tiempo Unix, siempre obligatoria (1*12), el total es 52. En este caso, el tamaño de payload óptimo a configurar sería 64 bytes.

### Acumulador de registros

* **Descripción:** controla cuántos ciclos de lectura (registros) debe almacenar el **ISURLOG** en su memoria interna antes de realizar una transmisión de datos a la plataforma IsurDASH.
* **Ejemplo:** si el Tiempo de latencia es de **10 minutos** y el Acumulador es **6**, el **ISURLOG** se despertará cada 10 minutos para leer, pero solo se conectará a la red y enviará los 6 registros acumulados cada **60 minutos**, optimizando así el consumo de batería.

### Latitud y longitud

* **Descripción:** permite establecer las coordenadas geográficas (en grados decimales) donde está instalado el dispositivo. Esta información se usa para posicionar correctamente el **ISURLOG** en el mapa del Dashboard.

### Sincronización RTC

* **Descripción:** este parámetro (activado/desactivado) controla si las lecturas de sensores se realizan en intervalos de tiempo fijos y predecibles (sincronizados con el reloj) o en intervalos relativos al momento de encendido del dispositivo.
* **Opciones:**
    * **Activado (Recomendado):** con esta opción activada, el **ISURLOG** ajusta su ciclo de trabajo para realizar las lecturas en múltiplos exactos del tiempo de latencia.
        * **Ejemplo:** si el Tiempo de latencia es de 5 minutos, el dispositivo programará sus lecturas para que ocurran en la hora en punto, y cinco, y diez, etc. (p. ej. 14:00, 14:05, 14:10).
    * **Desactivado:** si la sincronización está desactivada, el **ISURLOG** realizará la primera lectura en el momento en que se enciende, y las lecturas siguientes ocurrirán en intervalos relativos a ese momento de inicio.
        * **Ejemplo:** si el Tiempo de latencia es de 5 minutos y el dispositivo se enciende a las 14:12, las siguientes lecturas ocurrirán a las 14:17, 14:22, 14:27, y así sucesivamente.

### Alarmas por vandalismo

!!! note "Nota de hardware/firmware"
    Disponible solo en **ISURLOG v3.0 y posteriores**, con firmware **1.1.6 o posterior**.

* **Descripción:** activa el envío de alarmas de vandalismo. El dispositivo usa su acelerómetro interno para detectar movimiento, y el módem NB-IoT (NRF9151) para obtener coordenadas GPS. Cada vez que se detecta movimiento, envía las coordenadas actuales a través de los canales de notificación configurados por el usuario.
* **Nota de consumo:** dado que el acelerómetro LIS2DH12 debe permanecer en modo activo (de bajo consumo) para que esta función opere, añade un pequeño consumo extra. Esto sigue siendo compatible con el funcionamiento a batería, pero conviene tenerlo en cuenta al dimensionar la duración de la batería.

## 7.2. Parámetros de Comunicaciones Inalámbricas

Estos parámetros configuran el método inalámbrico que usa el **ISURLOG** para comunicarse con la plataforma (broker MQTT, ajustes celulares NB-IoT/LTE-M, credenciales LoRaWAN, o credenciales Wi-Fi, según el módem instalado).

!!! note "Importante"
    A diferencia del resto de parámetros de esta página, los parámetros de comunicación inalámbrica **no son editables de forma remota por downlink** — dado que un valor incorrecto podría cortar la conectividad por completo, solo pueden editarse **localmente por Bluetooth** (ver **[5.1 Modo de Diagnóstico por Bluetooth](datalogger-operation.md#51-modo-de-diagnostico-por-bluetooth-activado-por-iman)**). Disponible desde el firmware **1.0.8 o posterior**.

Los campos mostrados dependen de qué módulo de comunicación esté instalado — NB-IoT/LTE-M, LoRaWAN o Wi-Fi.

### MQTT (NB-IoT/LTE-M y Wi-Fi)

* **Servidor:** dirección IP o nombre de host del broker MQTT.
* **Puerto:** puerto del broker MQTT.
* **Usuario:** nombre de usuario para la autenticación MQTT.
* **Contraseña:** contraseña para la autenticación MQTT.
* **Topic:** topic base de MQTT en el que publica el dispositivo.
* **Registrar calidad de red:** casilla, **solo NB-IoT, firmware 1.1.6 o posterior**. Si se activa, el dispositivo añade la lectura de calidad de señal NB-IoT (RSRQ/RSRP) al último payload de cada lote de transmisión — ver **[3.4 Decodificación del Payload (NB-IoT/Cayenne LPP)](realtime-data-mqtt.md#34-decodificacion-del-payload-nb-iotcayenne-lpp)**.

### NB-IoT/LTE-M

* **APN:** nombre del punto de acceso para la conexión de datos celular.
* **SIM externa:** casilla. Alterna entre la eSIM integrada y una Nano-SIM externa — ver **[3.2 Flexibilidad en la Gestión de la SIM](communications.md#flexibilidad-en-la-gestion-de-la-sim)**.
* **Preferencia de conexión:** desplegable — **Automático**, **LTE-M**, o **NB-IoT**. Selecciona con qué tecnología celular debe conectarse el módem.
    * **Nota:** **Automático** todavía no está totalmente soportado por el firmware — al seleccionarlo, el dispositivo recurre por defecto a NB-IoT.

### LoRaWAN

* **DEV EUI:** EUI de dispositivo LoRaWAN.
* **APP EUI:** EUI de aplicación LoRaWAN.
* **APP KEY:** clave de aplicación LoRaWAN (OTAA).
* **Clase LoRaWAN:** desplegable — clase de dispositivo (A, B o C).
* **Downlinks confirmados:** casilla. Si se activa, el dispositivo solicita confirmación de la red para los mensajes downlink.

### Wi-Fi

* **Wifi SSID:** nombre de la red Wi-Fi a la que conectarse.
* **Wifi Pass:** contraseña de la red Wi-Fi.
* Además de los mismos parámetros de **MQTT** descritos arriba.

## 7.3. Parámetros de Configuración de Batería

!!! note "Nota de hardware/firmware"
    Disponible solo en **ISURLOG v3.0 y posteriores**, con firmware **1.1.9 o posterior**.

Estos parámetros configuran cómo se informa y monitoriza la batería del **ISURLOG**.

* **Tipo de batería:** desplegable — **Recargable (Li-Ion)** o **No recargable (Li-SOCl2)** — ver **[2.1.4 Baterías No Recargables (Li-SOCl2)](power-supply.md#214-baterias-no-recargables-li-socl2)** para la configuración de hardware correspondiente.
    * **Importante:** este parámetro **no** afecta al comportamiento del propio firmware del ISURLOG. Lo usa exclusivamente **IsurDASH** para convertir correctamente la tensión de batería reportada en un porcentaje, y aplicar los umbrales de batería baja adecuados según la química de batería seleccionada.
* **Registrar variación de batería:** casilla. Activa el registro de la tasa de carga/descarga de la batería (**C-Rate**).
* **Activar alarmas de batería baja:** casilla. Activa o desactiva las notificaciones de alarma de batería baja.

## 7.4. Parámetros de Sensores

Estos parámetros se configuran al añadir o editar un sensor concreto desde el "Listado de Sensores" en la pestaña de configuración del dispositivo.

### Sensor Analógico (Entradas 4-20mA)

Esta sección permite configurar cualquiera de las **cuatro entradas analógicas** del **ISURLOG** para leer sensores con salida de corriente 4-20mA, ya sean activos (alimentación externa) o pasivos (alimentados por el **ISURLOG**).

!!! note "Ver También"
    Para el esquema de conexión física de los sensores a los terminales, consultar la sección **[1. Conexión de Sensores](sensor-connections.md)**.

#### Parámetros de Entrada Analógica

* **Número de entrada analógica:**
    * **Descripción:** selecciona el terminal físico de la placa **ISURLOG** (numerado del **0 al 3**) al que está conectado el sensor.
* **Tiempo preadquisición (ms):**
    * **Descripción:** define un tiempo de espera en milisegundos (ms) desde que el **ISURLOG** alimenta la salida de 12V hasta que realiza la lectura. Es útil para sensores que necesitan tiempo para estabilizarse tras encenderse.
* **Descripción:**
    * **Descripción:** un nombre o texto descriptivo para identificar esta entrada en la plataforma IsurDASH (p. ej. "Nivel Depósito Norte", "Presión Bomba 2").
* **Unidad:**
    * **Descripción:** las unidades de ingeniería en las que se mostrará el valor medido tras la conversión (p. ej. "m", "bar", "pH").
* **Cero:**
    * **Descripción:** el valor de ingeniería que corresponde a la lectura de **4mA** del sensor.
    * **Ejemplo:** si un sensor de nivel de 0 a 5 metros mide 4mA cuando el depósito está vacío, el valor de "Cero" sería **0**.
* **Fondo de escala:**
    * **Descripción:** el valor de ingeniería que corresponde a la lectura de **20mA** del sensor.
    * **Ejemplo:** para ese mismo sensor de nivel de 0 a 5 metros, el "Fondo de escala" sería **5**, ya que corresponde a la lectura de 20mA cuando el depósito está lleno.
* **Alarma de bajo:**
    * **Descripción:** define el umbral numérico inferior para esta entrada. Si el valor medido (en sus unidades de ingeniería) cae por debajo de este umbral, se registra una alarma.
* **Alarma de alto:**
    * **Descripción:** define el umbral numérico superior. Si el valor medido supera este umbral, se registra una alarma.
* **Activar alarma de bajo:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar alarma de alto:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar condición de alarmas de bajo:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de valor bajo fuerza una **transmisión de datos inmediata** cuando el Modo de registro está configurado como "**Condicional**".
* **Activar condición de alarmas de alto:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de valor alto fuerza una **transmisión inmediata** cuando el Modo de registro está configurado como "**Condicional**".

### Sensor Digital

Esta sección detalla la configuración de la entrada digital del **ISURLOG**. La entrada puede funcionar como detector de estado (abierto/cerrado) o como contador de pulsos.

!!! note "Ver También"
    Para el esquema de conexión física del sensor a los terminales, consultar la sección **[1. Conexión de Sensores](sensor-connections.md)**.

#### Parámetros del Sensor Digital

* **Descripción:**
    * **Descripción:** un nombre o texto descriptivo para identificar esta entrada en la plataforma IsurDASH (p. ej. "Contador de Agua Finca", "Alarma Escotilla Barco").
* **Unidad:**
    * **Descripción:** la unidad de medida del valor registrado. En modo "Contador", puede ser "pulsos", "litros", "m³", "kW", etc.
* **Modo:**
    * **Descripción:** define el comportamiento de la entrada digital.
    * **Opciones:**
        * **Estado:** en este modo, el **ISURLOG** lee y registra el estado binario de la entrada en cada ciclo: **1** (activo/cerrado) o **0** (inactivo/abierto).
        * **Contador:** en este modo, el **ISURLOG** utiliza su procesador de ultra bajo consumo para contar los pulsos recibidos, incluso mientras el dispositivo está en reposo profundo. En cada ciclo de lectura se registra el número total de pulsos contados desde el último reinicio del contador.
* **Valor impulso:**
    * **Descripción:** parámetro aplicable solo en modo "Contador". Permite asignar un peso o valor a cada pulso contado para convertirlo a unidades de ingeniería. El valor final registrado será (Número de Pulsos) x (Valor impulso).
    * **Ejemplo:** si un contador de agua emite un pulso por cada 10 litros, el "Valor impulso" debería configurarse a **10**.
* **Pulsos para despertar:**
    * **Descripción:** parámetro aplicable solo en modo "Contador". Define un número de pulsos que, al alcanzarse, despierta de inmediato al **ISURLOG** y fuerza una transmisión de datos, sin esperar al siguiente Tiempo de latencia.
* **Alarma de bajo:**
    * **Descripción:** define el umbral numérico inferior. Si el valor final medido (el estado, o los pulsos multiplicados por su valor) cae por debajo de este umbral, se registra una alarma.
* **Alarma de alto:**
    * **Descripción:** define el umbral numérico superior. Si el valor final medido supera este umbral, se registra una alarma.
* **Activar alarma de bajo:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar alarma de alto:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar condición de alarmas de bajo:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de valor bajo fuerza una **transmisión de datos inmediata** cuando el Modo de registro está configurado como "**Condicional**".
* **Activar condición de alarmas de alto:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de valor alto fuerza una **transmisión inmediata** cuando el Modo de registro está configurado como "**Condicional**".

### Entradas Modbus (RS485)

Esta sección permite configurar lecturas de dispositivos externos que utilizan el protocolo Modbus RTU a través de la interfaz RS485 del **ISURLOG**.

!!! note "Ver También"
    Para el esquema de cableado físico de los sensores al bus RS485, consultar la sección **[1. Conexión de Sensores](sensor-connections.md)**.

#### Parámetros Modbus

* **Número de entrada modbus:**
    * **Descripción:** un identificador virtual para una lectura Modbus (el **ISURLOG** admite hasta 4). Es importante señalar que, aunque se pueden configurar varias entradas, todos los sensores Modbus están conectados físicamente al mismo bus RS485.
* **Baudrate:**
    * **Descripción:** define la velocidad de transmisión para la comunicación modbus.
* **Data bits:**
    * **Descripción:** define los bits de datos para la comunicación modbus.
* **Stop bits:**
    * **Descripción:** define los bits de parada para la comunicación modbus.
* **Parity:**
    * **Descripción:** define la paridad para la comunicación modbus.
* **Tiempo preadquisición (ms):**
    * **Descripción:** define un tiempo de espera en milisegundos (ms) desde que el **ISURLOG** alimenta los sensores externos hasta que inicia la comunicación Modbus. Es útil para dar tiempo a los esclavos Modbus a arrancar y estabilizarse.
* **Descripción:**
    * **Descripción:** un nombre o texto descriptivo para identificar esta lectura en la plataforma (p. ej. "Estado Bomba 1", "Analizador de Cloro").
* **Unidad:**
    * **Descripción:** las unidades en las que se mostrará el valor leído (p. ej. "RPM", "mg/L", "Estado").
* **Dirección esclavo:**
    * **Descripción:** la dirección ID del dispositivo esclavo Modbus en el bus RS485, típicamente un valor entre 1 y 247.
* **Dirección registro:**
    * **Descripción:** la dirección del registro concreto a leer dentro del dispositivo esclavo.
* **Function code:**
    * **Descripción:** el código de función Modbus que se usará para la lectura. Los valores posibles son 1 (Read Coils), 2 (Read Discrete Inputs), 3 (Read Holding Registers), o 4 (Read Input Registers).
* **Registro IEEE 754:**
    * **Descripción:** campo de tipo casilla. Debe activarse si el valor a leer ocupa dos registros consecutivos y está codificado en formato de coma flotante IEEE 754 de 32 bits.
* **Número de decimales:**
    * **Descripción:** aplica un factor de división a los valores numéricos leídos para posicionar el punto decimal. El valor leído se divide entre 10 elevado a este número.
    * **Ejemplo:** si el dispositivo devuelve 2530 y se configuran 2 decimales, el valor final será 25.30 (porque 2530 / 10² = 25.30).
* **Offset:**
    * **Descripción:** un valor numérico que se suma o resta al valor leído (ya ajustado por los decimales) para realizar un ajuste o calibración final.
* **Modo:**
    * **Descripción:** define cómo se aplica el Offset al valor.
    * **Opciones:**
        * **Directo:** el valor final se calcula como: (Valor Leído) - Offset.
        * **Inverso:** el valor final se calcula como: Offset - (Valor Leído).
* **Alarma de bajo:**
    * **Descripción:** define el umbral numérico inferior. Si el valor final medido (el estado, o los pulsos multiplicados por su valor) cae por debajo de este umbral, se registra una alarma.
* **Alarma de alto:**
    * **Descripción:** define el umbral numérico superior. Si el valor final medido supera este umbral, se registra una alarma.
* **Activar alarma de bajo:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar alarma de alto:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar condición de alarmas de bajo:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de valor bajo fuerza una **transmisión de datos inmediata** cuando el Modo de registro está configurado como "**Condicional**".
* **Activar condición de alarmas de alto:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de valor alto fuerza una **transmisión inmediata** cuando el Modo de registro está configurado como "**Condicional**".

### Sensor de Temperatura PT100

Esta sección detalla los parámetros de configuración de la entrada para sondas de temperatura PT100.

!!! note "Ver También"
    Para el esquema de conexión física y la configuración de hardware de la sonda, consultar la sección **[1. Conexión de Sensores](sensor-connections.md)** (concretamente el apartado de PT100).

#### Parámetros PT100

* **Número de hilos:**
    * **Descripción:** permite seleccionar la configuración de la sonda de temperatura PT100 según el número de hilos que utiliza.
    * **Opciones:** 2, 3 o 4 hilos.

!!! note "Nota importante"
    La configuración del número de hilos debe realizarse tanto en **software** (mediante este parámetro) como en **hardware** (soldando jumpers en la placa PCB). Ambos ajustes deben coincidir para garantizar una lectura precisa.

* **Alarma de bajo:**
    * **Descripción:** define el umbral mínimo de temperatura. Si la temperatura medida cae por debajo de este valor, se registra una alarma.
    * **Unidades:** grados Celsius (ºC).
* **Alarma de alto:**
    * **Descripción:** define el umbral máximo de temperatura. Si la temperatura medida supera este valor, se registra una alarma.
    * **Unidades:** grados Celsius (ºC).

* **Activar alarma de bajo:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar alarma de alto:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar condición de alarmas de bajo:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de valor bajo fuerza una **transmisión de datos inmediata** cuando el Modo de registro está configurado como "**Condicional**".
* **Activar condición de alarmas de alto:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de valor alto fuerza una **transmisión inmediata** cuando el Modo de registro está configurado como "**Condicional**".

### Sensor de Temperatura y Humedad Interno (SHT30)

Estos parámetros configuran las alarmas para el sensor de temperatura y humedad integrado en la propia placa del **ISURLOG**.

#### Parámetros de Temperatura

* **Alarma de bajo de temperatura:**
    * **Descripción:** define el umbral mínimo de temperatura. Si la temperatura medida por el sensor interno cae por debajo de este valor, se registra un evento de alarma.
    * **Unidades:** grados Celsius (ºC).
* **Alarma de alto de temperatura:**
    * **Descripción:** define el umbral máximo de temperatura. Si la temperatura medida supera este valor, se registra un evento de alarma.
    * **Unidades:** grados Celsius (ºC).
* **Activar alarma de bajo de temperatura:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar alarma de alto de temperatura:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar condición de alarmas de bajo de temperatura:**
    * **Descripción:** campo de tipo casilla (activado/desactivado). Si se activa, una alarma de baja temperatura contribuye a la condición general de alarma que fuerza una **transmisión inmediata** cuando el Modo de registro está configurado como "**Condicional**". Si está desactivada, el evento de alarma es solo informativo.
* **Activar condición de alarmas de alto de temperatura:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de alta temperatura fuerza una **transmisión inmediata** con el Modo de registro configurado como "**Condicional**". Si está desactivada, la alarma es solo informativa.

#### Parámetros de Humedad

* **Alarma de bajo de humedad:**
    * **Descripción:** define el umbral mínimo de humedad relativa. Si la humedad medida cae por debajo de este valor, se registra un evento de alarma.
    * **Unidades:** porcentaje de humedad relativa (%RH).
* **Alarma de alto de humedad:**
    * **Descripción:** define el umbral máximo de humedad relativa. Si la humedad medida supera este valor, se registra un evento de alarma.
    * **Unidades:** porcentaje de humedad relativa (%RH).
* **Activar alarma de bajo de humedad:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar alarma de alto de humedad:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar condición de alarmas de bajo de humedad:**
    * **Descripción:** campo de tipo casilla. Cuando se activa, una alarma de humedad baja fuerza una **transmisión inmediata** con el Modo de registro configurado como "**Condicional**".
* **Activar condición de alarmas de alto de humedad:**
    * **Descripción:** campo de tipo casilla. Cuando se activa, una alarma de humedad alta fuerza una **transmisión inmediata** con el Modo de registro configurado como "**Condicional**".

### Sensor de Temperatura y Humedad Externo (BME280)

Estos parámetros configuran las alarmas para el sensor de temperatura y humedad externo conectado por I2C al **ISURLOG**.

#### Parámetros de Temperatura

* **Alarma de bajo de temperatura:**
    * **Descripción:** define el umbral mínimo de temperatura. Si la temperatura medida por el sensor interno cae por debajo de este valor, se registra un evento de alarma.
    * **Unidades:** grados Celsius (ºC).
* **Alarma de alto de temperatura:**
    * **Descripción:** define el umbral máximo de temperatura. Si la temperatura medida supera este valor, se registra un evento de alarma.
    * **Unidades:** grados Celsius (ºC).
* **Activar alarma de bajo de temperatura:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar alarma de alto de temperatura:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar condición de alarmas de bajo de temperatura:**
    * **Descripción:** campo de tipo casilla (activado/desactivado). Si se activa, una alarma de baja temperatura contribuye a la condición general de alarma que fuerza una **transmisión inmediata** cuando el Modo de registro está configurado como "**Condicional**". Si está desactivada, el evento de alarma es solo informativo.
* **Activar condición de alarmas de alto de temperatura:**
    * **Descripción:** campo de tipo casilla. Si se activa, una alarma de alta temperatura fuerza una **transmisión inmediata** con el Modo de registro configurado como "**Condicional**". Si está desactivada, la alarma es solo informativa.

#### Parámetros de Humedad

* **Alarma de bajo de humedad:**
    * **Descripción:** define el umbral mínimo de humedad relativa. Si la humedad medida cae por debajo de este valor, se registra un evento de alarma.
    * **Unidades:** porcentaje de humedad relativa (%RH).
* **Alarma de alto de humedad:**
    * **Descripción:** define el umbral máximo de humedad relativa. Si la humedad medida supera este valor, se registra un evento de alarma.
    * **Unidades:** porcentaje de humedad relativa (%RH).
* **Activar alarma de bajo de humedad:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar alarma de alto de humedad:**
    * **Descripción:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Activar condición de alarmas de bajo de humedad:**
    * **Descripción:** campo de tipo casilla. Cuando se activa, una alarma de humedad baja fuerza una **transmisión inmediata** con el Modo de registro configurado como "**Condicional**".
* **Activar condición de alarmas de alto de humedad:**
    * **Descripción:** campo de tipo casilla. Cuando se activa, una alarma de humedad alta fuerza una **transmisión inmediata** con el Modo de registro configurado como "**Condicional**".

### Acelerómetro Interno (LIS2DH12)

!!! note "Nota de hardware/firmware"
    Disponible solo en **ISURLOG v3.0 y posteriores**, con firmware **1.1.6 o posterior**.

Esta sección configura umbrales de alarma independientes para cada uno de los tres ejes de aceleración (X, Y, Z) medidos por el acelerómetro integrado **LIS2DH12**.

Los mismos cuatro parámetros se repiten por eje (**X**, **Y**, **Z**):

* **Alarma de bajo eje X/Y/Z:** define el umbral inferior de aceleración (en g) para ese eje. Si el valor medido cae por debajo de este umbral, se registra una alarma.
* **Activar alarma de bajo eje X/Y/Z:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".
* **Alarma de alto eje X/Y/Z:** define el umbral superior de aceleración (en g) para ese eje. Si el valor medido supera este umbral, se registra una alarma.
* **Activar alarma de alto eje X/Y/Z:** campo de tipo casilla. Si se activa, el sistema envía una notificación de alarma a través de las opciones de mensajería configuradas (SMS, Telegram, Email), además de registrar la alarma en la plataforma. Esto es independiente de la transmisión por Modo de registro "Condicional".

!!! note "🚧 Próximamente"
    El firmware ya soporta forzar una transmisión inmediata a partir de una alarma de eje cuando el Modo de registro está en "Condicional" (el mismo comportamiento de **Activar Condición de Alarma** disponible para el resto de sensores), pero esta opción **todavía no está expuesta en IsurDASH** para los ejes del acelerómetro. Estará disponible en una futura actualización de la plataforma.
