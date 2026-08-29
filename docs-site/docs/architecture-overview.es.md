# 2. Visión General de la Arquitectura

Para el desarrollo de aplicaciones y para aprovechar al máximo las capacidades del hardware del **ISURLOG**, se ofrece una base de software de referencia desarrollada en MicroPython. Este software es de código abierto y está disponible en el repositorio de GitHub.

El objetivo principal de esta estructura de software es proporcionar las herramientas necesarias para interactuar con todos los circuitos integrados (IC) y periféricos del **ISURLOG**, además de ofrecer una plantilla de ejemplo funcional de una aplicación de datalogger típica.

## 2.1 La Estructura Modular del Software

El software del repositorio presenta una estructura modular pensada para un uso flexible y sencillo, basada en los siguientes componentes clave:

### 1. La Carpeta `/lib` (Librerías Base)

* **Drivers de bajo nivel:** contiene librerías de MicroPython para controlar directamente los distintos IC presentes en la placa del **ISURLOG** (sensores, módem de comunicación, RTC, etc.).
* **Gestión directa del hardware:** estas librerías gestionan la comunicación directa con el hardware (por ejemplo, vía I2C, SPI, UART).
* **Librerías de terceros:** puede incluir librerías de terceros desarrolladas específicamente para el **ISURLOG** o adaptadas para él.

### 2. La Carpeta `/modules` (Envoltorios de Alto Nivel)

* **Capa de abstracción:** actúa como una capa de abstracción sobre las librerías de la carpeta `/lib`.
* **Propósito:** estos módulos (o "wrappers") simplifican el uso de las funcionalidades del hardware, ofreciendo interfaces más intuitivas y reduciendo la cantidad de código de aplicación necesario.

### 3. El Archivo `main.py` (Punto de Entrada de la Aplicación)

Este es el script principal que se ejecuta en el ESP32. El `main.py` proporcionado viene preconfigurado para implementar una aplicación de datalogger completa y funcional.

Un ejemplo típico de este punto de entrada gestiona las siguientes tareas:

* Inicializar sensores y periféricos.
* Leer los datos de los sensores conectados.
* Formatear los datos.
* Establecer la conexión a la nube mediante LoRaWAN o NB-IoT.
* Enviar los datos a un servidor LoRaWAN o a un broker MQTT (en el caso de NB-IoT).
* Recibir nuevas configuraciones.
* Gestionar el consumo de energía.

## 2.2 Compatibilidad y Adaptabilidad

El software se ha diseñado pensando en la adaptabilidad:

### Configuración mediante JSON

La forma más sencilla de configurar el datalogger es estableciendo los parámetros en `dynamic_config.json`. Esto cubre la mayoría de los casos de uso habituales.

### Modificación del Código

Para lógicas de funcionamiento totalmente personalizadas o muy específicas que no puedan resolverse solo con la configuración JSON, el usuario siempre tiene la opción de modificar directamente el archivo `main.py` o incluir sus propios módulos en la carpeta `/modules`. Al ser el código abierto, el usuario tiene total libertad para adaptarlo a los requisitos exactos de cada aplicación.

## 2.3 ¿Buscas un módulo concreto?

Para un desglose archivo por archivo de cada módulo en `/modules` y cada driver en `/lib` — su propósito, API pública, dependencias, y qué claves de configuración lee cada uno — ver **[2.1 Referencia de Módulos y Librerías](module-library-reference.md)**.
