# 2. Configura tu ISURLOG

Elige tus opciones abajo — el total se actualiza a medida que avanzas. Esto solo incluye elementos disponibles directamente desde Isurki (con precio real); para las alternativas "consíguelo tú mismo", las especificaciones completas, y los enlaces de proveedor de cada elemento, ver **[1. Piezas y Accesorios](parts-and-accessories.md)**. Cuando estés listo, solicita presupuesto y confirmaremos compatibilidad y precio final.

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  .cfg-wrap{
    --bg:#eef1f0; --surface:#ffffff; --surface-2:#f6f8f7;
    --border:#d7dcda; --border-strong:#b9c1be;
    --text:#182322; --text-2:#4d5957; --text-3:#7c8886;
    --accent:#b8721e; --accent-ink:#5c3810; --accent-bg:#f7e8d4;
    --warn-bg:#f8e4e1; --warn-ink:#7a2b1c;
    --radius:10px;
    --font-ui: "IBM Plex Sans", -apple-system, "Segoe UI", sans-serif;
    --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", monospace;
  }
  [data-md-color-scheme="slate"] .cfg-wrap{
    --bg:#121615; --surface:#1b201f; --surface-2:#212726;
    --border:#333b39; --border-strong:#454f4c;
    --text:#e8ece9; --text-2:#aab5b1; --text-3:#78827f;
    --accent:#e5a355; --accent-ink:#ffe4bd; --accent-bg:#3a2a15;
    --warn-bg:#3a201a; --warn-ink:#f0b3a3;
  }
  .cfg-wrap, .cfg-wrap *{box-sizing:border-box;}
  .cfg-wrap{max-width:900px;margin:0 auto;padding:1.5rem 0 2rem;font-family:var(--font-ui);color:var(--text);}
  .cfg-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem;margin-bottom:1.1rem;}
  .cfg-card h3{font-size:.85rem;font-weight:600;text-transform:uppercase;letter-spacing:.03em;margin:0 0 .9rem;color:var(--text-2);}
  .cfg-seg{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:.5rem;}
  .cfg-seg-btn{flex:1;min-width:140px;text-align:left;padding:.6rem .8rem;border-radius:8px;border:1px solid var(--border);background:var(--surface-2);color:var(--text-2);cursor:pointer;}
  .cfg-seg-btn[data-active="true"]{background:var(--accent-bg);color:var(--accent-ink);border-color:var(--accent);}
  .cfg-seg-btn .lbl{display:block;font-size:.85rem;font-weight:600;}
  .cfg-seg-btn .pr{display:block;font-size:.78rem;font-family:var(--font-mono);margin-top:.15rem;color:var(--text-3);}
  .cfg-seg-btn[data-active="true"] .pr{color:var(--accent-ink);}
  .cfg-row{display:flex;align-items:flex-start;gap:.6rem;padding:.5rem 0;border-top:1px solid var(--border);}
  .cfg-row:first-of-type{border-top:none;}
  .cfg-row input{margin-top:.25rem;accent-color:var(--accent);width:16px;height:16px;flex:none;}
  .cfg-row label{flex:1;font-size:.85rem;cursor:pointer;}
  .cfg-row .pr{font-family:var(--font-mono);font-size:.85rem;font-weight:600;white-space:nowrap;padding-left:.5rem;}
  .cfg-row .sub{display:block;font-size:.76rem;color:var(--text-3);margin-top:.1rem;font-weight:400;}
  .cfg-warn{margin-top:.7rem;padding:.6rem .8rem;border-radius:8px;background:var(--warn-bg);color:var(--warn-ink);font-size:.8rem;display:none;}
  .cfg-warn.show{display:block;}
  .cfg-warn p{margin:0 0 .3rem;}
  .cfg-warn p:last-child{margin-bottom:0;}
  .cfg-summary{background:var(--surface);border:1px solid var(--border-strong);border-radius:var(--radius);padding:1.25rem;}
  .cfg-summary h3{font-size:.85rem;font-weight:600;text-transform:uppercase;letter-spacing:.03em;margin:0 0 .8rem;color:var(--text-2);}
  .cfg-line{display:flex;justify-content:space-between;font-size:.82rem;padding:.3rem 0;color:var(--text-2);}
  .cfg-line span:last-child{font-family:var(--font-mono);color:var(--text);}
  .cfg-empty{font-size:.8rem;color:var(--text-3);padding:.3rem 0;}
  .cfg-total{display:flex;justify-content:space-between;align-items:baseline;border-top:1px solid var(--border-strong);margin-top:.6rem;padding-top:.8rem;}
  .cfg-total .label{font-size:.85rem;font-weight:600;}
  .cfg-total .num{font-family:var(--font-mono);font-size:1.8rem;font-weight:600;color:var(--accent-ink);}
  .cfg-cta{display:block;text-align:center;margin-top:1.1rem;padding:.75rem 1rem;border-radius:8px;background:var(--accent);color:#fff;font-weight:600;text-decoration:none;font-size:.9rem;}
  .cfg-cta:hover{opacity:.92;}
  .cfg-note{font-size:.74rem;color:var(--text-3);margin-top:.6rem;line-height:1.5;}
</style>

<div class="cfg-wrap">

  <div class="cfg-card">
    <h3>Conectividad</h3>
    <div class="cfg-seg" id="cfg-variant">
      <div class="cfg-seg-btn" data-key="nbiot" data-active="true"><span class="lbl">NB-IoT / LTE-M</span><span class="pr">€387</span></div>
      <div class="cfg-seg-btn" data-key="lora" data-active="false"><span class="lbl">LoRaWAN</span><span class="pr">€330</span></div>
      <div class="cfg-seg-btn" data-key="wifi" data-active="false"><span class="lbl">Solo Wi-Fi</span><span class="pr">€310</span></div>
    </div>
    <p class="cfg-note" id="cfg-antenna-note"></p>
  </div>

  <div class="cfg-card">
    <h3>Firmware</h3>
    <div class="cfg-seg" id="cfg-firmware" style="flex-direction:column;">
      <div class="cfg-seg-btn" data-key="standard" data-active="true"><span class="lbl">Firmware estándar, conectado a IsurDASH</span><span class="pr">€0</span></div>
      <div class="cfg-seg-btn" data-key="byo" data-active="false"><span class="lbl">Graba tu propio firmware</span><span class="pr">€0</span></div>
    </div>
  </div>

  <div class="cfg-card">
    <h3>Recubrimiento Protector</h3>
    <div class="cfg-seg" id="cfg-coating" style="flex-direction:column;">
      <div class="cfg-seg-btn" data-key="standard" data-active="true"><span class="lbl">Barniz de protección estándar</span><span class="pr">Incluido</span></div>
      <div class="cfg-seg-btn" data-key="extra" data-active="false"><span class="lbl">Capa extra de barniz de protección</span><span class="pr">+€15</span></div>
      <div class="cfg-seg-btn" data-key="resin" data-active="false"><span class="lbl">Encapsulado en resina (solo Li-SOCl2)</span><span class="pr">+€80</span></div>
    </div>
  </div>

  <div class="cfg-card">
    <h3>Carcasa y Montaje</h3>
    <div class="cfg-row"><input type="checkbox" id="cfg-enclosure"><label for="cfg-enclosure">Carcasa impresa en 3D (PETG, IP66)</label><span class="pr">€35</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-dinrail"><label for="cfg-dinrail">Soporte de carril DIN</label><span class="pr">€28</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-pole"><label for="cfg-pole">Soporte de poste</label><span class="pr">€18</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-er34615holder"><label for="cfg-er34615holder">Soporte/adaptador de baterías ER34615<span class="sub">Necesario para usar baterías Li-SOCl2</span></label><span class="pr">€20</span></div>
  </div>

  <div class="cfg-card">
    <h3>Baterías</h3>
    <div class="cfg-row"><input type="checkbox" id="cfg-liion"><label for="cfg-liion">18650 Li-Ion, set de 5 (recargables)</label><span class="pr">€30</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-lisocl2"><label for="cfg-lisocl2">Li-SOCl2, set de 2 (no recargables, v3.3+)</label><span class="pr">€40</span></div>
    <div class="cfg-warn" id="cfg-warn-battery"></div>
  </div>

  <div class="cfg-card">
    <h3>Alimentación Externa / Solar</h3>
    <div class="cfg-row"><input type="checkbox" id="cfg-solar5v"><label for="cfg-solar5v">Panel solar regulado de 5V</label><span class="pr">€34</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-walladapter"><label for="cfg-walladapter">Alimentador de pared 5V/1A</label><span class="pr">€20</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-usbcable"><label for="cfg-usbcable">Cable USB-A a Micro-USB (para alimentación por terminales PIN)</label><span class="pr">€10</span></div>
  </div>

  <div class="cfg-card">
    <h3>Plan de Conectividad</h3>
    <div class="cfg-row"><input type="checkbox" id="cfg-esim"><label for="cfg-esim">eSIM integrada + plan de datos<span class="sub">500 MB o 5 años, lo que ocurra antes</span></label><span class="pr">€36</span></div>
  </div>

  <div class="cfg-summary">
    <h3>Tu Configuración</h3>
    <div id="cfg-lines"><div class="cfg-empty">Todavía no hay accesorios seleccionados — solo la unidad base.</div></div>
    <div class="cfg-total"><span class="label">Total</span><span class="num" id="cfg-total-num">€387</span></div>
    <a class="cfg-cta" id="cfg-quote-btn" href="#">Solicitar Presupuesto para Esta Configuración</a>
    <p class="cfg-note">Esto es una estimación, no un precio final — confirmaremos compatibilidad y coste exacto al solicitar presupuesto. Al pulsar el botón se abre tu cliente de correo con todo ya rellenado.</p>
  </div>

</div>

<script>
(function(){
  var VARIANTS = {
    nbiot: {label:"ISURLOG — variante NB-IoT/LTE-M", price:387, antenna:"Incluye la antena NB-IoT/LTE-M (compartida con la recepción GPS)."},
    lora:  {label:"ISURLOG — variante LoRaWAN", price:330, antenna:"Incluye la antena LoRaWAN (868 MHz)."},
    wifi:  {label:"ISURLOG — solo Wi-Fi", price:310, antenna:"Usa la antena integrada en la PCB — no necesita antena externa."}
  };
  var COATINGS = {
    standard: {label:"Barniz de protección estándar", price:0},
    extra:    {label:"Capa extra de barniz de protección", price:15},
    resin:    {label:"Encapsulado en resina", price:80}
  };
  var ADDONS = [
    {id:"cfg-enclosure", label:"Carcasa impresa en 3D (PETG, IP66)", price:35},
    {id:"cfg-dinrail", label:"Soporte de carril DIN", price:28},
    {id:"cfg-pole", label:"Soporte de poste", price:18},
    {id:"cfg-er34615holder", label:"Soporte/adaptador de baterías ER34615", price:20},
    {id:"cfg-liion", label:"Baterías 18650 Li-Ion, set de 5", price:30},
    {id:"cfg-lisocl2", label:"Baterías Li-SOCl2, set de 2", price:40},
    {id:"cfg-solar5v", label:"Panel solar regulado de 5V", price:34},
    {id:"cfg-walladapter", label:"Alimentador de pared 5V/1A", price:20},
    {id:"cfg-usbcable", label:"Cable USB-A a Micro-USB", price:10},
    {id:"cfg-esim", label:"eSIM integrada + plan de datos", price:36}
  ];
  var FIRMWARE = {
    standard: {label:"Firmware estándar, conectado a IsurDASH", price:0},
    byo:      {label:"Graba tu propio firmware", price:0}
  };

  var variant = "nbiot";
  var firmware = "standard";
  var coating = "standard";

  function fmt(n){ return "€" + n; }

  function selectSeg(container, key){
    container.querySelectorAll(".cfg-seg-btn").forEach(function(btn){
      btn.dataset.active = (btn.dataset.key === key) ? "true" : "false";
    });
  }

  var variantEl = document.getElementById("cfg-variant");
  variantEl.querySelectorAll(".cfg-seg-btn").forEach(function(btn){
    btn.addEventListener("click", function(){
      variant = btn.dataset.key;
      selectSeg(variantEl, variant);
      update();
    });
  });

  var firmwareEl = document.getElementById("cfg-firmware");
  firmwareEl.querySelectorAll(".cfg-seg-btn").forEach(function(btn){
    btn.addEventListener("click", function(){
      firmware = btn.dataset.key;
      selectSeg(firmwareEl, firmware);
      update();
    });
  });

  var coatingEl = document.getElementById("cfg-coating");
  coatingEl.querySelectorAll(".cfg-seg-btn").forEach(function(btn){
    btn.addEventListener("click", function(){
      coating = btn.dataset.key;
      selectSeg(coatingEl, coating);
      update();
    });
  });

  ADDONS.forEach(function(a){
    document.getElementById(a.id).addEventListener("change", update);
  });

  function update(){
    var v = VARIANTS[variant];
    var f = FIRMWARE[firmware];
    var c = COATINGS[coating];
    var total = v.price + f.price + c.price;
    var lines = [];

    document.getElementById("cfg-antenna-note").textContent = v.antenna;

    lines.push({label: v.label, price: v.price});
    lines.push({label: f.label, price: f.price});
    if (c.price > 0) lines.push({label: c.label, price: c.price});

    var selectedIds = {};
    ADDONS.forEach(function(a){
      var checked = document.getElementById(a.id).checked;
      selectedIds[a.id] = checked;
      if (checked){
        total += a.price;
        lines.push({label: a.label, price: a.price});
      }
    });

    var linesEl = document.getElementById("cfg-lines");
    if (lines.length === 2){
      linesEl.innerHTML = '<div class="cfg-empty">Todavía no hay accesorios seleccionados — solo la unidad base.</div>';
    } else {
      linesEl.innerHTML = lines.map(function(l){
        return '<div class="cfg-line"><span>' + l.label + '</span><span>' + fmt(l.price) + '</span></div>';
      }).join("");
    }
    document.getElementById("cfg-total-num").textContent = fmt(total);

    // Soft warnings only — nothing is blocked
    var warnEl = document.getElementById("cfg-warn-battery");
    var warnings = [];
    if (coating === "resin" && !selectedIds["cfg-lisocl2"]){
      warnings.push("El encapsulado en resina solo es compatible con baterías Li-SOCl2 — añádelas abajo, o cambia el recubrimiento.");
    }
    if (selectedIds["cfg-lisocl2"] && !selectedIds["cfg-er34615holder"]){
      warnings.push("Las baterías Li-SOCl2 necesitan el soporte/adaptador ER34615 (en Carcasa y Montaje) — añádelo arriba.");
    }
    if (warnings.length){
      warnEl.innerHTML = warnings.map(function(w){ return "<p>⚠️ " + w + "</p>"; }).join("");
      warnEl.classList.add("show");
    } else {
      warnEl.classList.remove("show");
      warnEl.innerHTML = "";
    }

    // Build the quote request mailto
    var subject = "ISURLOG - Solicitud de Presupuesto (Configurador)";
    var body = "Hola equipo de ISURKI,\n\nMe gustaria solicitar presupuesto para la siguiente configuracion de ISURLOG:\n\n";
    lines.forEach(function(l){
      body += "- " + l.label + " (" + fmt(l.price) + ")\n";
    });
    body += "\nTotal estimado: " + fmt(total) + "\n\nGracias!";
    var mailto = "mailto:tecnica@isurki.com?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    document.getElementById("cfg-quote-btn").setAttribute("href", mailto);
  }

  update();
})();
</script>
