# 1. Resolución de Problemas

Problemas habituales reportados por clientes, por qué ocurren, y cómo solucionarlos. Esta página crece con el tiempo, a medida que surgen nuevos casos — si te encuentras con algo que no está aquí listado, contacta con soporte (ver la página de [Inicio](index.md)) para que se pueda añadir.

---

## Las baterías se agotan mucho más rápido de lo esperado

Este es, con diferencia, el problema más reportado, y suele deberse a una o varias de las siguientes causas.

### 1. Firmware desactualizado (ESP32 y/o módem NB-IoT)

Las versiones de firmware más antiguas estaban significativamente menos optimizadas para el consumo de energía. Además, el **firmware antiguo del módem nRF9151 no soportaba RAI** (Release Assistance Indication) — sin él, incluso después de que el ISURLOG terminara de transmitir, la conexión celular del módem permanecía en estado **RRC Connected** unos 30 segundos adicionales antes de liberarse, consumiendo batería todo ese tiempo sin ningún beneficio.

**Solución:** Actualizar el firmware.

* **Recomendado:** actualizar el firmware del ESP32 directamente desde IsurDASH — ver **[6.8. Mantenimiento de Dispositivos](isurdash-maintenance.md)**.
* **Alternativa manual:** grabarlo tú mismo — ver **[3. Grabado del Firmware y Carga de la Aplicación](flashing-application-upload.md)**.

Usa siempre la release marcada como **"Latest"** en la [página de Releases de GitHub](https://github.com/isurki-tecnica/isurlog-firmware/releases) — las versiones **pre-release** pueden contener errores que *aumenten* el consumo de energía en vez de reducirlo.

### 2. Dejar el cargador de batería activado sin fuente de alimentación externa

El propio circuito del cargador consume una pequeña cantidad de energía solo por estar activo. En instalaciones que funcionan **solo con baterías** (sin panel solar, TEG, o cargador de 5V conectado), dejar el jumper del cargador activado desperdicia energía sin ningún beneficio — no tiene nada de qué cargar.

**Solución:** Configurar los jumpers para el máximo ahorro de energía — ver **[2. Métodos de Alimentación](power-supply.md)** para la configuración de jumpers correcta en instalaciones solo con batería (Charger desactivado).

### 3. Específico de LoRaWAN: clase de dispositivo y ADR

Para unidades ISURLOG con **LoRaWAN** en concreto, hay otros dos factores adicionales que suelen causar un consumo excesivo:

* **Clase de dispositivo incorrecta.** Configurar **Clase B o Clase C** en vez de **Clase A** cuando la aplicación en realidad no necesita downlinks de baja latencia y el dispositivo está pensado para funcionar con baterías. Las Clases B y C mantienen la radio escuchando mucho más a menudo que la Clase A, que es, con diferencia, la clase más eficiente energéticamente.
* **ADR (Adaptive Data Rate) no activado** en el network server LoRaWAN. Sin ADR, el dispositivo puede seguir transmitiendo con más potencia / menor Data Rate de la que sus condiciones de enlace reales requieren, desperdiciando energía en cada uplink.

---

## Faltan datos / huecos en los datos recibidos / menos registros de los esperados

Esto también suele deberse, en general, a un **firmware desactualizado que gestiona mal las pérdidas de conectividad**. Por ejemplo, cuando la cobertura es temporalmente mala, o el ISURLOG tiene que reconectarse a la red, las versiones de firmware más antiguas no gestionan correctamente los registros ya almacenados en la **RAM del RTC** mientras esto ocurre — y esos registros pendientes se pierden en vez de enviarse una vez recuperada la conexión.

**Solución:** Actualizar el firmware del ESP32 — igual que arriba, **recomendado** mediante IsurDASH (**[6.8. Mantenimiento de Dispositivos](isurdash-maintenance.md)**) o manualmente (**[3. Grabado del Firmware y Carga de la Aplicación](flashing-application-upload.md)**), usando siempre la release marcada como **"Latest"** en vez de una pre-release.

---

## Los cambios de configuración no parecen aplicarse

Cuando editas la configuración de un dispositivo en IsurDASH y pulsas guardar, los cambios se guardan en la **propia base de datos de IsurDASH** — pero **todavía no se envían al ISURLOG**. Esto es intencionado: permite seguir editando varias secciones de configuración antes de enviar una única transmisión al dispositivo, en vez de enviar un downlink por cada campo.

Mientras un dispositivo tiene cambios sin guardar, IsurDASH muestra un banner de aviso:

!!! warning "Banner de IsurDASH"
    ⚠️ **"Configuración no sincronizada con el dispositivo"** — con dos botones, **Ignorar** y **Sincronizar**.

Durante este estado, el widget de Configuración del dashboard del dispositivo muestra **"Sin enviar"**.

Al pulsar **Sincronizar** se pone en cola la configuración para enviarla al dispositivo — el widget pasa entonces a mostrar **"Sincronizado"**.

!!! warning "Importante"
    "Sincronizado" no significa que el dispositivo ya esté funcionando con la nueva configuración. Solo significa que la configuración se ha enviado desde el lado de IsurDASH. Para que realmente llegue y surta efecto en el ISURLOG:

1. El ISURLOG tiene que realizar un **uplink** (una transmisión de datos) — esto se aplica igual a dispositivos NB-IoT, LoRaWAN y Wi-Fi.
      * **Excepción — NB-IoT con eDRX:** en **dispositivos NB-IoT con eDRX activado**, la espera es mucho más corta. En vez de esperar al siguiente ciclo de transmisión completo, la configuración puede llegar al dispositivo dentro del **temporizador eDRX** configurado — típicamente **40,96 segundos** en las versiones de firmware estándar.
2. Justo después del uplink, el dispositivo recibe el **downlink** con la nueva configuración, la guarda, y vuelve a dormir.
3. Solo en el **siguiente ciclo de despertar** el dispositivo lee esa configuración guardada y empieza a operar realmente con ella.

Por lo tanto, hay un retraso inherente de hasta **dos ciclos de transmisión completos** entre pulsar "Sincronizar" y que el cambio surta efecto realmente en campo — algo a tener en cuenta, especialmente en dispositivos configurados con tiempos de latencia largos (ver **[7. Referencia de Parámetros de Configuración](reference-parameters.md)**).

---

## El sensor Modbus no responde / timeout

Cuando un sensor Modbus RTU en el bus RS485 no responde, o el ISURLOG reporta un timeout al leerlo, la causa es casi siempre una de las siguientes.

### 1. Dirección de esclavo, baudrate, o paridad no coincidentes

La **Dirección de Esclavo**, el **Baudrate**, la **Paridad**, los **Data Bits**, y los **Stop Bits** configurados en IsurDASH para esa Entrada Modbus deben coincidir exactamente con la propia configuración del sensor (normalmente ajustada mediante interruptores DIP o la herramienta de configuración propia del fabricante). Cualquier desajuste da como resultado que no haya respuesta en absoluto, no una respuesta corrupta — Modbus RTU no se degrada de forma progresiva.

**Importante — estos parámetros de comunicación son de todo el bus, no por sensor.** IsurDASH permite ajustar Baudrate/Paridad/Data Bits/Stop Bits individualmente para cada una de las 4 Entradas Modbus virtuales, pero físicamente solo hay **un** bus RS485. Todos los sensores conectados a él están escuchando eléctricamente la misma señal, así que **todos los sensores del bus deben estar configurados realmente con los mismos valores**. Configurar un baudrate distinto en la Entrada Modbus 2 que en la Entrada Modbus 0, por ejemplo, no le da a cada sensor su propia velocidad — simplemente rompe la comunicación para el sensor o sensores que no coincidan con lo que realmente está configurado en el bus.

### 2. Cableado del bus incorrecto o falta la resistencia de terminación

En redes Modbus más grandes — varios sensores en el mismo bus, y/o tiradas de cable largas — las buenas prácticas de cableado importan mucho más de lo que parece, y la mayoría de los problemas de campo se deben a esto.

* **Cablea el bus como una única cadena (daisy chain), nunca en paralelo/estrella.** Modbus RTU sobre RS485 es una topología de bus: las conexiones deben ir ISURLOG → Sensor 1 → Sensor 2 → … → Sensor N, con cada sensor cableado a los terminales del *anterior* — no todos los sensores cableados de vuelta de forma independiente a los propios terminales del ISURLOG en forma de estrella. A/B y GND se encadenan todos de la misma forma.
* **Termina ambos extremos físicos del bus con una resistencia de 120 Ω.** La propia entrada RS485 del ISURLOG ya incluye una **resistencia de terminación de 120 Ω integrada** (ver **[1. Conexión de Sensores](sensor-connections.md)**), cubriendo automáticamente el extremo del bus del lado del ISURLOG. El otro extremo — el **último sensor de la cadena** — necesita su propia resistencia de terminación de 120 Ω añadida entre A/B, ya sea integrada en el sensor (algunos tienen un interruptor DIP o jumper para ello) o añadida externamente en ese último punto de conexión. Los sensores intermedios, en medio de la cadena, **no** deben terminarse.
* La falta de terminación no siempre provoca un fallo total — a menudo se manifiesta como timeouts intermitentes que empeoran con más sensores, tiradas de cable más largas, o baudrates más altos, lo que hace fácil diagnosticarlo erróneamente como un problema del sensor o de configuración en vez de cableado.

**Solución:** Verificar que la Dirección de Esclavo, el Baudrate, la Paridad, los Data Bits, y los Stop Bits sean idénticos en todos los sensores del bus y coincidan con lo configurado en IsurDASH; cablear los sensores en cadena en vez de en paralelo; y confirmar que hay una resistencia de terminación de 120 Ω únicamente en el último sensor de la cadena (el extremo del ISURLOG ya está terminado internamente).

---

## El BLE no conecta desde la app / IsurDASH

A diferencia de NB-IoT/LoRaWAN, que el ISURLOG usa según su propio programa, **el Bluetooth está desactivado por defecto y hay que despertarlo deliberadamente** — es una decisión deliberada de ahorro de energía, no un fallo.

### 1. El BLE todavía no está anunciándose (advertising)

Para ahorrar batería, el ISURLOG no mantiene encendida su radio Bluetooth. Primero hay que activarla con el imán, como se describe en **[1.8. Sensores Internos y Diagnóstico](sensor-connections.md#18-sensores-internos-y-diagnostico)**: mantener el imán cerca del sensor de efecto Hall durante **más de 5 segundos** pone al dispositivo en **Modo de Diagnóstico por Bluetooth**.

Una vez activo, la interfaz Bluetooth permanece abierta durante **2 minutos** esperando un intento de emparejamiento. Si nada se conecta en esa ventana, se apaga automáticamente para ahorrar energía — así que la app/IsurDASH tiene que intentar la conexión dentro de esa misma ventana de 2 minutos, ni antes de activarlo ni mucho después. Una vez que ocurre un emparejamiento exitoso, ese timeout de 2 minutos deja de aplicar durante el resto de la sesión.

**Solución:** Activar el Bluetooth con el imán (>5s) justo antes de intentar conectar, y completar la conexión dentro de los siguientes 2 minutos. Si expira, simplemente reactívalo de nuevo con el imán.

### 2. El ISURLOG está ocupado con otra tarea

El imán solo se comprueba una vez, justo al arrancar o al despertar del reposo profundo — no se vuelve a comprobar mientras el dispositivo está en marcha. Si se acerca el imán mientras el ISURLOG está leyendo sensores, conectándose a la red, o transmitiendo datos, no pasa nada: el dispositivo termina esa tarea con normalidad, sin entrar en modo Bluetooth. Solo entra en modo de diagnóstico por Bluetooth si el imán está presente en el instante exacto en que el dispositivo despierta de un reposo profundo real.

**Solución:** Espera un momento y vuelve a intentarlo. En cuanto el ISURLOG termine su ciclo en curso (lectura de sensores, conexión, transmisión) y entre en reposo profundo, el siguiente acercamiento del imán sí lo detectará.

### 3. Alcance del Bluetooth

El ESP32 del ISURLOG usa la antena integrada directamente en la PCB en vez de una externa, así que el alcance del BLE es inherentemente corto — normalmente unos **5 metros**, y menos según el material de la carcasa, los obstáculos, y el entorno circundante (las carcasas/armarios metálicos en particular pueden reducirlo todavía más).

**Solución:** Acércate a pocos metros del dispositivo, con la mejor línea de visión posible, antes de intentar emparejar.
