*Parte de [6. Plataforma IsurDASH](isurdash-platform.md).*

# 6.4. Alarmas

Esta sección ofrece un histórico completo y detallado de todos los eventos de alarma generados por la flota de dispositivos **ISURLOG**. A diferencia del panel de alarmas del Dashboard, que solo muestra los eventos más recientes/sin leer, aquí el usuario puede consultar, filtrar y analizar todo el histórico de alarmas. Tiene dos pestañas: **Resumen** y **Listado De Alarmas**.

## Resumen

Una vista analítica de las alarmas de toda la flota:

* Totales: **Total**, **Sin leer**, **Batería** (alarmas de batería baja), **Fuera de rango** (alarmas de valores fuera de rango), **Sin datos**, e **Isurlogs sin alarmas**.
* **Alarmas por tipo:** un gráfico desglosado por tipo de alarma (batería baja frente a fuera de rango).
* **Alarmas por día** y **Alarmas por franja horaria:** cuándo se han producido las alarmas, por día y por franja horaria.
* **Isurlogs con más alarmas:** un ranking de qué dispositivos han generado más alarmas.

![Pestaña Resumen de Alarmas en IsurDASH](images/7-alarms-resumen.png){width="1000"}

*La pestaña Resumen — analítica de alarmas de toda la flota.*

## Listado De Alarmas

Una tabla filtrable y con búsqueda que enumera cada evento de alarma individualmente:

| Columna | Descripción |
| :--- | :--- |
| **Tipo** | La naturaleza de la alarma (p. ej., "Valor fuera de rango," "Batería baja"). |
| **Isurlog** | El nombre e ID del dispositivo que generó la alarma. |
| **Detalle** | El sensor o medición que disparó la alarma (p. ej., "Humedad interna"). |
| **Valor** | El valor exacto medido que disparó la alarma. |
| **Fecha** | Cuándo registró y transmitió el ISURLOG el evento de alarma. |
| **Estado** | Si la alarma ha sido leída. |

Un cuadro de búsqueda (por Isurlog, nombre, o descripción), un filtro de tipo (**Todos los tipos** / **Valor fuera de rango** / **Batería baja**), y un filtro de estado de lectura (**Todas** / **Sin Leer** / **Leídas**) permiten acotar la lista. Las columnas son ordenables.

![Pestaña Listado De Alarmas en IsurDASH](images/7-alarms-listado.png){width="1000"}

*La pestaña Listado De Alarmas — el histórico completo y filtrable de alarmas.*
