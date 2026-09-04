# 2. Calculadora de Consumo de Energía y Vida de la Batería

Estima la vida de la batería a partir del ciclo de trabajo completo de un dispositivo — despertar, sensores, y radio — sobre NB-IoT/LTE-M, LoRaWAN, o Wi-Fi. Añade los mismos sensores que configurarías en IsurDASH; los sensores de 4-20mA y Modbus suelen ser el mayor consumo individual, ya que se alimentan desde el raíl VDC de 9-24V, no directamente de la batería.

!!! note "Valores de ejemplo"
    El timing de radio (corriente y duración de despertar/preparación/TX) está calibrado con mediciones reales para NB-IoT, LoRaWAN, y Wi-Fi. Los valores por defecto específicos de cada sensor y el margen de capacidad utilizable de la batería siguen siendo estimaciones de ingeniería — ajústalos en la sección "Avanzado" de cada widget a medida que haya mediciones reales disponibles (Power Profiler Kit, hojas de datos).

??? warning "No es infalible"
    Incluso con todos estos parámetros, esto sigue siendo un modelo, no una garantía — los despliegues reales tienen variabilidad adicional que la calculadora no contempla:

    * **Temperatura.** El frío reduce la capacidad utilizable de la batería y aumenta la resistencia interna — empeora especialmente el efecto de pasivación en las celdas Li-SOCl2.
    * **Estado de salud de la batería.** La capacidad se degrada con el número de ciclos y el simple paso del tiempo (la autodescarga también tiende a aumentar), así que una batería cerca del final de su vida útil rendirá por debajo de esta estimación.
    * **Cobertura / calidad de señal.** Una cobertura NB-IoT/LTE-M o LoRaWAN deficiente implica más reintentos, tiempos de conexión más largos, y a veces mayor potencia de transmisión que los valores por defecto del modelo.
    * **Transmisiones no programadas.** Eventos como una alarma de vandalismo/acelerómetro disparan ciclos extra de despertar y envío fuera del programa habitual, que no forman parte de este modelo periódico.
    * **Tolerancias de fabricación y de componentes.** El consumo real de corriente varía de chip a chip y de unidad a unidad respecto a los valores nominales de la hoja de datos.

    Trata el resultado como una estimación de planificación, no como una cifra de garantía.

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  .pb-wrap{
    --bg:#eef1f0; --surface:#ffffff; --surface-2:#f6f8f7;
    --border:#d7dcda; --border-strong:#b9c1be;
    --text:#182322; --text-2:#4d5957; --text-3:#7c8886;
    --accent:#b8721e; --accent-ink:#5c3810; --accent-bg:#f7e8d4;
    --nbiot:#2f5f8a; --nbiot-bg:#e2edf5;
    --lora:#6a4a9e; --lora-bg:#ece5f6;
    --wifi:#1f7a5c; --wifi-bg:#dff0e9;
    --sleep:#c9cfce; --wake:#8fb3c9; --sensors:#3f9e72; --modemprep:#5aa9c9; --tx:var(--accent); --tail:#d68a3f; --selfdis:#9b8ec7;
    --danger-bg:#f8e4e1; --danger-ink:#7a2b1c;
    --radius:10px;
    --font-ui: "IBM Plex Sans", -apple-system, "Segoe UI", sans-serif;
    --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", monospace;
  }
  [data-md-color-scheme="slate"] .pb-wrap{
    --bg:#121615; --surface:#1b201f; --surface-2:#212726;
    --border:#333b39; --border-strong:#454f4c;
    --text:#e8ece9; --text-2:#aab5b1; --text-3:#78827f;
    --accent:#e5a355; --accent-ink:#ffe4bd; --accent-bg:#3a2a15;
    --nbiot:#7fb2dc; --nbiot-bg:#1f2e3a;
    --lora:#b39be0; --lora-bg:#2c2440;
    --wifi:#6fcaa8; --wifi-bg:#193226;
    --sleep:#3a423f; --wake:#3f6580; --sensors:#3fa876; --modemprep:#4a7f9c; --tx:var(--accent); --tail:#8a5a2a; --selfdis:#7a6bb0;
    --danger-bg:#3a201a; --danger-ink:#f0b3a3;
  }
  .pb-wrap, .pb-wrap *{box-sizing:border-box;}
  .pb-wrap{max-width:1000px;margin:0 auto;padding:1.5rem 0 2rem;font-family:var(--font-ui);color:var(--text);}
  .grid{display:grid;grid-template-columns:1.25fr 1fr;gap:1.25rem;align-items:start;}
  @media (max-width:820px){.grid{grid-template-columns:1fr;}}
  .card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem;}
  .card + .card{margin-top:1.25rem;}
  .card h2{font-size:.95rem;font-weight:600;margin:0 0 1rem;}
  .card h2 small{font-weight:400;color:var(--text-3);font-size:.78rem;}
  .tabs{display:flex;gap:.4rem;margin-bottom:1.1rem;}
  .tab{flex:1;text-align:center;padding:.5rem .4rem;border-radius:8px;border:1px solid var(--border);background:var(--surface-2);color:var(--text-2);font-size:.82rem;font-weight:600;cursor:pointer;}
  .tab[data-active="true"][data-tech="nbiot"]{background:var(--nbiot-bg);color:var(--nbiot);border-color:var(--nbiot);}
  .tab[data-active="true"][data-tech="lora"]{background:var(--lora-bg);color:var(--lora);border-color:var(--lora);}
  .tab[data-active="true"][data-tech="wifi"]{background:var(--wifi-bg);color:var(--wifi);border-color:var(--wifi);}
  .field{margin-bottom:.85rem;}
  .field label{display:flex;justify-content:space-between;font-size:.8rem;color:var(--text-2);margin-bottom:.3rem;}
  .field label b{font-family:var(--font-mono);color:var(--text);font-weight:600;font-variant-numeric:tabular-nums;}
  .field input[type="range"]{width:100%;accent-color:var(--accent);}
  .buffer-alert{margin:-.3rem 0 .85rem;padding:.55rem .7rem;border-radius:7px;background:var(--danger-bg);color:var(--danger-ink);font-size:.78rem;line-height:1.4;}
  .field select, .field input[type="number"]{width:100%;height:32px;border-radius:6px;border:1px solid var(--border);background:var(--surface-2);color:var(--text);font-family:var(--font-ui);font-size:.82rem;padding:0 .5rem;}
  .row2{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;}
  .row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:.75rem;}
  .divider{border:none;border-top:1px solid var(--border);margin:1rem 0;}
  .section-label{font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:var(--text-3);margin:0 0 .6rem;}
  .result{text-align:center;padding:1.4rem 1rem 1.1rem;}
  .result .num{font-family:var(--font-mono);font-size:2.6rem;font-weight:600;font-variant-numeric:tabular-nums;line-height:1;color:var(--accent-ink);}
  .result .unit{font-size:1rem;color:var(--text-2);margin-left:.3rem;}
  .result .sub2{font-size:.8rem;color:var(--text-3);margin-top:.5rem;}
  .stat-row{display:flex;justify-content:space-between;padding:.45rem 0;border-top:1px solid var(--border);font-size:.82rem;}
  .stat-row span:first-child{color:var(--text-2);}
  .stat-row span:last-child{font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-weight:600;}
  .bar{display:flex;height:20px;border-radius:6px;overflow:hidden;margin:.75rem 0 .6rem;border:1px solid var(--border);}
  .bar div{height:100%;}
  .legend{display:flex;flex-wrap:wrap;gap:.6rem 1rem;font-size:.75rem;color:var(--text-2);}
  .legend i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:.4rem;vertical-align:1px;}
  .note{font-size:.76rem;color:var(--text-3);line-height:1.5;margin-top:1rem;}
  .add-row{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1rem;}
  .add-btn{font-size:.78rem;font-weight:600;padding:.4rem .7rem;border-radius:7px;border:1px dashed var(--border-strong);background:var(--surface-2);color:var(--text-2);cursor:pointer;}
  .add-btn:disabled{opacity:.4;cursor:not-allowed;}
  .add-btn:not(:disabled):hover{border-color:var(--sensors);color:var(--sensors);}
  .sensor-card{border:1px solid var(--border);border-radius:8px;padding:.7rem .85rem;margin-bottom:.6rem;background:var(--surface-2);}
  .sensor-head{display:flex;align-items:center;justify-content:space-between;gap:.5rem;}
  .sensor-title{font-size:.85rem;font-weight:600;}
  .sensor-summary{font-size:.74rem;color:var(--text-3);font-family:var(--font-mono);margin-top:.15rem;}
  .sensor-remove{background:none;border:none;color:var(--text-3);cursor:pointer;font-size:1rem;line-height:1;padding:.2rem .4rem;}
  .sensor-remove:hover{color:var(--danger-ink);}
  details.sensor-adv{margin-top:.5rem;}
  details.sensor-adv summary{cursor:pointer;font-size:.74rem;font-weight:600;color:var(--sensors);list-style:none;}
  details.sensor-adv summary::-webkit-details-marker{display:none;}
  details.sensor-adv summary::before{content:"▸ ";}
  details.sensor-adv[open] summary::before{content:"▾ ";}
  details.sensor-adv .field{margin-top:.6rem;}
  .empty-sensors{font-size:.8rem;color:var(--text-3);text-align:center;padding:1rem;border:1px dashed var(--border);border-radius:8px;}
  .seg{display:flex;gap:.4rem;}
  .seg-btn{flex:1;text-align:center;padding:.45rem .3rem;border-radius:7px;border:1px solid var(--border);background:var(--surface-2);color:var(--text-2);font-size:.82rem;font-weight:600;cursor:pointer;font-family:var(--font-mono);}
  .seg-btn[data-active="true"]{background:var(--sensors);color:#fff;border-color:var(--sensors);}
  .battery-readout{font-size:.8rem;color:var(--text-2);margin-top:.5rem;padding-top:.6rem;border-top:1px solid var(--border);}
  .battery-readout b{font-family:var(--font-mono);color:var(--text);}
</style>

<div class="pb-wrap">

  <div class="grid">
    <div>
      <div class="card">
        <h2>Configuración</h2>
        <p class="section-label">Conectividad</p>
        <div class="tabs" id="tabs">
          <div class="tab" data-tech="nbiot" data-active="true">NB-IoT / LTE-M</div>
          <div class="tab" data-tech="lora" data-active="false">LoRaWAN</div>
          <div class="tab" data-tech="wifi" data-active="false">Wi-Fi</div>
        </div>

        <p class="section-label">Programación</p>
        <div class="field">
          <label>Tiempo de latencia <b id="out-latency">10 min</b></label>
          <input type="range" id="latency" min="5" max="120" value="10" step="1">
        </div>
        <div class="field">
          <label>Acumulador de registros <b id="out-acc">6 lecturas/tx</b></label>
          <input type="range" id="acc" min="1" max="288" value="6" step="1">
        </div>
        <div class="buffer-alert" id="buffer-alert" style="display:none;"></div>

        <details class="sensor-adv">
          <summary>Avanzado</summary>
          <div class="row2">
            <div class="field">
              <label>Corriente en reposo <b id="out-sleep">80 µA</b></label>
              <input type="range" id="sleep" min="5" max="200" value="80" step="1">
            </div>
            <div class="field">
              <label>Eficiencia del convertidor boost <b id="out-eff">85 %</b></label>
              <input type="range" id="eff" min="50" max="98" value="85" step="1">
            </div>
          </div>
          <p class="section-label">Sobrecoste de despertar del ESP32 (por ciclo, antes de leer sensores)</p>
          <div class="row2">
            <div class="field">
              <label>Corriente de despertar <b id="out-wakeI">44 mA</b></label>
              <input type="range" id="wakeI" min="10" max="300" value="44" step="1">
            </div>
            <div class="field">
              <label>Duración del despertar <b id="out-wakeT">5000 ms</b></label>
              <input type="range" id="wakeT" min="0" max="10000" value="5000" step="100">
            </div>
          </div>
          <div class="field">
            <label>Tiempo de lectura ADC/registro del sensor (tras la preadquisición) <b id="out-settle">50 ms</b></label>
            <input type="range" id="settle" min="0" max="500" value="50" step="10">
          </div>
          <p class="section-label">Radio — preparación del módem <span style="text-transform:none;font-weight:400;">(ESP32 + módem despiertos, handshake AT, comprobación MQTT/señal — antes de la ráfaga real)</span></p>
          <div class="row2">
            <div class="field">
              <label>Corriente de preparación <b id="out-prepI">35 mA</b></label>
              <input type="range" id="prepI" min="5" max="200" value="35" step="1">
            </div>
            <div class="field">
              <label>Tiempo de preparación <b id="out-prepT">8 s</b></label>
              <input type="range" id="prepT" min="0" max="20" value="8" step="0.5">
            </div>
          </div>
          <div class="field" id="atpenalty-field">
            <label style="align-items:center;">
              <span><input type="checkbox" id="atPenaltyOn" checked style="vertical-align:-2px;margin-right:.4rem;">Penalización de reintento AT del módem (firmware &lt; v2.0.0), a la corriente de preparación</span>
              <b id="out-atPenalty">3000 ms</b>
            </label>
            <input type="range" id="atPenalty" min="0" max="5000" value="3000" step="100">
          </div>
          <p class="section-label">Radio — transmisión en ráfaga <span style="text-transform:none;font-weight:400;">(el envío real por el aire)</span></p>
          <div class="row2">
            <div class="field">
              <label>Corriente de TX <b id="out-txI">180 mA</b></label>
              <input type="range" id="txI" min="20" max="500" value="180" step="5">
            </div>
            <div class="field">
              <label>Tiempo de TX <b id="out-txT">1 s</b></label>
              <input type="range" id="txT" min="0.5" max="30" value="1" step="0.5">
            </div>
          </div>
          <div class="field" id="tail-field">
            <label>Cola de radio tras TX <b id="out-tailT">0 s (RAI activado)</b></label>
            <input type="range" id="tailT" min="0" max="35" value="0" step="1">
          </div>
        </details>
      </div>

      <div class="card">
        <h2>Batería</h2>
        <p class="section-label">Química</p>
        <div class="seg" id="battType">
          <div class="seg-btn" data-type="liion" data-active="true">Li-Ion</div>
          <div class="seg-btn" data-type="lisocl2" data-active="false">Li-SOCl2</div>
        </div>

        <p class="section-label" style="margin-top:1rem;">Número de baterías</p>
        <div class="seg" id="battCount"></div>

        <div class="battery-readout" id="battReadout"></div>

        <details class="sensor-adv">
          <summary>Avanzado</summary>
          <div class="field">
            <label>Autodescarga <b id="out-selfdis">1.0 %/mes</b></label>
            <input type="range" id="selfdis" min="0.5" max="2" value="1" step="0.1">
          </div>
          <p class="section-label" style="margin-top:.85rem;">Capacidad de la celda (por batería, nominal)</p>
          <div class="row2">
            <div class="field">
              <label>Celda Li-Ion (INR18650) <b id="out-liionCell">3400 mAh</b></label>
              <input type="range" id="liionCell" min="2000" max="3600" value="3400" step="50">
            </div>
            <div class="field">
              <label>Celda Li-SOCl2 <b id="out-lisoclCell">19000 mAh</b></label>
              <input type="range" id="lisoclCell" min="1000" max="25000" value="19000" step="100">
            </div>
          </div>
          <p class="section-label">Capacidad utilizable <span style="text-transform:none;font-weight:400;">(frente a la nominal — tiene en cuenta el margen de tensión de corte y, para Li-SOCl2, la pasivación bajo cargas pulsadas)</span></p>
          <div class="row2">
            <div class="field">
              <label>Li-Ion utilizable <b id="out-liionUsable">85 %</b></label>
              <input type="range" id="liionUsable" min="50" max="100" value="85" step="1">
            </div>
            <div class="field">
              <label>Li-SOCl2 utilizable <b id="out-lisoclUsable">85 %</b></label>
              <input type="range" id="lisoclUsable" min="40" max="100" value="85" step="1">
            </div>
          </div>
        </details>
      </div>

      <div class="card">
        <h2>Sensores <small id="sensor-count-label"></small></h2>
        <div class="add-row" id="add-row"></div>
        <div id="sensor-list"></div>
        <div class="empty-sensors" id="empty-sensors">Todavía no se ha añadido ningún sensor — añade uno arriba. Los sensores suelen dominar el consumo energético.</div>
      </div>

    </div>

    <div>
      <div class="card result">
        <div><span class="num" id="lifeNum">—</span><span class="unit" id="lifeUnit">días</span></div>
        <div class="sub2" id="lifeAlt">— meses · — años</div>
      </div>
      <div class="card">
        <h2>Desglose de energía diario</h2>
        <div class="bar" id="bar"></div>
        <div class="legend">
          <span><i style="background:var(--sleep)"></i>Reposo</span>
          <span><i style="background:var(--wake)"></i>Despertar</span>
          <span><i style="background:var(--sensors)"></i>Sensores</span>
          <span><i style="background:var(--modemprep)"></i>Prep. módem</span>
          <span><i style="background:var(--tx)"></i>TX</span>
          <span><i style="background:var(--tail)"></i>Cola</span>
          <span><i style="background:var(--selfdis)"></i>Autodescarga</span>
        </div>
        <div class="stat-row"><span>Lecturas / día</span><span id="statReads">—</span></div>
        <div class="stat-row"><span>Transmisiones / día</span><span id="statTx">—</span></div>
        <div class="stat-row"><span>Carga en reposo / día</span><span id="statSleepCharge">—</span></div>
        <div class="stat-row"><span>Carga de despertar / día</span><span id="statWakeCharge">—</span></div>
        <div class="stat-row"><span>Carga de sensores / día</span><span id="statSensorCharge">—</span></div>
        <div class="stat-row"><span>Carga de prep. módem / día</span><span id="statPrepCharge">—</span></div>
        <div class="stat-row"><span>Carga de TX / día</span><span id="statTxCharge">—</span></div>
        <div class="stat-row"><span>Carga de cola / día</span><span id="statTailCharge">—</span></div>
        <div class="stat-row"><span>Autodescarga / día</span><span id="statSelfDischarge">—</span></div>
        <div class="stat-row" style="border-top:1px solid var(--border-strong);font-weight:600;"><span>Carga usada / día (suma)</span><span id="statCharge">—</span></div>
        <div class="stat-row"><span>Consumo medio de corriente</span><span id="statAvg">—</span></div>
        <p class="note">La energía se calcula por dominio de alimentación: el consumo de los sensores integrados y de la radio/ESP32 se contabiliza directamente contra la tensión del pack de baterías; los sensores de 4-20mA y Modbus se alimentan desde el raíl VDC elevado de 9-24V, así que su contribución se convierte a mAh equivalentes de batería (V×I×t ÷ tensión de batería ÷ eficiencia del convertidor). La autodescarga se modela como un drenaje diario constante proporcional a la capacidad total.</p>
      </div>
    </div>
  </div>
</div>

<script>
(function(){
  var presets = {
    nbiot: {prepI:35, prepT:8, txI:180, txT:1, tailT:0, showTail:true, sleepUA:80, showAtPenalty:true},
    lora:  {prepI:35, prepT:6, txI:120, txT:1.2, tailT:0, showTail:false, sleepUA:50, showAtPenalty:true},
    wifi:  {prepI:100, prepT:15, txI:140, txT:2.5, tailT:0, showTail:false, sleepUA:80, showAtPenalty:false}
  };

  var BATTERY_DEFS = {
    liion:   {label:"Li-Ion",   voltage:3.7, counts:[1,2,3,4,5], defaultCount:5, selfdisMin:0.5, selfdisMax:2, selfdisDefault:1, selfdisUnit:"%/mes", selfdisDivisor:30.44},
    lisocl2: {label:"Li-SOCl2", voltage:3.6, counts:[1,2],       defaultCount:2, selfdisMin:0.5, selfdisMax:2, selfdisDefault:1, selfdisUnit:"%/año",  selfdisDivisor:365.25}
  };
  var battery = { type: "liion", count: 5 };

  var SENSOR_DEFS = {
    analog:    {label:"Analógico (4-20mA)", max:4, powered:true,  defaultCurrent:12, defaultVoltage:12, defaultPreAcq:1000},
    modbus:    {label:"Modbus",          max:4, powered:true,  defaultCurrent:12, defaultVoltage:12, defaultPreAcq:1000},
    digital:   {label:"Digital",         max:1, powered:false, defaultCurrent:1,  defaultDuration:50},
    pt100:     {label:"PT100",           max:1, powered:false, defaultCurrent:2,  defaultDuration:200},
    internalTH:{label:"Temperatura y Humedad Interna (SHT30)", max:1, powered:false, defaultCurrent:1.5, defaultDuration:200},
    externalTH:{label:"Temperatura y Humedad Externa (BME280)", max:1, powered:false, defaultCurrent:1, defaultDuration:200},
    accel:     {label:"Acelerómetro (LIS2DH12)", max:1, powered:false, defaultCurrent:1, defaultDuration:200}
  };

  var sensors = [];
  var nextId = 1;

  var el = {};
  ["latency","acc","selfdis","sleep","eff","wakeI","wakeT","settle","prepI","prepT","txI","txT","tailT","atPenalty","liionCell","lisoclCell","liionUsable","lisoclUsable"].forEach(function(id){ el[id]=document.getElementById(id); });
  var atPenaltyOn = document.getElementById("atPenaltyOn");

  function fmt(n, d){ d = d===undefined?0:d; return Number(n).toFixed(d); }

  function countByType(type){ return sensors.filter(function(s){ return s.type===type; }).length; }

  function addSensor(type){
    var def = SENSOR_DEFS[type];
    if (countByType(type) >= def.max) return;
    var s = { id: nextId++, type: type };
    if (def.powered){
      s.current = def.defaultCurrent;
      s.voltage = def.defaultVoltage;
      s.preAcq = def.defaultPreAcq;
    } else {
      s.current = def.defaultCurrent;
      s.duration = def.defaultDuration;
    }
    sensors.push(s);
    renderSensors();
    update();
  }

  function removeSensor(id){
    sensors = sensors.filter(function(s){ return s.id !== id; });
    renderSensors();
    update();
  }

  function buildAddRow(){
    var row = document.getElementById("add-row");
    row.innerHTML = "";
    Object.keys(SENSOR_DEFS).forEach(function(type){
      var def = SENSOR_DEFS[type];
      var btn = document.createElement("button");
      btn.className = "add-btn";
      btn.type = "button";
      btn.dataset.type = type;
      row.appendChild(btn);
    });
  }

  function refreshAddRow(){
    var row = document.getElementById("add-row");
    Array.prototype.forEach.call(row.children, function(btn){
      var type = btn.dataset.type;
      var def = SENSOR_DEFS[type];
      var count = countByType(type);
      btn.textContent = "+ " + def.label + " (" + count + "/" + def.max + ")";
      btn.disabled = count >= def.max;
    });
  }

  function renderSensors(){
    refreshAddRow();
    var list = document.getElementById("sensor-list");
    var empty = document.getElementById("empty-sensors");
    var countLabel = document.getElementById("sensor-count-label");
    countLabel.textContent = sensors.length ? "(" + sensors.length + (sensors.length === 1 ? " añadido)" : " añadidos)") : "";
    list.innerHTML = "";
    empty.style.display = sensors.length ? "none" : "block";

    sensors.forEach(function(s){
      var def = SENSOR_DEFS[s.type];
      var card = document.createElement("div");
      card.className = "sensor-card";

      var summary = def.powered
        ? s.voltage + "V · " + s.current + "mA · " + s.preAcq + "ms preadq."
        : s.current + "mA · " + s.duration + "ms";

      var head = document.createElement("div");
      head.className = "sensor-head";
      head.innerHTML =
        '<div><div class="sensor-title">' + def.label + '</div>' +
        '<div class="sensor-summary" data-role="summary">' + summary + '</div></div>' +
        '<button class="sensor-remove" type="button" aria-label="Eliminar sensor">×</button>';
      head.querySelector(".sensor-remove").addEventListener("click", function(){ removeSensor(s.id); });
      card.appendChild(head);

      var adv = document.createElement("details");
      adv.className = "sensor-adv";
      var advSummary = document.createElement("summary");
      advSummary.textContent = "Avanzado";
      adv.appendChild(advSummary);

      if (def.powered){
        adv.appendChild(makeField("Corriente", s.current, "mA", 5, 80, 1, function(v){ s.current = v; }));
        adv.appendChild(makeSelectField("Tensión", s.voltage, [9,12,18,24], "V", function(v){ s.voltage = v; }));
        adv.appendChild(makeField("Tiempo de preadquisición", s.preAcq, "ms", 0, 5000, 50, function(v){ s.preAcq = v; }));
      } else {
        adv.appendChild(makeField("Corriente", s.current, "mA", 0.1, 50, 0.1, function(v){ s.current = v; }));
        adv.appendChild(makeField("Duración activa", s.duration, "ms", 5, 5000, 5, function(v){ s.duration = v; }));
      }
      card.appendChild(adv);

      function refreshSummary(){
        var sum = def.powered
          ? s.voltage + "V · " + s.current + "mA · " + s.preAcq + "ms preadq."
          : s.current + "mA · " + s.duration + "ms";
        head.querySelector('[data-role="summary"]').textContent = sum;
      }
      adv.addEventListener("input", refreshSummary);

      list.appendChild(card);
    });
  }

  function makeField(labelText, value, unit, min, max, step, onChange){
    var wrap = document.createElement("div");
    wrap.className = "field";
    var id = "f" + Math.random().toString(36).slice(2);
    wrap.innerHTML = '<label>' + labelText + ' <b>' + fmt(value, step<1?1:0) + ' ' + unit + '</b></label>' +
      '<input type="range" id="' + id + '" min="' + min + '" max="' + max + '" value="' + value + '" step="' + step + '">';
    var input = wrap.querySelector("input");
    var out = wrap.querySelector("b");
    input.addEventListener("input", function(){
      var v = +input.value;
      out.textContent = fmt(v, step<1?1:0) + " " + unit;
      onChange(v);
      update();
    });
    return wrap;
  }

  function makeSelectField(labelText, value, options, unit, onChange){
    var wrap = document.createElement("div");
    wrap.className = "field";
    var label = document.createElement("label");
    label.textContent = labelText;
    wrap.appendChild(label);
    var select = document.createElement("select");
    options.forEach(function(opt){
      var o = document.createElement("option");
      o.value = opt; o.textContent = opt + " " + unit;
      if (opt === value) o.selected = true;
      select.appendChild(o);
    });
    select.addEventListener("change", function(){
      onChange(+select.value);
      update();
    });
    wrap.appendChild(select);
    return wrap;
  }

  function renderBattCount(){
    var def = BATTERY_DEFS[battery.type];
    var wrap = document.getElementById("battCount");
    wrap.innerHTML = "";
    def.counts.forEach(function(n){
      var btn = document.createElement("div");
      btn.className = "seg-btn";
      btn.dataset.count = n;
      btn.dataset.active = (n === battery.count) ? "true" : "false";
      btn.textContent = n;
      btn.addEventListener("click", function(){
        battery.count = n;
        renderBattCount();
        update();
      });
      wrap.appendChild(btn);
    });
  }

  document.querySelectorAll("#battType .seg-btn").forEach(function(btn){
    btn.addEventListener("click", function(){
      document.querySelectorAll("#battType .seg-btn").forEach(function(x){ x.dataset.active = "false"; });
      btn.dataset.active = "true";
      battery.type = btn.dataset.type;
      var def = BATTERY_DEFS[battery.type];
      battery.count = def.defaultCount;
      el.selfdis.min = def.selfdisMin;
      el.selfdis.max = def.selfdisMax;
      el.selfdis.value = def.selfdisDefault;
      renderBattCount();
      update();
    });
  });
  renderBattCount();

  document.querySelectorAll(".tab").forEach(function(t){
    t.addEventListener("click", function(){
      document.querySelectorAll(".tab").forEach(function(x){ x.dataset.active = "false"; });
      t.dataset.active = "true";
      var p = presets[t.dataset.tech];
      el.prepI.value = p.prepI; el.prepT.value = p.prepT; el.txI.value = p.txI; el.txT.value = p.txT; el.tailT.value = p.tailT; el.sleep.value = p.sleepUA;
      document.getElementById("tail-field").style.display = p.showTail ? "block" : "none";
      document.getElementById("atpenalty-field").style.display = p.showAtPenalty ? "block" : "none";
      update();
    });
  });
  document.getElementById("tail-field").style.display = "block";

  buildAddRow();
  document.getElementById("add-row").addEventListener("click", function(e){
    var btn = e.target.closest(".add-btn");
    if (btn && !btn.disabled) addSensor(btn.dataset.type);
  });

  function update(){
    var latency = +el.latency.value, acc = +el.acc.value;
    var sleepUA = +el.sleep.value, eff = +el.eff.value/100;
    var wakeI = +el.wakeI.value, wakeT = +el.wakeT.value, settle = +el.settle.value;
    var prepI = +el.prepI.value, prepT = +el.prepT.value;
    var txI = +el.txI.value, txT = +el.txT.value, tailT = +el.tailT.value;
    var atPenaltyMs = atPenaltyOn.checked ? +el.atPenalty.value : 0;
    var selfdisRate = +el.selfdis.value;
    var liionCell = +el.liionCell.value, lisoclCell = +el.lisoclCell.value;
    var liionUsable = +el.liionUsable.value, lisoclUsable = +el.lisoclUsable.value;

    var battDef = BATTERY_DEFS[battery.type];
    var BATTERY_V = battDef.voltage;
    var cellCapacity = battery.type === "liion" ? liionCell : lisoclCell;
    var usablePct = battery.type === "liion" ? liionUsable : lisoclUsable;
    var capRated = battery.count * cellCapacity;
    var cap = capRated * (usablePct/100);

    document.getElementById("out-latency").textContent = latency + " min";
    document.getElementById("out-acc").textContent = acc + " lecturas/tx";
    document.getElementById("out-selfdis").textContent = fmt(selfdisRate,1) + " " + battDef.selfdisUnit;
    document.getElementById("out-liionCell").textContent = fmt(liionCell,0) + " mAh";
    document.getElementById("out-lisoclCell").textContent = fmt(lisoclCell,0) + " mAh";
    document.getElementById("out-liionUsable").textContent = fmt(liionUsable,0) + " %";
    document.getElementById("out-lisoclUsable").textContent = fmt(lisoclUsable,0) + " %";
    document.getElementById("battReadout").innerHTML = battery.count + "× " + battDef.label + " → " + fmt(capRated,0) + " mAh nominal → <b>" + fmt(cap,0) + " mAh utilizables</b> @ " + BATTERY_V + "V";
    document.getElementById("out-sleep").textContent = sleepUA + " µA";
    document.getElementById("out-eff").textContent = (+el.eff.value) + " %";
    document.getElementById("out-wakeI").textContent = wakeI + " mA";
    document.getElementById("out-wakeT").textContent = wakeT + " ms";
    document.getElementById("out-settle").textContent = settle + " ms";
    document.getElementById("out-prepI").textContent = prepI + " mA";
    document.getElementById("out-prepT").textContent = fmt(prepT,1) + " s";
    document.getElementById("out-txI").textContent = txI + " mA";
    document.getElementById("out-txT").textContent = fmt(txT,1) + " s";
    document.getElementById("out-tailT").textContent = tailT + " s" + (tailT===0 ? " (RAI activado)" : "");
    document.getElementById("out-atPenalty").textContent = fmt(+el.atPenalty.value,0) + " ms";

    var readsDay = 1440 / latency;
    var txDay = readsDay / acc;

    var bufferAlert = document.getElementById("buffer-alert");
    if (txDay < 1){
      var bufferHours = (latency*acc)/60;
      bufferAlert.style.display = "block";
      bufferAlert.textContent = "⚠️ Con esta configuración, el dispositivo transmite solo cada " + fmt(bufferHours,1) + " horas (menos de una vez al día). No se recomienda esta configuración.";
    } else {
      bufferAlert.style.display = "none";
    }

    // per-cycle: wake overhead time (mAh-equivalent, direct battery domain)
    var wakeMAh_perCycle = wakeI * (wakeT/3600000);

    // per-cycle: sensors
    var sensorsMAh_perCycle = 0;
    var sensorsTimeMs_perCycle = 0;
    sensors.forEach(function(s){
      var def = SENSOR_DEFS[s.type];
      if (def.powered){
        var t_ms = s.preAcq + settle;
        var mWh = s.voltage * s.current * (t_ms/3600000);
        sensorsMAh_perCycle += mWh / BATTERY_V / eff;
        sensorsTimeMs_perCycle += t_ms;
      } else {
        sensorsMAh_perCycle += s.current * (s.duration/3600000);
        sensorsTimeMs_perCycle += s.duration;
      }
    });

    var wakeMAh_day = readsDay * wakeMAh_perCycle;
    var sensorsMAh_day = readsDay * sensorsMAh_perCycle;
    var prepMAh_day = txDay * prepI * ((prepT + atPenaltyMs/1000)/3600);
    var txMAh_day = txDay * txI * (txT/3600);
    var tailMAh_day = txDay * txI * (tailT/3600);

    var activeS_day = readsDay*(wakeT+sensorsTimeMs_perCycle)/1000 + txDay*(prepT+atPenaltyMs/1000+txT+tailT);
    var sleepS_day = Math.max(0, 86400 - activeS_day);
    var sleepMAh_day = (sleepUA/1000) * (sleepS_day/3600);

    var selfDischargeMAh_day = cap * (selfdisRate/100) / battDef.selfdisDivisor;

    var totalMAh_day = sleepMAh_day + wakeMAh_day + sensorsMAh_day + prepMAh_day + txMAh_day + tailMAh_day + selfDischargeMAh_day;
    var lifeDays = cap / totalMAh_day;
    var avgMA = totalMAh_day / 24;

    document.getElementById("lifeNum").textContent = lifeDays >= 1000 ? fmt(lifeDays/365,1) : fmt(lifeDays,0);
    document.getElementById("lifeUnit").textContent = lifeDays >= 1000 ? " años" : " días";
    document.getElementById("lifeAlt").textContent = fmt(lifeDays/30.44,1) + " meses · " + fmt(lifeDays/365.25,2) + " años";

    document.getElementById("statReads").textContent = fmt(readsDay,1) + " /día";
    document.getElementById("statTx").textContent = fmt(txDay,2) + " /día";
    document.getElementById("statSleepCharge").textContent = fmt(sleepMAh_day,2) + " mAh";
    document.getElementById("statWakeCharge").textContent = fmt(wakeMAh_day,2) + " mAh";
    document.getElementById("statSensorCharge").textContent = fmt(sensorsMAh_day,2) + " mAh";
    document.getElementById("statPrepCharge").textContent = fmt(prepMAh_day,2) + " mAh";
    document.getElementById("statTxCharge").textContent = fmt(txMAh_day,2) + " mAh";
    document.getElementById("statTailCharge").textContent = fmt(tailMAh_day,2) + " mAh";
    document.getElementById("statSelfDischarge").textContent = fmt(selfDischargeMAh_day,2) + " mAh";
    document.getElementById("statAvg").textContent = fmt(avgMA,2) + " mA";
    document.getElementById("statCharge").textContent = fmt(totalMAh_day,2) + " mAh";

    var total = totalMAh_day;
    var bar = document.getElementById("bar");
    bar.innerHTML =
      '<div style="width:'+(100*sleepMAh_day/total)+'%;background:var(--sleep)"></div>' +
      '<div style="width:'+(100*wakeMAh_day/total)+'%;background:var(--wake)"></div>' +
      '<div style="width:'+(100*sensorsMAh_day/total)+'%;background:var(--sensors)"></div>' +
      '<div style="width:'+(100*prepMAh_day/total)+'%;background:var(--modemprep)"></div>' +
      '<div style="width:'+(100*txMAh_day/total)+'%;background:var(--tx)"></div>' +
      '<div style="width:'+(100*tailMAh_day/total)+'%;background:var(--tail)"></div>' +
      '<div style="width:'+(100*selfDischargeMAh_day/total)+'%;background:var(--selfdis)"></div>';
  }

  Object.keys(el).forEach(function(id){ el[id].addEventListener("input", update); });
  atPenaltyOn.addEventListener("change", update);
  document.getElementById("atpenalty-field").style.display = "block";

  renderSensors();
  update();
})();
</script>
