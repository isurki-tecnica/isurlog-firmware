# 1. Resumen de Acceso a Datos

Este documento ofrece una guía técnica completa para desarrolladores e integradores de sistemas que deseen integrar los datos de los dispositivos Isurlog en plataformas de terceros, como SCADA, herramientas de Business Intelligence (BI), o aplicaciones a medida. La plataforma Isurlog está diseñada para ser abierta y flexible, permitiendo acceder a los datos de la forma que mejor se adapte a las necesidades del cliente.

Isurlog ofrece dos métodos principales de acceso a datos, cada uno pensado para un caso de uso distinto:

## 1.1 Datos Históricos vía API de InfluxDB (Método Pull)

* **Caso de uso:** ideal para analítica, informes, y para poblar dashboards con mediciones pasadas.
* **Mecanismo:** este método permite a los clientes consultar la base de datos bajo demanda, para obtener datos de cualquier periodo de tiempo.
* **Formato de datos:** los datos que ofrece la API ya vienen **decodificados** y presentados en un formato legible.

Para los detalles completos de este método, ver **[2. Datos Históricos vía API de InfluxDB (Método Pull)](historical-data-influxdb.md)**.

## 1.2 Datos en Tiempo Real vía MQTT (Método Push)

* **Caso de uso:** perfecto para monitorización en vivo, alertas inmediatas, y aplicaciones dirigidas por eventos.
* **Mecanismo:** este método ofrece un flujo continuo de datos, enviados directamente desde el servidor de Isurlog a los sistemas del cliente en el instante en que se recibe una nueva medición.
* **Formato de datos:** este flujo consiste en el **payload en bruto del dispositivo**, que **requiere decodificación** por parte del cliente.

Para los detalles completos de este método, ver **[3. Datos en Tiempo Real vía MQTT (Método Push)](realtime-data-mqtt.md)**.
