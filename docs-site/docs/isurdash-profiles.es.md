*Parte de [6. Plataforma IsurDASH](isurdash-platform.md).*

# 6.6. Perfiles

Para facilitar la gestión y configuración de múltiples dataloggers **ISURLOG**, la plataforma IsurDASH incorpora una potente funcionalidad de **Perfiles**.

Un perfil es una plantilla de configuración que agrupa un conjunto de parámetros y sensores. De esta forma, si el usuario necesita desplegar varios **ISURLOG** con una configuración idéntica o muy similar (por ejemplo, para medir temperatura en distintos puntos, o para un grupo de mareógrafos), no es necesario configurar cada dispositivo individualmente. Se puede crear un único perfil y aplicarlo a varios **ISURLOG** en una sola acción.

Además, un perfil puede usarse como configuración base. Es posible aplicar un perfil a un dispositivo y, después, acceder a la configuración de ese **ISURLOG** en concreto para realizar pequeños ajustes individuales.

!!! note "Nota sobre compatibilidad de firmware"
    IsurDASH muestra los parámetros configurables para la **última** versión de firmware del ISURLOG. Al aplicar un perfil a un datalogger concreto, algunos de esos parámetros pueden no estar soportados por la versión de firmware real de ese dispositivo — en ese caso, el parámetro no soportado simplemente se **descarta** para ese dispositivo, mientras que el resto del perfil se aplica con normalidad.

## 6.6.1. Listado de Perfiles

Al acceder al menú "**Perfiles**", se presenta un listado de todas las plantillas de configuración creadas. La tabla muestra la siguiente información:

| Columna | Descripción |
| :--- | :--- |
| **Nombre de perfil** | El nombre identificativo de la plantilla. |
| **Modo de registro** | El modo de registro del dispositivo para este perfil (p. ej. "Fijo"). |
| **Número de sensores del perfil** | Cuántos sensores están definidos dentro de esa plantilla. |
| **Grupo de usuario** | El grupo al que pertenece el perfil. |

![Listado de Perfiles en IsurDASH](images/7-profiles-list.png){width="1000"}

*El listado de Perfiles.*

## 6.6.2. Crear un Nuevo Perfil

Para crear una nueva plantilla de configuración, el usuario (con rol **Ingeniero**) debe seguir estos pasos:

1.  **Iniciar la creación:** pulsar el botón azul con el símbolo de añadir (**+**), situado en la esquina superior derecha.
2.  **Rellenar el formulario:** completar el formulario con los parámetros generales que definirán el comportamiento base del perfil:
    * **Grupo de usuario**
    * **Nombre de perfil**
    * **Tiempo de latencia**
    * **Sincronización RTC**
    * **Modo de registro**
    * **Acumulador de registros**

Al guardar, se creará un perfil base que, inicialmente, **no contiene ninguna configuración de sensores**.

## 6.6.3. Gestionar y Aplicar un Perfil

Al pulsar sobre un perfil ya creado en el listado, el usuario accede a su pantalla de gestión detallada — organizada igual que la pestaña de Configuración de un dispositivo, con **Configuración general** y **Sensores** en un submenú lateral. Desde aquí se pueden realizar dos acciones principales:

1.  **Configurar el propio perfil:** editar sus parámetros generales (latencia, tensión de alimentación de sensores, modo de registro, tamaño de payload, acumulador de registros, sincronización RTC, alarma de vandalismo) y añadir los sensores (digitales, analógicos, entradas Modbus, etc.) que deben leer los dispositivos que usen este perfil.
2.  **"Aplicar perfil a varios dispositivos":** selecciona uno o varios **ISURLOG** de la flota para aplicar de forma masiva esta plantilla de configuración completa.

![Pantalla de gestión de perfiles en IsurDASH](images/7-profile-manage.png){width="1000"}

*Configurar un perfil y aplicarlo a varios dispositivos.*
