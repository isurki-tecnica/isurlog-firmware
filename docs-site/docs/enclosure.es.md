# 2. La Caja

La caja del ISURLOG aloja el datalogger, sus baterías y el cableado en una sola caja impresa en 3D, diseñada por ISURKI e impresa en PETG. La tapa se cierra con cuatro cierres de cuarto de vuelta cautivos y lleva una ranura para una junta de cordón de silicona de Ø3 mm. Por dentro se monta un raíl WAGO para las conexiones o un portapilas para dos pilas ER34615, según el tipo de batería. Por fuera se fija a una pared, a un carril DIN o a un poste. Gírala, acércate y despiézala aquí abajo.

## 2.1 Visión general

<div class="encl">
  <div class="encl-stage">
    <div class="encl-opts">
      <span>Batería</span>
      <div class="encl-seg encl-seg-inline" role="group" aria-label="Batería">
        <button type="button" aria-pressed="true" data-variant="liion" data-note="Placa principal con portapilas integrados (celdas 18650) y raíl WAGO.">Li-ion<small>recargable</small></button>
        <button type="button" aria-pressed="false" data-variant="lisocl2" data-note="Placa principal sin portapilas integrados, más el portapilas con dos pilas ER34615.">Li-SOCl₂<small>no recargable</small></button>
      </div>
    </div>
    <div class="encl-canvas">
      <model-viewer id="encl-hero" src="/enclosure/enclosure-liion.glb" alt="Modelo 3D de la caja del ISURLOG" animation-name="explode" camera-controls touch-action="pan-y" auto-rotate auto-rotate-delay="3000" rotation-per-second="12deg" camera-orbit="-35deg 68deg 105%" min-camera-orbit="auto auto 0.12m" max-camera-orbit="auto auto 2m" environment-image="neutral" shadow-intensity="0.8" shadow-softness="0.9" exposure="0.7" loading="lazy"></model-viewer>
      <div class="encl-seg" role="group" aria-label="Vista">
        <button type="button" aria-pressed="true" data-explode="0">Montada</button>
        <button type="button" aria-pressed="false" data-explode="1">Despiece</button>
      </div>
      <span class="encl-hint">Arrastra para girar · rueda o pellizco para acercar</span>
    </div>
    <div class="encl-bar">
      <span>Montada</span>
      <input type="range" class="encl-range" id="encl-range" min="0" max="1000" value="0" aria-label="Montar o desmontar la caja">
      <span>Despiece</span>
    </div>
  </div>
  <p class="encl-note" id="encl-note">Placa principal con portapilas integrados (celdas 18650) y raíl WAGO.</p>
  <div class="encl-colors">
    <span class="encl-colors-label">Prueba tus colores</span>
    <div class="encl-swatches" role="group" aria-label="Caja y tapa"><small>Caja y tapa</small><button type="button" class="encl-sw" data-role="body" data-color="#EDE6CC" style="--c:#EDE6CC" aria-label="Marfil" aria-pressed="true"></button><button type="button" class="encl-sw" data-role="body" data-color="#F2F2F0" style="--c:#F2F2F0" aria-label="Blanco" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="body" data-color="#9AA0A6" style="--c:#9AA0A6" aria-label="Gris" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="body" data-color="#E8782A" style="--c:#E8782A" aria-label="Naranja" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="body" data-color="#2E6DB4" style="--c:#2E6DB4" aria-label="Azul" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="body" data-color="#2B2B2E" style="--c:#2B2B2E" aria-label="Negro" aria-pressed="false"></button></div>
    <div class="encl-swatches" role="group" aria-label="Cierres, destornillador y accesorios interiores"><small>Cierres, destornillador y accesorios interiores</small><button type="button" class="encl-sw" data-role="accent" data-color="#00A838" style="--c:#00A838" aria-label="Verde" aria-pressed="true"></button><button type="button" class="encl-sw" data-role="accent" data-color="#F28C28" style="--c:#F28C28" aria-label="Naranja" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="accent" data-color="#2E6DB4" style="--c:#2E6DB4" aria-label="Azul" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="accent" data-color="#C8372D" style="--c:#C8372D" aria-label="Rojo" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="accent" data-color="#E8C21A" style="--c:#E8C21A" aria-label="Amarillo" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="accent" data-color="#F2F2F0" style="--c:#F2F2F0" aria-label="Blanco" aria-pressed="false"></button></div>
  </div>
  <div class="encl-legend">
    <span><i id="lg-body" style="background:#EDE6CC"></i>Caja, tapa y tornillo de la contratapa</span>
    <span><i id="lg-accent" style="background:#00A838"></i>Cierres, destornillador, contratapa y accesorios interiores</span>
    <span><i style="background:#0F522B"></i>Placa principal</span>
    <span><i style="background:#2F6FB8"></i>Baterías</span>
    <span><i style="background:#212124"></i>Soportes de montaje</span>
  </div>
</div>

## 2.2 Las piezas

Elige una pieza para inspeccionarla. Todas se pueden girar y ampliar.

<div class="encl">
  <div class="encl-stage is-short">
    <model-viewer id="encl-part" src="/enclosure/parts/box.glb" alt="Modelo 3D de la pieza seleccionada de la caja" camera-controls touch-action="pan-y" auto-rotate rotation-per-second="14deg" camera-orbit="-35deg 68deg auto" environment-image="neutral" shadow-intensity="0.8" shadow-softness="0.9" exposure="0.7" loading="lazy"></model-viewer>
    <span class="encl-hint">Arrastra para girar · rueda o pellizco para acercar</span>
  </div>
  <div class="encl-parts" role="group" aria-label="Piezas">
    <button type="button" class="encl-part" aria-pressed="true" data-viewer="encl-part" data-src="/enclosure/parts/box.glb" data-panel="p-box">Caja<small>× 1</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/lid.glb" data-panel="p-lid">Tapa y cierres<small>× 1 + 4</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/cover.glb" data-panel="p-cover">Contratapa<small>× 1 + tornillo</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/key.glb" data-panel="p-key">Destornillador<small>× 1</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/wago.glb" data-panel="p-wago">Raíl WAGO<small>opcional</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/battery.glb" data-panel="p-battery">Portapilas<small>opcional</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/din.glb" data-panel="p-din">Soporte DIN<small>opcional</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/pole.glb" data-panel="p-pole">Soporte de poste<small>opcional</small></button>
  </div>

  <div class="encl-info" id="p-box">
    <h3>Caja</h3>
    <p>El cuerpo principal. Lleva los anclajes en L que sujetan los accesorios interiores, las torretas para la PCB, el anillo en «C» del frontal donde se guarda el destornillador y cinco agujeros M12 para prensaestopas en la pared trasera (cuatro en la fila superior y uno en la inferior).</p>
    <dl><dt>Cantidad</dt><dd>1</dd><dt>Material</dt><dd>PETG</dd></dl>
  </div>
  <div class="encl-info" id="p-lid" hidden>
    <h3>Tapa y cierres</h3>
    <p>La tapa tiene la ranura de la junta, un alojamiento para el imán, un marco para el desecante y un rebaje para la etiqueta. Los cuatro cierres de cuarto de vuelta se imprimen ya montados (<em>print in place</em>) y quedan cautivos en la tapa, así que no se pueden perder, por ejemplo dentro de una arqueta.</p>
    <dl><dt>Cantidad</dt><dd>1 tapa + 4 cierres</dd><dt>Material</dt><dd>PETG</dd><dt>Junta</dt><dd>Cordón de silicona de Ø3 mm (no se imprime)</dd></dl>
  </div>
  <div class="encl-info" id="p-cover" hidden>
    <h3>Contratapa</h3>
    <p>Va bajo la tapa y se sujeta al buje central de la tapa con un tornillo de cuarto de vuelta.</p>
    <dl><dt>Cantidad</dt><dd>1 contratapa + 1 tornillo</dd></dl>
  </div>
  <div class="encl-info" id="p-key" hidden>
    <h3>Destornillador</h3>
    <p>Gira los cierres de cuarto de vuelta. Se guarda encajado en el anillo en «C» del frontal de la caja, así que viaja siempre con ella.</p>
    <dl><dt>Cantidad</dt><dd>1</dd></dl>
  </div>
  <div class="encl-info" id="p-wago" hidden>
    <h3>Raíl WAGO</h3>
    <p>Un raíl para conectores WAGO 221. Se encaja en los anclajes en L de la caja. Usa los mismos agujeros que el portapilas, así que se monta uno u otro.</p>
    <dl><dt>Cantidad</dt><dd>1 (alternativa al portapilas)</dd></dl>
  </div>
  <div class="encl-info" id="p-battery" hidden>
    <h3>Portapilas (2 × ER34615)</h3>
    <p>Una base y una abrazadera con las dos cunas: las patas de la abrazadera pasan por las ranuras de la base y se enganchan encima. Usa los mismos agujeros que el raíl WAGO, así que se monta uno u otro.</p>
    <dl><dt>Cantidad</dt><dd>1 base + 1 abrazadera (alternativa al raíl WAGO)</dd></dl>
  </div>
  <div class="encl-info" id="p-din" hidden>
    <h3>Soporte para carril DIN</h3>
    <p>Una placa con un pestillo de muelle, impresos en una sola pieza (<em>print in place</em>). Se fija a la base de la caja con tornillos y tuercas M6 de acero inoxidable; las tuercas van en cajeras hexagonales del soporte.</p>
    <dl><dt>Cantidad</dt><dd>1</dd></dl>
  </div>
  <div class="encl-info" id="p-pole" hidden>
    <h3>Soporte de poste</h3>
    <p>Se fija a la base de la caja con tornillos y tuercas M6 de acero inoxidable. Se imprimen dos soportes por caja, más cuatro cilindros separadores (dos por soporte). Los cilindros tienen dos posiciones de taladro, la interior para postes finos. El modelo muestra un soporte y un cilindro.</p>
    <dl><dt>Cantidad</dt><dd>2 soportes + 4 cilindros</dd></dl>
  </div>
</div>

## 2.3 Montaje y uso

<div class="encl">
  <div class="encl-videos">
    <figure><a class="glightbox" href="/enclosure/video/01-overview.mp4" data-type="video" data-title="Visión general" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/01-overview.mp4" type="video/mp4"></video></a><figcaption><b>Visión general</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/02-open-close.mp4" data-type="video" data-title="Abrir y cerrar" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/02-open-close.mp4" type="video/mp4"></video></a><figcaption><b>Abrir y cerrar</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/03-cover.mp4" data-type="video" data-title="Contratapa" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/03-cover.mp4" type="video/mp4"></video></a><figcaption><b>Contratapa</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/04-wago.mp4" data-type="video" data-title="Raíl WAGO" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/04-wago.mp4" type="video/mp4"></video></a><figcaption><b>Raíl WAGO</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/05-battery.mp4" data-type="video" data-title="Portapilas" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/05-battery.mp4" type="video/mp4"></video></a><figcaption><b>Portapilas</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/06-din.mp4" data-type="video" data-title="Soporte para carril DIN" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/06-din.mp4" type="video/mp4"></video></a><figcaption><b>Soporte para carril DIN</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/07-pole.mp4" data-type="video" data-title="Soporte de poste" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/07-pole.mp4" type="video/mp4"></video></a><figcaption><b>Soporte de poste</b></figcaption></figure>
  </div>
</div>

Haz clic en un vídeo para ampliarlo.

## 2.4 Por qué una caja impresa

Una caja impresa no es una solución de compromiso. Permite cosas que son difíciles con una caja de inyección, y pone el diseño en tus manos.

### 2.4.1 Hazla tuya

<div class="grid cards" markdown>

- **Tus colores y tu logotipo.** Imprime la caja, los cierres y los soportes del color de filamento que quieras: los de tu marca o uno distinto para cada tipo de instalación. La tapa ya tiene un rebaje para la etiqueta y, con los archivos STL, puedes añadir tu logotipo o un número de identificación con tu laminador o con cualquier herramienta de modelado 3D. Prueba los colores en el modelo de [2.1](#21-vision-general).
- **Tus propias piezas.** El raíl WAGO y el portapilas están construidos sobre el mismo bastidor y usan los mismos anclajes de la caja, así que un accesorio interior tuyo también puede usarlos.
- **Tus propias aberturas.** La caja ya trae cinco agujeros M12 para prensaestopas en la pared trasera (cuatro en la fila superior y uno en la inferior). Si necesitas más, o de otros tamaños, puedes añadir los tuyos con tu laminador o con cualquier herramienta de modelado 3D. Toda abertura tiene que sellarse, con un prensaestopas o con un tapón ciego, también las que no uses.
- **Tu propio material.** De base se imprime en PETG, pero puedes experimentar: ASA, o filamentos reforzados con fibra de vidrio o de carbono, si tu entorno de instalación es más exigente. Los filamentos reforzados son abrasivos y requieren una boquilla endurecida. Conviene volver a comprobar la holgura del *print in place* con cualquier material nuevo. Los filamentos que conducen la electricidad, como algunos con fibra de carbono o con carga metálica, pueden debilitar la señal de las antenas que van dentro de la caja. Comprueba la calidad de la señal después de cambiar de material.
- **Mods y remixes.** Puedes modificar las piezas para tu uso. Si compartes una modificación, cita a ISURKI, indica qué has cambiado y usa la misma licencia ([2.5.3](#253-licencia)).

</div>

### 2.4.2 Fácil de mantener

<div class="grid cards" markdown>

- **Reparable.** Una pieza rota es un trabajo de impresión, no un pedido de recambios. La reimprimes y la cambias.
- **Cierres que no se pierden.** Los cuatro cierres de cuarto de vuelta se imprimen ya montados y quedan cautivos en la tapa.
- **Modular.** Pared, carril DIN o poste por fuera; raíl WAGO o portapilas por dentro. La misma caja en todos los casos.

</div>

## 2.5 Imprímela tú

Los archivos (STL y proyectos de Bambu Studio listos para imprimir) están publicados en [MakerWorld](https://makerworld.com/es/models/3392577-isurlog-enclosure-iot-datalogger-ip66-box){ target="_blank" rel="noopener" } bajo la licencia descrita en [2.5.3](#253-licencia).

### 2.5.1 Proyectos de impresión

Los ajustes de impresión van dentro de proyectos de Bambu Studio, así que no hay una lista de ajustes que copiar. Elige el que corresponda a dónde va a estar la caja:

| Dónde va a estar | Proyecto | Descarga |
| :--- | :--- | :--- |
| **A resguardo**, por ejemplo dentro de un edificio | **Interior** | [MakerWorld](https://makerworld.com/es/models/3392577-isurlog-enclosure-iot-datalogger-ip66-box){ target="_blank" rel="noopener" } |
| **Exterior o clima adverso** (agua, sol) | **Exterior**. La caja, la tapa y los cierres que se imprimen con ella son las piezas que evitan que entren agua y polvo, así que este proyecto las imprime con un perfil más exigente | [MakerWorld](https://makerworld.com/es/models/3392577-isurlog-enclosure-iot-datalogger-ip66-box){ target="_blank" rel="noopener" } |

Los proyectos están preparados para una Bambu Lab P2S con boquilla de 0,4 mm y PETG de Sunlu, con una placa por pieza: caja, tapa con cierres, contratapa, tornillo de la contratapa, destornillador, raíl WAGO, portapilas, soporte DIN y soporte de poste. Con otra impresora u otro filamento, abre el proyecto en Bambu Studio, elige la tuya, vuelve a laminar y revisa cada placa antes de imprimir.

### 2.5.2 Antes de imprimir

* **Material que no se imprime.**
    * Junta de cordón de silicona de Ø3 mm.
    * Tornillos M6 × 15 mm y tuercas de acero inoxidable para los soportes, 4 por soporte.
    * Un imán de Ø18 × 4 mm para el alojamiento de la tapa.
* **Print in place.** Los cierres y el pestillo del soporte DIN se imprimen ya montados, con una holgura de 0,2 mm. Tu impresora tiene que respetar esa holgura sin soldar las piezas entre sí.
* **Material.** PETG; los proyectos están preparados para [PETG de Sunlu](https://i.refs.cc/uja9Haai){ target="_blank" rel="sponsored nofollow noopener" }. Son posibles otros materiales (ver [2.4.1](#241-hazla-tuya)); la misma marca también fabrica PETG-CF y ASA. Los ajustes de impresión ya vienen en los proyectos de [2.5.1](#251-proyectos-de-impresion). *(Enlace de referido: comprar a través de él apoya el proyecto.)*
* **Garantía.** Si montas el ISURLOG en una caja que no ha suministrado ISURKI, la garantía de la electrónica sigue en vigor. Solo quedan fuera las averías causadas por esa caja, por ejemplo si entra agua o polvo y estropea la placa.

### 2.5.3 Licencia

Los archivos tienen licencia [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es). Además, ISURKI permite, sin coste:

* imprimir las piezas para dispositivos ISURLOG que poseas u operes, para uso personal o empresarial;
* que profesionales que dan servicio a dispositivos ISURLOG de sus clientes impriman y monten las piezas y cobren su trabajo, pero no las piezas impresas como producto por separado;
* modificar las piezas para esos usos. Si compartes una modificación, cita a ISURKI, indica qué has cambiado y usa la misma licencia.

Vender piezas impresas, cajas o kits, o vender los archivos, requiere una licencia comercial: escribe a [tecnica@isurki.com](mailto:tecnica@isurki.com). Los nombres y logotipos ISURKI e ISURLOG no están cubiertos por la licencia.

<link rel="stylesheet" href="/enclosure/enclosure.css">
<script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@4.3.1/dist/model-viewer.min.js"></script>
<script src="/enclosure/viewer.js" defer></script>
