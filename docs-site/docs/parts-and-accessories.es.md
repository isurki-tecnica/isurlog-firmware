# 1. Piezas y Accesorios

Una referencia completa de todo el hardware que puede acompañar a un ISURLOG — el propio dispositivo, carcasa/montaje, antenas, baterías, alimentación externa/solar, y conectividad. Para cada elemento: qué puedes conseguir directamente **de Isurki**, y qué puedes **conseguir por tu cuenta** si prefieres comprarlo tú o ya lo tienes.

¿Prefieres montar un pedido a medida en vez de leer tablas? Ver **[2. Configura tu ISURLOG](configurator.md)** para un configurador interactivo que va sumando el total a medida que eliges.

*Todos los precios "Desde Isurki" están en EUR y no incluyen IVA.*

!!! note "Trabajo en progreso"
    🚧 Varias filas de más abajo son huecos por rellenar — faltan precios, modelos, y enlaces de proveedor reales. Nada aquí está inventado; donde no tenemos todavía una cifra confirmada, se indica explícitamente en vez de dejarla sin comprobar.

## 1.1 El Datalogger

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **ISURLOG — variante NB-IoT/LTE-M** | **€387** | *Sin alternativa — es el hardware principal* |
| **ISURLOG — variante LoRaWAN** | **€330** | *Sin alternativa — es el hardware principal* |
| **ISURLOG — solo Wi-Fi** | **€310** | *Sin alternativa — es el hardware principal* |

### Opciones de Protección Ambiental

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **Barniz de protección estándar** (50–200 µm) | *Incluido en todas las placas, de serie* | *No aplica — proceso de fábrica* |
| **Capa extra de barniz de protección** | **+€15** | Aplica tu propio barniz — por ejemplo, [Multicomp Pro MP014781, barniz de protección de silicona, 55 ml](https://es.farnell.com/multicomp-pro/mp014781/conformal-coating-silicone-55ml/dp/4538715) |
| **Encapsulado en resina** — la placa se moldea en resina transparente, dejando expuestos únicamente los conectores de sensores y alimentación | **+€80** | Aplica tu propia resina — necesitas 2 paquetes de [Electrolube UR5634RP250G, resina de poliuretano transparente, 250 g](https://es.farnell.com/electrolube/ur5634rp250g/resina-poliuretano-clara-aplicac/dp/2476085). Solo compatible con baterías **Li-SOCl2**. |

Para más detalles sobre el encapsulado en resina, [contacta con Isurki](mailto:tecnica@isurki.com).

## 1.2 Carcasa y Montaje

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **Carcasa impresa en 3D** (PETG, IP66) | **€35** | 💬 En debate |
| **Soporte de carril DIN** — directo, o mediante una pieza impresa en 3D independiente fijada a la pared | **€28** | 💬 En debate |
| **Soporte de poste** | **€18** | 💬 En debate |
| **Soporte/adaptador de baterías ER34615** — pequeña PCB que toma la alimentación de hasta 2 celdas ER34615 y la combina en una única salida que alimenta al ISURLOG. Necesario para usar [baterías Li-SOCl2](#14-baterias). | **€20** | 💬 En debate |

💬 **Todavía no hay una vía de autofabricación/DIY disponible para estas piezas (carcasa, montaje) — la dirección sigue en debate.** [Avísanos](https://github.com/isurki-tecnica/isurlog-firmware/issues/new) si te resultaría útil.

Ver [4.2 Montaje Físico](installation-commissioning.md#42-montaje-fisico) para las dimensiones estándar de los orificios de montaje, si prefieres diseñar tu propio soporte.

## 1.3 Antenas

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **Antena NB-IoT / LTE-M** *(comparte la recepción GPS, no necesita antena GPS aparte)* | *Incluida con la unidad NB-IoT/LTE-M* | [Molex 209142-0180](https://www.mouser.es/es/ProductDetail/Molex/209142-0180) — ~€3,78, o cualquier otra antena compatible con NB-IoT de 50 Ω de impedancia |
| **Antena LoRaWAN** (868 MHz) | *Incluida con la unidad LoRaWAN* | [TE Connectivity 2195835-3](https://www.digikey.es/es/products/detail/te-connectivity-amp-connectors/2195835-3/13926726) — debe ser de 868 MHz, 50 Ω, bajo ROE (VSWR). **No es la misma antena que la de NB-IoT** — banda de frecuencia distinta. |

Ambas usan un **conector U.FL** en la PCB. El Wi-Fi y el Bluetooth no necesitan antena externa — usan la integrada directamente en la PCB. Ver [3. Comunicaciones](communications.md) para los requisitos de conexión completos.

### Antenas de Montaje Externo (Mayor Ganancia / Montaje Remoto)

Si hace falta una antena externa de mayor ganancia, las antenas de arriba — que se montan directamente sobre el conector U.FL de la placa — no son la opción adecuada. Un pigtail saca la conexión hacia una antena externa, montada por cable.

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **Cable pigtail U.FL a SMA-hembra** — saca la conexión U.FL hacia un conector SMA-hembra montable en panel/mamparo. Compatible con el conector U.FL de a bordo tanto del módulo NB-IoT/LTE-M como del LoRaWAN. | **€12** | [RS Online — Cable coaxial U.FL a SMA-hembra](https://es.rs-online.com/web/p/cables-coaxiales/7619881?gb=a), o cualquier otro pigtail U.FL a SMA-hembra con impedancia de 50 Ω |
| **Antena externa NB-IoT / LTE-M** (SMA macho) | **€6** | [SR Passives GSM-ANT-SV03](https://www.tme.eu/es/details/gsm-ant-sv03/antenas-gsm/sr-passives/), o cualquier otra antena SMA compatible con NB-IoT de 50 Ω de impedancia |
| **Antena externa LoRaWAN** (SMA macho, 868 MHz) | **€10** | [RS Online — Antena de telemetría 868 MHz](https://es.rs-online.com/web/p/antenas-de-telemetria/2150982), o cualquier otra antena SMA de 868 MHz con impedancia de 50 Ω |

!!! warning "Pierde la Protección IP66"
    Montar la antena fuera de la [carcasa impresa en 3D](#12-carcasa-y-montaje) implica taladrarla para pasar el pigtail — esto rompe su protección **IP66** a menos que el paso quede correctamente sellado (por ejemplo, con un prensaestopas o un conector SMA de panel con junta).

## 1.4 Baterías

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **18650 (Li-Ion, recargable)** — de 1 a 5 celdas, hasta 17000 mAh en total | **€30** *(set de 5, recargables)* | [Samsung INR18650-35E, 3400mAh / 8A](https://www.nkon.nl/es/samsung-inr18650-35e.html) o equivalente — ~€2,59/unidad. Debe ser **formato 18650, Li-Ion, recargable**. |
| **Li-SOCl2 (no recargable)** — requiere **ISURLOG v3.3+** y el [soporte/adaptador de baterías ER34615](#12-carcasa-y-montaje) de arriba | **€40** *(set de 2)* | Cualquier batería **formato ER34615, química Li-SOCl2**. Recomendada: [EVE ER34615EHR2](https://www.tme.eu/es/details/eve-er34615ehr2/pilas/eve-battery/er34615ehr2/) |
| **CR2032 (pila de botón)** — solo respaldo del RTC, no alimentación principal | *Incluida en la PCB estándar* | Para recambios/repuestos: **EEMB CR2032**, 3V, con cable y **conector Molex 51021-02 (paso de 2mm)** — no vale cualquier CR2032, el conector debe coincidir. Ver [2.3 Batería de Respaldo del RTC](power-supply.md#23-bateria-de-respaldo-del-rtc-cr2032) para el pinout del conector. |

Ver [2. Métodos de Alimentación](power-supply.md) para la configuración de jumpers y los detalles de los portapilas.

## 1.5 Alimentación Externa / Solar (Modo Híbrido)

Para instalaciones que combinan baterías con una fuente de carga externa. La entrada MPPC acepta uno de tres rangos de tensión — ver [2.2 Configuración de Jumpers](power-supply.md#22-configuracion-de-jumpers-para-los-modos-de-alimentacion) para la configuración de jumpers necesaria.

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **Panel solar 5V** | **€34** | [Panel de ejemplo](https://www.amazon.es/dp/B09Q87WKGR?ref=fed_asin_title&th=1) — ver la advertencia de abajo antes de elegir el tuyo |
| **1.5V** — micropanel solar | — | 🚧 *Todavía sin modelo recomendado* |
| **0.3V** — TEG (generador termoeléctrico) | — | 🚧 *Todavía sin modelo recomendado* |

!!! warning "Se necesita un 5V regulado"
    Muchos paneles etiquetados como "5V" en realidad alcanzan hasta **7V en circuito abierto** (es decir, sin nada conectado, o con poca carga), lo que puede dañar la entrada del ISURLOG. Usa únicamente un panel con **regulador interno** que mantenga su salida estable y no supere nunca los **5,5V**, incluso sin carga.

## 1.6 Alimentación Externa (Red Eléctrica)

Para instalaciones alimentadas desde la red eléctrica en vez de solo con baterías — ver [2.1.2 Solo Alimentación Externa](power-supply.md#212-solo-alimentacion-externa). La alimentación entra por el puerto **USB-C**, o por los terminales de presión **PIN**. Las baterías pueden seguir instaladas junto con la alimentación externa como respaldo ante cortes — ver [2.1.3 Baterías + Alimentación Externa (Modo Híbrido)](power-supply.md#213-baterias-alimentacion-externa-modo-hibrido).

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **Alimentador de pared 5V/1A** | **€20** | [Alimentador de ejemplo](https://www.amazon.es/dp/B01J2G52O6?ref=fed_asin_title&th=1) |
| **Cable USB-A a Micro-USB** — solo necesario para alimentar por los terminales **PIN** en vez de por USB-C | **€10** | [Amazon Basics USB-A 2.0 a Micro-USB, 3 m](https://www.amazon.es/dp/B071S5NTDR?ref=fed_asin_title&th=1) — ver nota abajo |

!!! note "Este cable se cablea a los terminales PIN, no se usa como cable USB normal"
    Corta el extremo Micro-USB e identifica los dos cables de alimentación que hay dentro — los cables de datos no hacen falta. Conecta el positivo y el negativo directamente a los terminales de presión **PIN 5V MAX** del ISURLOG.

## 1.7 Conectividad

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **eSIM integrada + plan de datos** (NB-IoT/LTE-M) — 500 MB o 5 años, lo que ocurra antes. Un ISURLOG típico consume ~1,5–2 MB/mes, muy por debajo del límite. El consumo de datos se puede consultar por dispositivo en IsurDASH, en [Visualización de Datos, Ubicación y Datos SIM](isurdash-devices.md#visualizacion-de-datos-ubicacion-y-datos-sim). | **€36** | *No aplica, viene integrada* |
| **Nano-SIM externa** (NB-IoT/LTE-M) | — | Cualquier SIM de operador compatible con NB-IoT/LTE-M |
| **SIM NTN** (satélite, vía nRF9151) | — | [Monogoto](https://monogoto.io) — comprobar la [cobertura satelital NTN](https://docs.monogoto.io/getting-started/ntn-satellite-coverage) para tu región |

Ver [3.2 Flexibilidad en la Gestión de la SIM](communications.md#flexibilidad-en-la-gestion-de-la-sim) para cómo funciona el cambio entre eSIM y Nano-SIM.

## 1.8 Firmware

| Elemento | Desde Isurki | Consíguelo tú mismo |
| :--- | :--- | :--- |
| **Firmware estándar** — grabado de fábrica, se integra con IsurDASH de serie | **€0** *(incluido)* | Ver las [versiones publicadas en GitHub](https://github.com/isurki-tecnica/isurlog-firmware/releases) |
| **Graba tu propio firmware** — el firmware es de código abierto ([GitHub](https://github.com/isurki-tecnica/isurlog-firmware)), compila y graba una build a medida en su lugar | **€0** | Ver [1. Configuración del Entorno de Compilación](build-environment.md) y [3. Grabado del Firmware y Carga de la Aplicación](flashing-application-upload.md) |

## 1.9 Herramientas de Desarrollador *(de un solo uso, reutilizables entre unidades — no por despliegue)*

| Elemento | Necesario para |
| :--- | :--- |
| **Cable UART a USB TTL** | Grabar el lado del ESP32 — ver [3. Grabado del Firmware y Carga de la Aplicación](flashing-application-upload.md). |
| **[nRF9160-DK](https://www.digikey.es/es/products/detail/nordic-semiconductor-asa/NRF9160-DK/9740721)** + **[cable TAG-Connect de 6 pines](https://www.tag-connect.com/product/tc2030-ctx-nl-6-pin-no-legs-cable-with-10-pin-micro-connector-for-cortex-processors)** + **[nRF Connect for Desktop](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop)** | Actualizar el firmware del módem nRF9151 — ver [5.6 Requisitos de Hardware de Grabado](nbiot-modem-guide.md#56-requisitos-de-hardware-de-grabado-y-conexion). |

---

¿Falta algo que esperabas encontrar aquí, o tienes una recomendación de proveedor para alguna de las filas 🚧? [Abre un GitHub Issue](https://github.com/isurki-tecnica/isurlog-firmware/issues/new) — ver [7.4 Uso del Rastreador de Issues](contribution-guide.md#74-uso-del-rastreador-de-issues).
