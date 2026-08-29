# 4. Instalación y Puesta en Marcha

Esta sección cubre la instalación física, las advertencias de seguridad y la secuencia final de encendido del datalogger ISURLOG.

## 4.1. Advertencias de Seguridad (Baterías de Litio)

El ISURLOG se alimenta con baterías de litio. Su manipulación, instalación y desecho deben ajustarse a la normativa europea vigente (Directiva 2006/66/CE, Reglamento (UE) 2019/1020).

!!! warning "Instrucciones Clave de Seguridad"
    * **Tipo de batería:** usar únicamente el tipo y modelo de batería especificado por el fabricante.
    * **Mezcla:** no mezclar baterías nuevas y usadas, ni combinar baterías de distinta capacidad, tipo o fabricante.
    * **Polaridad:** respetar siempre la polaridad correcta (+/-) indicada en el compartimento de baterías. Una polaridad incorrecta puede provocar cortocircuitos o sobrecalentamiento.
    * **Daños:** insertar las baterías con cuidado para no dañar la funda aislante. No perforar ni deformar las baterías.
    * **Exposición:** evitar exponer el dispositivo o las baterías a fuentes de calor superiores a 60 °C, humedad o líquidos.
    * **Almacenamiento:** si el producto no se va a usar durante un periodo prolongado, retirar las baterías.
    * **Desecho:** no desechar las baterías junto con los residuos domésticos. Depositarlas en los puntos de recogida selectiva autorizados (ISURKI es miembro de ERP, certificado n.º 4598).

## 4.2. Montaje Físico

La carcasa IP66 del ISURLOG ofrece dos métodos de fijación a pared.

### Montaje Estándar

Este método utiliza los cuatro orificios de montaje previstos en el interior de la carcasa.

* **Procedimiento:** hay que abrir la tapa frontal para acceder a los puntos de anclaje.
* **Distancia entre orificios (centro a centro):** 125 mm x 125 mm (patrón cuadrado — el ancho y el alto coinciden).

### Accesorios de Montaje Externo (Opcionales)

Dos accesorios permiten montar y desmontar el ISURLOG sin necesidad de abrir nunca la carcasa IP66, simplificando la instalación y el mantenimiento:

1. **Soporte de carril DIN** — fija el ISURLOG a un carril DIN. Hay dos variantes disponibles:
    * Montaje directo sobre un **carril DIN estándar**.
    * Montaje sobre una **pieza de plástico impresa en 3D** independiente, que se fija primero a la pared, y sobre la que después se encaja el ISURLOG.
2. **Soporte de poste** — fija el ISURLOG a un poste o mástil.

* **Enlace al modelo 3D:** 🚧 Próximamente.

## 4.3. Extracción e Inserción de Baterías

Por seguridad y para evitar daños en las baterías o en el datalogger, seguir estas instrucciones:

### Proceso de Extracción

1.  **Apagar:** apagar el ISURLOG con el interruptor **ON/OFF**. Desconectar cualquier fuente de alimentación externa (USB-C o terminales PIN) antes de apagar.
2.  **Levantar el polo negativo:** levantar primero, con cuidado, el polo negativo de la batería.
3.  **Deslizar:** deslizar la batería hacia el polo negativo.
4.  **Extraer:** la batería ya puede extraerse.

### Proceso de Inserción

1.  **Apagar:** asegurarse de que el ISURLOG esté apagado y de que cualquier alimentación externa esté desconectada.
2.  **Insertar el polo positivo:** insertar primero el polo positivo de la batería.
3.  **Empujar:** empujar la batería hacia el polo positivo.
4.  **Insertar el polo negativo:** por último, insertar el polo negativo.

## 4.4. Secuencia de Encendido

Una vez que el sistema de alimentación (baterías o fuente externa) está correctamente configurado (ver **[2. Métodos de Alimentación](power-supply.md)**) y los sensores externos están conectados, el dispositivo está listo para su activación inicial.

### Paso 1: Verificar la Conexión de la Antena

Antes de encender, es fundamental verificar que la antena de comunicación (LoRaWAN o NB-IoT) esté correctamente conectada al conector U.FL de la PCB, para garantizar una transmisión de datos fiable y evitar daños en el circuito de RF.

### Paso 2: Localizar el Interruptor

Localizar el interruptor **ON/OFF** en la PCB.

![Ubicación del interruptor ON/OFF en la PCB del ISURLOG](images/5-onoff-switch-location.png){width="400"}

*El interruptor ON/OFF.*

### Paso 3: Encender

Mover el interruptor desde la posición inicial **OFF** (izquierda) hasta la posición **ON** (derecha).

### Paso 4: Confirmación de la Activación Inicial

Unos segundos después de la activación, el **LED STATUS** del dispositivo empezará a parpadear, indicando que ha comenzado la secuencia de arranque. Consultar [5. Funcionamiento del Datalogger](datalogger-operation.md) para interpretar los patrones del LED.

---
