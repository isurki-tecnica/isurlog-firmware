# 5. LoRaWAN con tu Propio Servidor ChirpStack

La versión LoRaWAN del ISURLOG funciona con un servidor de red LoRaWAN estándar: se une con OTAA, usa la banda de 868 MHz y trabaja como dispositivo de Clase A (ver [Ficha Técnica](technical-specifications.md)). Así puedes usar tus propios gateways y tu propio servidor, y mantener tu red LoRaWAN abierta y bajo tu control.

Esta página explica cómo hacerlo con **ChirpStack**, un servidor de red LoRaWAN de código abierto.

## 5.1 Qué Necesitas

* Un **ISURLOG con módulo LoRaWAN** (868 MHz).
* Un **gateway LoRaWAN** para la banda EU868, conectado a tu servidor ChirpStack.
* **ChirpStack v4**. Para instalar el servidor y el gateway bridge, sigue la [documentación oficial de ChirpStack](https://www.chirpstack.io/docs/).

## 5.2 Perfil de Dispositivo

Crea en ChirpStack un perfil de dispositivo para el ISURLOG:

* **Región:** EU868.
* **Activación:** OTAA.
* **Clase:** A o B se recomiendan para dispositivos con batería. La clase A es la más eficiente y da la máxima autonomía; la clase B no es lo óptimo para la máxima autonomía y ISURKI no la ha probado. La clase C solo se recomienda donde el ISURLOG tiene alimentación externa, ya que mantiene la radio escuchando todo el tiempo.
* **ADR:** activado, para que el dispositivo no transmita con más potencia o menor velocidad de la que el enlace necesita.

En la página de [Resolución de Problemas](troubleshooting.md) encontrarás las razones (apartado sobre la clase del dispositivo y el ADR en LoRaWAN).

## 5.3 Decodificador de Payload

El ISURLOG envía sus lecturas en un formato binario compacto (ver [3.4 Decodificación del Payload](realtime-data-mqtt.md)). ChirpStack lo convierte en valores legibles con un decodificador.

1. Descarga el decodificador: [`IsurlogLPP_Decoder.js`](https://github.com/isurki-tecnica/isurlog-firmware/blob/main/data_integration/chirpstack/IsurlogLPP_Decoder.js).
2. En ChirpStack, abre el **perfil de dispositivo** de tus ISURLOG, ve a la pestaña **Codec** y elige **JavaScript functions**.
3. Pega el contenido del archivo y guarda.

A partir de ahí, cada evento de uplink incluye los valores decodificados en la clave `object`:

```json
"object": {
  "AnalogInput0": -0.99,
  "DigitalInput0": 0,
  "HumiditySensor0": 67.5,
  "TemperatureSensor0": 24.7,
  "UnixTime0": 1757953501,
  "VoltageInput0": 4071,
  "extracted_payload_timestamp": 1757953501
}
```

* **Nombres de campo:** son el tipo de lectura seguido de su canal, y coinciden con los nombres que IsurDASH guarda en InfluxDB (ver [2.4 Esquema de Datos](historical-data-influxdb.md)). Por ejemplo, una lectura del acelerómetro produce `AccelerometerX0`, `AccelerometerY0` y `AccelerometerZ0`.
* **Hora de la lectura:** `UnixTime0` es el momento en que el ISURLOG tomó la lectura, en segundos desde 1970 (UTC). `extracted_payload_timestamp` lo repite.
* **Datos desconocidos:** si un payload contiene un tipo de dato que el decodificador no conoce, conserva lo decodificado hasta ese punto y añade al resultado una lista `warnings`, y un campo `error` en el `object`.

## 5.4 Dar de Alta el Dispositivo

Crea una aplicación en ChirpStack y añade cada ISURLOG como dispositivo con sus credenciales LoRaWAN. Usa el **DEV EUI**, el **APP EUI** y la **APP KEY** configurados en el dispositivo (ver los [parámetros LoRaWAN](reference-parameters.md#lorawan)), y asigna el perfil de dispositivo del paso anterior.

Al encender el ISURLOG, se une a la red y empieza a enviar.

## 5.5 Obtener los Datos

ChirpStack publica cada uplink en su integración MQTT, en el topic `application/{application-id}/device/{device_eui}/event/up`. El formato se describe en [3.3.1 Dispositivos LoRaWAN (vía ChirpStack)](realtime-data-mqtt.md).

## 5.6 Conectar tu Servidor a IsurDASH

Tu servidor ChirpStack se puede conectar a **IsurDASH**, nuestra plataforma gratuita para visualizar y configurar dataloggers. Mantienes tu propia red y tus propios gateways, y además dispones de los paneles, las alarmas y la configuración remota de IsurDASH (ver [6. Plataforma IsurDASH](isurdash-platform.md)).

Esta conexión la configura ISURKI. [Contacta con nosotros](mailto:tecnica@isurki.com?subject=ISURLOG%20LoRaWAN%20-%20Conectar%20mi%20servidor%20ChirpStack) y lo acordamos contigo.

## 5.7 Usar los Datos en un SCADA

Las lecturas que llegan a IsurDASH se guardan en InfluxDB, en un bucket propio, con un token privado de solo lectura. Cualquier SCADA o aplicación que pueda hacer peticiones HTTP puede leerlas con una consulta Flux. Consulta [2. Datos Históricos (InfluxDB)](historical-data-influxdb.md), incluida la implementación de referencia con una consulta que funciona, para los parámetros de conexión y los nombres de campo.

Si prefieres recibir los datos en tiempo real, suscríbete a la integración MQTT de tu servidor ChirpStack (ver [5.5](#55-obtener-los-datos)).
