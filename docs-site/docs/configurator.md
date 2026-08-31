# 2. Build Your Own ISURLOG

Pick your options below — the total updates as you go. This only includes items available directly from Isurki (with a real price); for the "bring your own" alternatives, full specs, and supplier links for each item, see **[1. Parts and Accessories](parts-and-accessories.md)**. When you're ready, request a quote and we'll confirm compatibility and final pricing.

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
    <h3>Connectivity</h3>
    <div class="cfg-seg" id="cfg-variant">
      <div class="cfg-seg-btn" data-key="nbiot" data-active="true"><span class="lbl">NB-IoT / LTE-M</span><span class="pr">€387</span></div>
      <div class="cfg-seg-btn" data-key="lora" data-active="false"><span class="lbl">LoRaWAN</span><span class="pr">€330</span></div>
      <div class="cfg-seg-btn" data-key="wifi" data-active="false"><span class="lbl">Wi-Fi only</span><span class="pr">€310</span></div>
    </div>
    <p class="cfg-note" id="cfg-antenna-note"></p>
  </div>

  <div class="cfg-card">
    <h3>Firmware</h3>
    <div class="cfg-seg" id="cfg-firmware" style="flex-direction:column;">
      <div class="cfg-seg-btn" data-key="standard" data-active="true"><span class="lbl">Standard firmware, connected to IsurDASH</span><span class="pr">€0</span></div>
      <div class="cfg-seg-btn" data-key="byo" data-active="false"><span class="lbl">Flash your own firmware</span><span class="pr">€0</span></div>
    </div>
  </div>

  <div class="cfg-card">
    <h3>Protective Coating</h3>
    <div class="cfg-seg" id="cfg-coating" style="flex-direction:column;">
      <div class="cfg-seg-btn" data-key="standard" data-active="true"><span class="lbl">Standard conformal coating</span><span class="pr">Included</span></div>
      <div class="cfg-seg-btn" data-key="extra" data-active="false"><span class="lbl">Extra conformal coating layer</span><span class="pr">+€15</span></div>
      <div class="cfg-seg-btn" data-key="resin" data-active="false"><span class="lbl">Resin potting (Li-SOCl2 only)</span><span class="pr">+€80</span></div>
    </div>
  </div>

  <div class="cfg-card">
    <h3>Enclosure &amp; Mounting</h3>
    <div class="cfg-row"><input type="checkbox" id="cfg-enclosure"><label for="cfg-enclosure">3D-printed enclosure (PETG, IP66)</label><span class="pr">€35</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-dinrail"><label for="cfg-dinrail">DIN rail mount</label><span class="pr">€28</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-pole"><label for="cfg-pole">Pole mount</label><span class="pr">€18</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-er34615holder"><label for="cfg-er34615holder">ER34615 battery holder/adapter<span class="sub">Required to use Li-SOCl2 batteries</span></label><span class="pr">€20</span></div>
  </div>

  <div class="cfg-card">
    <h3>Batteries</h3>
    <div class="cfg-row"><input type="checkbox" id="cfg-liion"><label for="cfg-liion">18650 Li-Ion, set of 5 (rechargeable)</label><span class="pr">€30</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-lisocl2"><label for="cfg-lisocl2">Li-SOCl2, set of 2 (non-rechargeable, v3.3+)</label><span class="pr">€40</span></div>
    <div class="cfg-warn" id="cfg-warn-battery"></div>
  </div>

  <div class="cfg-card">
    <h3>External / Solar Power</h3>
    <div class="cfg-row"><input type="checkbox" id="cfg-solar5v"><label for="cfg-solar5v">5V regulated solar panel</label><span class="pr">€34</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-walladapter"><label for="cfg-walladapter">5V/1A wall power adapter</label><span class="pr">€20</span></div>
    <div class="cfg-row"><input type="checkbox" id="cfg-usbcable"><label for="cfg-usbcable">USB-A to Micro-USB cable (for PIN-terminal power)</label><span class="pr">€10</span></div>
  </div>

  <div class="cfg-card">
    <h3>Connectivity Plan</h3>
    <div class="cfg-row"><input type="checkbox" id="cfg-esim"><label for="cfg-esim">Integrated eSIM + data plan<span class="sub">500 MB or 5 years, whichever comes first</span></label><span class="pr">€36</span></div>
  </div>

  <div class="cfg-summary">
    <h3>Your Configuration</h3>
    <div id="cfg-lines"><div class="cfg-empty">No add-ons selected yet — just the base unit.</div></div>
    <div class="cfg-total"><span class="label">Total</span><span class="num" id="cfg-total-num">€387</span></div>
    <a class="cfg-cta" id="cfg-quote-btn" href="#">Request a Quote for This Configuration</a>
    <p class="cfg-note">This is an estimate, not a final price — we'll confirm compatibility and exact cost when you request a quote. Clicking the button opens your email client with everything pre-filled.</p>
  </div>

</div>

<script>
(function(){
  var VARIANTS = {
    nbiot: {label:"ISURLOG — NB-IoT/LTE-M variant", price:387, antenna:"Includes the NB-IoT/LTE-M antenna (shared with GPS reception)."},
    lora:  {label:"ISURLOG — LoRaWAN variant", price:330, antenna:"Includes the LoRaWAN (868 MHz) antenna."},
    wifi:  {label:"ISURLOG — Wi-Fi only", price:310, antenna:"Uses the antenna integrated on the PCB — no external antenna needed."}
  };
  var COATINGS = {
    standard: {label:"Standard conformal coating", price:0},
    extra:    {label:"Extra conformal coating layer", price:15},
    resin:    {label:"Resin potting", price:80}
  };
  var ADDONS = [
    {id:"cfg-enclosure", label:"3D-printed enclosure (PETG, IP66)", price:35},
    {id:"cfg-dinrail", label:"DIN rail mount", price:28},
    {id:"cfg-pole", label:"Pole mount", price:18},
    {id:"cfg-er34615holder", label:"ER34615 battery holder/adapter", price:20},
    {id:"cfg-liion", label:"18650 Li-Ion batteries, set of 5", price:30},
    {id:"cfg-lisocl2", label:"Li-SOCl2 batteries, set of 2", price:40},
    {id:"cfg-solar5v", label:"5V regulated solar panel", price:34},
    {id:"cfg-walladapter", label:"5V/1A wall power adapter", price:20},
    {id:"cfg-usbcable", label:"USB-A to Micro-USB cable", price:10},
    {id:"cfg-esim", label:"Integrated eSIM + data plan", price:36}
  ];
  var FIRMWARE = {
    standard: {label:"Standard firmware, connected to IsurDASH", price:0},
    byo:      {label:"Flash your own firmware", price:0}
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
      linesEl.innerHTML = '<div class="cfg-empty">No add-ons selected yet — just the base unit.</div>';
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
      warnings.push("Resin potting is only compatible with Li-SOCl2 batteries — add those below, or switch coating.");
    }
    if (selectedIds["cfg-lisocl2"] && !selectedIds["cfg-er34615holder"]){
      warnings.push("Li-SOCl2 batteries need the ER34615 battery holder/adapter (in Enclosure & Mounting) — add it above.");
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
