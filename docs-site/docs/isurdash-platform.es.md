# 6. Plataforma IsurDASH

IsurDASH es la plataforma web centralizada desde la que se gestiona toda la flota de dataloggers **ISURLOG**. Está diseñada para ofrecer una interfaz intuitiva y potente que permite a los usuarios no solo visualizar los datos recogidos, sino también configurar y controlar los dispositivos de forma remota.

Todos los datos enviados por el **ISURLOG** se reciben en los servidores seguros de Isurki, donde se almacenan indefinidamente, garantizando que el histórico de mediciones nunca se pierda.

Para usuarios avanzados, se ofrece **[acceso por API](data-access-overview.md)**, que permite integrar los datos del **ISURLOG** en aplicaciones de terceros o sistemas SCADA. Además, para organizaciones que requieran un control total sobre sus datos, la plataforma IsurDASH puede instalarse en los propios servidores del cliente. Para esta opción de instalación a medida, contactar con Isurki.

## Barra de Herramientas Superior

En la parte superior de **todas** las páginas de IsurDASH hay presente una barra de herramientas — no solo en el Dashboard:

![Barra de herramientas superior de IsurDASH](images/7-top-toolbar.png){width="1000"}

*La barra de herramientas superior, presente en todas las páginas de IsurDASH.*

* **Filtros de tiempo:** restringe los datos mostrados a una ventana temporal — presets rápidos (p. ej. última 1 hora, últimas 2 horas) o un rango de fechas personalizado.
* **Filtros de Tags:** restringe los datos mostrados a dispositivos que tengan asignadas ciertas [Tags](isurdash-tags.md).
* **Interruptor de modo claro/oscuro:** alterna el tema visual; se guarda por usuario.
* **Campana de notificaciones:** todas las notificaciones (alarmas, batería baja, etc.) de toda la flota.
* **Botón de usuario:** muestra tu nombre de usuario; abre un menú para editar tu perfil, configurar notificaciones, gestionar claves de acceso, y cerrar sesión. *(Se detalla en la sección 6.9, próximamente.)*

Ambos filtros se aplican de forma **global**: una vez configurados, afectan a lo que se ve en [6.2. Dashboard](isurdash-dashboard.md) (el mapa solo muestra los Isurlogs que coinciden con las tags seleccionadas, y el recuento de alarmas se ajusta a la ventana temporal seleccionada), [6.3. Dispositivos](isurdash-devices.md) (listado de Isurlogs), [6.4. Alarmas](isurdash-alarms.md), y el Registro de eventos — todas las páginas reflejan los mismos filtros activos hasta que se cambien.

## Contenido

* **[6.1. Primeros Pasos: Acceso e Inicio de Sesión](isurdash-access-login.md)** — creación de la cuenta e inicio de sesión.
* **[6.2. Panel Principal de Control (Dashboard)](isurdash-dashboard.md)** — el mapa de la flota, el panel de alarmas y los gráficos resumen.
* **[6.3. Dispositivos](isurdash-devices.md)** — el listado de Isurlogs, añadir un dispositivo, visualización y configuración por dispositivo, y conexión local por Bluetooth.
* **[6.4. Alarmas](isurdash-alarms.md)** — analítica de alarmas de toda la flota e histórico completo de alarmas.
* **[6.5. Usuarios](isurdash-users.md)** — roles de usuario, creación de usuarios y asignación de dispositivos.
* **[6.6. Perfiles](isurdash-profiles.md)** — plantillas de configuración que se pueden aplicar a varios dispositivos a la vez.
* **[6.7. Tags](isurdash-tags.md)** — organizar y filtrar la flota mediante etiquetas personalizadas.
* **[6.8. Mantenimiento de Dispositivos](isurdash-maintenance.md)** — actualizaciones de firmware, REPL remoto, restablecimiento de fábrica y otras acciones de mantenimiento.
* **6.9. Account Settings** 🚧 — edición del perfil, preferencias de notificación y claves de acceso desde el menú de usuario. *(Próximamente.)*
