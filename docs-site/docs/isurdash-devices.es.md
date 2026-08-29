*Parte de [6. Plataforma IsurDASH](isurdash-platform.md).*

# 6.3. Dispositivos

Esta sección actúa como el centro de control de todos los ISURLOG registrados en la cuenta. Permite a los usuarios obtener tanto una visión general de la flota como acceder a la información detallada y a los ajustes de configuración de cada dispositivo individualmente.

## 6.3.1. Listado de Dispositivos

Al seleccionar el menú "**Isurlogs**", se presenta una tabla con todos los dataloggers de la flota, con un cuadro de búsqueda para filtrar por ID o nombre. Esta vista muestra: ID, Nombre, Tipo (NB-IoT/LoRa), Estado (En línea/Fuera de línea), Batería, y Última transmisión.

Para acceder a un **ISURLOG** concreto, el usuario debe pulsar sobre la fila correspondiente de la tabla.

![Listado de Isurlogs en IsurDASH](images/7-devices-list.png){width="1000"}

*El listado de Isurlogs.*

## 6.3.2. Añadir un Nuevo Dispositivo

Para registrar un nuevo datalogger **ISURLOG** en la plataforma, el usuario debe seguir estos pasos:

1.  **Iniciar el registro:** ir a la pantalla "**Isurlogs**" y pulsar el botón azul con el símbolo de añadir (**+**), situado en la esquina superior derecha.
2.  **Rellenar el formulario:** se abrirá un diálogo ("Añadir Nuevo Dispositivo") en el que hay que introducir dos datos clave para asociar el dispositivo a la cuenta:
    * **Identificador:** el número de serie del dispositivo. Debe introducirse en el formato **c-XXX** (p. ej., c-567).
    * **Código de seguridad:** un código de validación único que garantiza que solo el propietario del equipo pueda registrarlo. Este código ya no está impreso en la PCB — se encuentra **dentro de la carcasa del datalogger**, junto al número de serie, como un **código QR** para escanear.

![Diálogo Añadir Nuevo Dispositivo en IsurDASH](images/7-devices-add.png){width="1000"}

*El diálogo Añadir Nuevo Dispositivo.*

## 6.3.3. Visualización y Estado del Dispositivo

Al seleccionar un dispositivo, el usuario accede a su página dedicada, con el nombre e ID del dispositivo como título de página, y botones de acceso rápido para **Conectar BLE** (ver [6.3.5](#635-conexion-local-por-bluetooth)) y **REPL** (abre una consola de MicroPython en modo **Remoto** o **Puerto serie (USB)** — ver [6.8. Mantenimiento de Dispositivos](isurdash-maintenance.md) para más detalles; nótese que esto nunca está disponible por Bluetooth). La página tiene tres pestañas: **Visualización**, **Configuración** (ver [6.3.4](#634-pestana-de-configuracion)), y **Registros**.

### Panel de Estado (Vista Rápida)

En la parte superior de la pestaña Visualización, un conjunto de indicadores ofrece una vista rápida del estado actual del dispositivo:

* **Estado:** En línea/Fuera de línea — si el dispositivo se está comunicando correctamente.
* **Última conexión:** hace cuánto tiempo se conectó el dispositivo por última vez.
* **Config.:** si los últimos cambios de configuración guardados en la plataforma ya se han aplicado al ISURLOG ("Sincronizado") o están pendientes de la próxima conexión del dispositivo.
* **Batería:** nivel de batería en milivoltios (mV) y porcentaje estimado (%), además de una estimación de los días de vida de batería restantes.
* **Alarmas:** número de alarmas activas o recientes de ese dispositivo.

### Visualización de Datos, Ubicación y Datos SIM

Justo debajo del panel de estado:

* Una tabla con la **lectura más reciente** de cada uno de los sensores conectados.
* Un mapa que indica la **última ubicación conocida** del dispositivo.
* Una tarjeta de **Datos SIM** que muestra el consumo de datos frente al plan de la SIM (p. ej. "0,53 / 500 MB") y la calidad de cobertura actual — cobertura celular para dispositivos NB-IoT/LTE-M, o cobertura con el gateway para dispositivos LoRa.

![Estado, sensores, mapa y datos SIM de un dispositivo en IsurDASH](images/7-device-visualizacion.png){width="1000"}

*Estado del dispositivo, últimas lecturas de sensores, ubicación y datos SIM.*

Debajo, un área de gráficos interactivos permite analizar la evolución de los datos de los sensores y de la batería a lo largo del tiempo, con cuatro vistas: **Gráfico principal** (serie temporal por sensor), **Bubble chart**, **HeatMap de alarmas**, y **Tabla resumen**.

### Registros (Alarmas y Eventos)

La pestaña **Registros** tiene dos subsecciones:

* **Alarmas:** una lista de todos los eventos de alarma generados por ese **ISURLOG** en concreto (tipo, detalle, valor, fecha, estado leído/no leído).
* **Eventos:** un registro de actividad del propio dispositivo — cambios de configuración, sensores añadidos/eliminados, conexiones REPL, cambios manuales de batería, etc. — con un botón **"Registrar evento manual"** para anotar algo a mano (p. ej. un cambio de batería durante una visita de campo).

![Pestaña Registros de un dispositivo en IsurDASH: subsección Alarmas](images/7-device-registros-alarmas.png){width="1000"}

*La pestaña Registros — subsección Alarmas.*

## 6.3.4. Pestaña de Configuración

La pestaña **Configuración** se organiza como un submenú lateral con cinco categorías: **Configuración general**, **Comunicaciones inalámbricas**, **Sensores**, **Variables virtuales**, y **Sensores Isurnode**.

### Configuración general

Muestra los parámetros generales del ISURLOG: nombre, tipo de módem, versión de hardware/firmware, intervalos de lectura y transmisión, modo de registro, tamaño de payload, coordenadas GPS, sincronización RTC, alarma de vandalismo, Tags asignadas, y la opción de aplicar un Perfil guardado. En la parte inferior:

* **Botón "Editar":** habilita los campos para edición y poder realizar cambios.
* **Botón "Despertar Isurlog":** envía un comando para despertar al datalogger de su modo de bajo consumo y forzar un ciclo de lectura y transmisión inmediato. Solo disponible para versiones de **ISURLOG** con tecnología **NB-IoT**, gracias al eDRX (recepción discontinua extendida).

![Configuración general en IsurDASH](images/7-device-config-general.png){width="1000"}

*La pantalla de Configuración general.*

!!! note "Referencia"
    Para el significado y el efecto de cada parámetro individual, ver [7. Referencia de Parámetros de Configuración](reference-parameters.md) — esta página deliberadamente no incluye una captura de cada campo; esa referencia es la que se mantiene actualizada.

### Comunicaciones inalámbricas

Muestra los parámetros de conectividad de este ISURLOG: broker MQTT (servidor, puerto, usuario, contraseña, topic), y los ajustes específicos del módem — APN y preferencia de SIM para dispositivos NB-IoT/LTE-M, o los parámetros LoRaWAN equivalentes para dispositivos LoRa.

!!! warning "Importante"
    esta sección solo puede editarse **localmente, a través de la conexión Bluetooth** (ver [6.3.5](#635-conexion-local-por-bluetooth)) — no puede modificarse de forma remota, a diferencia del resto de la configuración.

### Sensores

Enumera todos los sensores (integrados y externos: digitales, analógicos, entradas Modbus, etc.) configurados para ese **ISURLOG** en concreto. Desde aquí se puede añadir un sensor nuevo, editar la configuración de uno existente (incluyendo sus umbrales de alarma), o eliminar uno que ya no esté en uso.

### Variables virtuales (Métricas Calculadas)

La plataforma permite crear **variables virtuales** además del listado de sensores físicos. Las variables virtuales son métricas que el ISURLOG no lee directamente; en su lugar, se obtienen aplicando una **fórmula matemática** a los datos de los sensores físicos ya configurados (digitales, analógicos, Modbus, etc.). Esto permite calcular métricas complejas, como el **caudal a partir del nivel**, o el **caudal a partir del nivel y la velocidad**, directamente en la plataforma.

### Sensores Isurnode

Enumera los sensores/salidas conectados a través de una unidad de expansión Isurnode, cuando esta está emparejada con el ISURLOG.

## 6.3.5. Conexión Local por Bluetooth

Además de la comunicación estándar por NB-IoT o LoRaWAN, el ISURLOG dispone de un modo de conexión local por **Bluetooth Low Energy (BLE)**. Esta funcionalidad resulta muy útil para tareas como la instalación, el mantenimiento o la calibración de sensores, ya que permite una interacción continua y en tiempo real con el dispositivo.

Cuando se establece una conexión Bluetooth:

* Los gráficos de la pestaña Visualización se actualizan cada pocos segundos.
* Los cambios realizados en la pestaña Configuración se aplican al instante.
* **Importante:** los datos transmitidos en este modo son solo para visualización en tiempo real y **no se registran** en el histórico de la plataforma IsurDASH.

El proceso para establecer una conexión Bluetooth local requiere una acción coordinada entre la plataforma y el dispositivo físico:

### Paso 1: Activar el Modo Bluetooth en el ISURLOG

Para que el ISURLOG sea visible y se pueda conectar, el usuario debe activarlo manualmente con un imán:

1.  El usuario debe localizar la zona del sensor magnético en la carcasa del dispositivo (ver [1. Conexión de Sensores](sensor-connections.md#18-sensores-internos-y-diagnostico) para la ubicación exacta).
2.  Hay que mantener un imán sobre esa zona de forma continua durante al menos **5 segundos**.
3.  El ISURLOG activará el Bluetooth y entrará en modo de emparejamiento. El usuario puede confirmar que el modo se ha activado correctamente observando el patrón específico del **LED STATUS** (ver [5. Funcionamiento del Datalogger: Diagnóstico en Campo](datalogger-operation.md#53-diagnostico-en-campo-led-status)).

### Paso 2: Iniciar la Conexión en IsurDASH

1.  Desde la página de "**Visualización**" del dispositivo deseado, el usuario debe pulsar el botón "**Conectar BLE**", situado en la esquina superior derecha.
2.  IsurDASH comenzará a buscar el ISURLOG con el número de serie correspondiente.
3.  Una vez encontrado, aparece el propio aviso de emparejamiento Bluetooth del navegador (p. ej. "Isurlog-c-1178"); el usuario debe pulsar "**Emparejar**" para establecer la conexión.

![Ventana emergente del navegador para el emparejamiento Bluetooth](images/7-bluetooth-pairing.jpg){width="500"}

*El propio aviso de emparejamiento Bluetooth del navegador.*

### Paso 3: Sesión en Tiempo Real y Desconexión

Una vez conectado, el indicador **Estado** cambia a "**Bluetooth**".

![Página de un dispositivo en IsurDASH mientras está conectado por Bluetooth](images/7-bluetooth-realtime-top.png){width="1000"}

*Conectado por Bluetooth — el indicador Estado cambia a "Bluetooth".*

Debajo, el área de gráficos (ahora etiquetada como **"Bluetooth Mode"**) representa los sensores conectados actualizándose cada pocos segundos, con los umbrales de alarma alto/bajo de cada sensor dibujados como líneas de referencia. El usuario puede hacer cambios en la pestaña Configuración y ver su efecto de inmediato.

![Gráfico en tiempo real en IsurDASH en Bluetooth Mode](images/7-bluetooth-realtime-bottom.png){width="1000"}

*Gráfico de sensores en tiempo real en Bluetooth Mode, actualizándose cada pocos segundos.*

Para finalizar la sesión, el usuario debe pulsar el botón "**Desconectar BLE**", que aparece en el mismo lugar que el botón de conexión. Al desconectarse, el ISURLOG apaga su radio Bluetooth y vuelve a su ciclo de funcionamiento normal programado.
