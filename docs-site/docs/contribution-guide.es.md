# 7. Guía de Contribución

¡El firmware del **ISURLOG** es un proyecto de código abierto, y las contribuciones de la comunidad son bienvenidas! Ya sea una simple corrección de errores, la sugerencia de una nueva funcionalidad, o la optimización de las rutinas de consumo de energía, tu ayuda es muy valorada.

!!! note "¿Dónde vive realmente el código propio de ISURKI?"
    Este repositorio es un **fork completo de MicroPython** — la gran mayoría del árbol de código (`py/`, `extmod/`, la mayor parte de `ports/`, etc.) es MicroPython original (upstream), mantenido sincronizado a través del remoto `upstream`. El código propio de ISURKI — la parte a la que en la mayoría de los casos contribuirás — vive en solo dos sitios: **`app/`** (la aplicación, `main.py` + configuración) y **`ports/esp32/modules/{modules,lib}`** (los envoltorios y drivers). Ver **[2. Visión General de la Arquitectura](architecture-overview.md)** y **[2.1 Referencia de Módulos y Librerías](module-library-reference.md)** antes de empezar — ahí se explica la separación entre `lib`/`modules` y se documenta cada archivo existente, para saber dónde encaja un nuevo driver de sensor o una nueva funcionalidad.

## 7.1 Formas de Contribuir

Se aceptan contribuciones en las siguientes áreas:

* **Contribuciones de código (Pull Requests):** correcciones de errores, nuevos drivers de sensores, optimizaciones de rendimiento, o nuevas funcionalidades.
* **Documentación:** mejorar la calidad, claridad y completitud de esta Wiki o de los comentarios en el código.
* **Reportes de errores:** enviar reportes claros y detallados a través del rastreador de Issues de GitHub.
* **Peticiones de funcionalidad:** sugerencias de funcionalidad futura o de integración de hardware.
* **Hardware (Printables):** aportar accesorios, soportes o carcasas nuevos o mejorados para el datalogger.

## 7.2 Requisitos Previos para Enviar Código

Antes de enviar un **Pull Request (PR)**, asegúrate de cumplir los siguientes requisitos:

1.  **Entorno:** debes usar el entorno de desarrollo recomendado **Ubuntu/WSL**, tal como se detalla en **1. Configuración del Entorno de Compilación**.
2.  **Base de código:** tu rama de desarrollo debe partir de la rama `main` del repositorio oficial de **ISURLOG** y estar actualizada con ella.
3.  **Calidad del código:** seguir los estándares de código de Python/MicroPython (p. ej. PEP 8 donde aplique). Los mensajes de commit deben seguir el `CODECONVENTIONS.md` del proyecto (heredado del MicroPython original) — prefijar cada commit con el directorio o archivo al que afecta, p. ej. `modules/nb_iot: Fix eDRX timeout handling.`
4.  **Pruebas locales:** los cambios que afecten a código relacionado con el hardware (sensores, gestión de energía, comunicaciones) deben probarse en un dispositivo **ISURLOG** físico. Las contribuciones que no toquen el hardware en absoluto (p. ej. una corrección del códec de payload en `IsurlogLPP.py`, o una corrección de lógica pura) pueden revisarse en su lugar con pruebas a nivel de unidad — indica en tu PR cómo lo has probado, en cualquiera de los dos casos.
5.  **Licencia:** al contribuir, aceptas que tu código se licencie bajo la licencia **GPL-3.0** del proyecto (ver `LICENSE`). Los archivos nuevos deben llevar la misma cabecera de copyright usada en todo el código base:

    ```python
    # Copyright (C) 2026 ISURKI
    #
    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.
    #
    # SPDX-License-Identifier: GPL-3.0-or-later
    ```

## 7.3 El Proceso de Contribución

Sigue estos pasos para una contribución limpia y eficiente:

### 1. Hacer un Fork del Repositorio

Empieza haciendo un fork del repositorio principal `isurlog-firmware` a tu cuenta personal de GitHub.

### 2. Crear una Rama de Trabajo

Crea una rama dedicada para tu corrección o funcionalidad concreta. Esto mantiene los cambios aislados.
```bash
git checkout -b feature/tu-funcionalidad-genial

```

### 3. Implementar los Cambios
Haz commits de tus cambios con frecuencia, con mensajes descriptivos que sigan el `CODECONVENTIONS.md` (p. ej., `modules/max31865_sensor: Fix float conversion in PT100 driver.`).

### 4. Crear un Pull Request (PR)
1. Sube tu rama de trabajo a tu fork personal en GitHub.
2. Ve a la página del repositorio oficial de ISURLOG e inicia un nuevo Pull Request.
3. Descripción del PR: describe con claridad el problema resuelto o la funcionalidad añadida. Incluye detalles de cómo has probado el cambio.

## 7.4 Uso del Rastreador de Issues

Usa la pestaña de Issues de GitHub para lo siguiente:

* **Reportes de errores**: incluye pasos claros para reproducir el error, el comportamiento esperado, y el comportamiento real observado.

* **Peticiones de funcionalidad**: describe la nueva funcionalidad y por qué sería valiosa para la comunidad de ISURLOG.

## 7.5 Dónde Mirar, Según Qué Quieras Tocar

| Quieres... | Empieza aquí |
| :--- | :--- |
| Entender la estructura del código base | **[2. Visión General de la Arquitectura](architecture-overview.md)** / **[2.1 Referencia de Módulos y Librerías](module-library-reference.md)** |
| Añadir o corregir un driver de sensor | **[2.1 Referencia de Módulos y Librerías](module-library-reference.md)** |
| Cambiar una asignación de GPIO/hardware | **[4. Mapeo de GPIO (Hardware-Software)](gpio-mapping.md)** |
| Trabajar en el módem NB-IoT (nRF9160/nRF9151) | **[5. Guía Avanzada del Módem NB-IoT](nbiot-modem-guide.md)** |
| Trabajar en el módem LoRaWAN (RAK3172) | **[6. Guía Avanzada del Módem LoRaWAN](lorawan-modem-guide.md)** |
| Grabar tu build para pruebas locales | **[3. Grabado del Firmware y Carga de la Aplicación](flashing-application-upload.md)** |
