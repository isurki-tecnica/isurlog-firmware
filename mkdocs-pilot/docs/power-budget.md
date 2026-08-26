# Power Budget & Battery Life Calculator

Estimate battery life from a device's duty cycle: how often it wakes, reads sensors, and transmits over NB-IoT/LTE-M, LoRaWAN, or Wi-Fi.

!!! note "Example values"
    Current/duration values below are illustrative, not measured specs. They will be replaced with real figures from a Nordic Power Profiler Kit once available.

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  .pb-wrap{
    --bg:#eef1f0; --surface:#ffffff; --surface-2:#f6f8f7;
    --border:#d7dcda;
    --text:#182322; --text-2:#4d5957; --text-3:#7c8886;
    --accent:#b8721e; --accent-ink:#5c3810;
    --nbiot:#2f5f8a; --nbiot-bg:#e2edf5;
    --lora:#6a4a9e; --lora-bg:#ece5f6;
    --wifi:#1f7a5c; --wifi-bg:#dff0e9;
    --sleep:#c9cfce; --read:#8fb3c9; --tx:var(--accent); --tail:#d68a3f;
    --radius:10px;
    font-family:"IBM Plex Sans", -apple-system, "Segoe UI", sans-serif;
    color:var(--text);
  }
  [data-md-color-scheme="slate"] .pb-wrap{
    --bg:#121615; --surface:#1b201f; --surface-2:#212726;
    --border:#333b39;
    --text:#e8ece9; --text-2:#aab5b1; --text-3:#78827f;
    --accent:#e5a355; --accent-ink:#ffe4bd;
    --nbiot:#7fb2dc; --nbiot-bg:#1f2e3a;
    --lora:#b39be0; --lora-bg:#2c2440;
    --wifi:#6fcaa8; --wifi-bg:#193226;
    --sleep:#3a423f; --read:#3f6580; --tail:#8a5a2a;
  }
  .pb-wrap *{box-sizing:border-box;}
  .pb-grid{display:grid;grid-template-columns:1.15fr 1fr;gap:1.25rem;align-items:start;margin:1.5rem 0;}
  @media (max-width:760px){.pb-grid{grid-template-columns:1fr;}}
  .pb-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem;}
  .pb-card + .pb-card{margin-top:1.25rem;}
  .pb-card h2{font-size:.95rem;font-weight:600;margin:0 0 1rem;}
  .pb-tabs{display:flex;gap:.4rem;margin-bottom:1.1rem;}
  .pb-tab{flex:1;text-align:center;padding:.5rem .4rem;border-radius:8px;border:1px solid var(--border);background:var(--surface-2);color:var(--text-2);font-size:.82rem;font-weight:600;cursor:pointer;}
  .pb-tab[data-active="true"][data-tech="nbiot"]{background:var(--nbiot-bg);color:var(--nbiot);border-color:var(--nbiot);}
  .pb-tab[data-active="true"][data-tech="lora"]{background:var(--lora-bg);color:var(--lora);border-color:var(--lora);}
  .pb-tab[data-active="true"][data-tech="wifi"]{background:var(--wifi-bg);color:var(--wifi);border-color:var(--wifi);}
  .pb-field{margin-bottom:.85rem;}
  .pb-field label{display:flex;justify-content:space-between;font-size:.8rem;color:var(--text-2);margin-bottom:.3rem;}
  .pb-field label b{font-family:"IBM Plex Mono",monospace;color:var(--text);font-weight:600;}
  .pb-field input[type="range"]{width:100%;accent-color:var(--accent);}
  .pb-row2{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;}
  .pb-divider{border:none;border-top:1px solid var(--border);margin:1rem 0;}
  .pb-section-label{font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:var(--text-3);margin:0 0 .6rem;}
  .pb-result{text-align:center;padding:1.4rem 1rem 1.1rem;}
  .pb-result .num{font-family:"IBM Plex Mono",monospace;font-size:2.6rem;font-weight:600;line-height:1;color:var(--accent-ink);}
  .pb-result .unit{font-size:1rem;color:var(--text-2);margin-left:.3rem;}
  .pb-result .sub2{font-size:.8rem;color:var(--text-3);margin-top:.5rem;}
  .pb-stat-row{display:flex;justify-content:space-between;padding:.45rem 0;border-top:1px solid var(--border);font-size:.82rem;}
  .pb-stat-row span:first-child{color:var(--text-2);}
  .pb-stat-row span:last-child{font-family:"IBM Plex Mono",monospace;font-weight:600;}
  .pb-bar{display:flex;height:20px;border-radius:6px;overflow:hidden;margin:.75rem 0 .6rem;border:1px solid var(--border);}
  .pb-bar div{height:100%;}
  .pb-legend{display:flex;flex-wrap:wrap;gap:.6rem 1rem;font-size:.75rem;color:var(--text-2);}
  .pb-legend i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:.4rem;vertical-align:1px;}
  .pb-note{font-size:.76rem;color:var(--text-3);line-height:1.5;margin-top:1rem;}
</style>

<div class="pb-wrap">
  <div class="pb-grid">
    <div>
      <div class="pb-card">
        <h2>Connectivity</h2>
        <div class="pb-tabs" id="pb-tabs">
          <div class="pb-tab" data-tech="nbiot" data-active="true">NB-IoT / LTE-M</div>
          <div class="pb-tab" data-tech="lora" data-active="false">LoRaWAN</div>
          <div class="pb-tab" data-tech="wifi" data-active="false">Wi-Fi</div>
        </div>

        <p class="pb-section-label">Schedule</p>
        <div class="pb-field">
          <label>Latency time <b id="pb-out-latency">10 min</b></label>
          <input type="range" id="pb-latency" min="1" max="120" value="10" step="1">
        </div>
        <div class="pb-field">
          <label>Record accumulator <b id="pb-out-acc">6 reads/tx</b></label>
          <input type="range" id="pb-acc" min="1" max="30" value="6" step="1">
        </div>

        <hr class="pb-divider">
        <p class="pb-section-label">Duty-cycle currents (example)</p>
        <div class="pb-field">
          <label>Sleep current <b id="pb-out-sleep">20 µA</b></label>
          <input type="range" id="pb-sleep" min="5" max="100" value="20" step="1">
        </div>
        <div class="pb-row2">
          <div class="pb-field">
            <label>Read current <b id="pb-out-readI">80 mA</b></label>
            <input type="range" id="pb-readI" min="10" max="300" value="80" step="5">
          </div>
          <div class="pb-field">
            <label>Read time <b id="pb-out-readT">2.5 s</b></label>
            <input type="range" id="pb-readT" min="0.5" max="10" value="2.5" step="0.5">
          </div>
        </div>
        <div class="pb-row2">
          <div class="pb-field">
            <label>TX current <b id="pb-out-txI">180 mA</b></label>
            <input type="range" id="pb-txI" min="20" max="500" value="180" step="5">
          </div>
          <div class="pb-field">
            <label>TX time <b id="pb-out-txT">4 s</b></label>
            <input type="range" id="pb-txT" min="0.5" max="30" value="4" step="0.5">
          </div>
        </div>
        <div class="pb-field" id="pb-tail-field">
          <label>Radio tail after TX <b id="pb-out-tailT">0 s (RAI on)</b></label>
          <input type="range" id="pb-tailT" min="0" max="35" value="0" step="1">
        </div>

        <hr class="pb-divider">
        <p class="pb-section-label">Battery</p>
        <div class="pb-field">
          <label>Capacity <b id="pb-out-cap">17000 mAh</b> <span style="font-weight:400">(5× INR18650)</span></label>
          <input type="range" id="pb-cap" min="2000" max="17000" value="17000" step="500">
        </div>
      </div>
    </div>

    <div>
      <div class="pb-card pb-result">
        <div><span class="num" id="pb-lifeNum">—</span><span class="unit" id="pb-lifeUnit">days</span></div>
        <div class="sub2" id="pb-lifeAlt">— months · — years</div>
      </div>
      <div class="pb-card">
        <h2>Daily energy breakdown</h2>
        <div class="pb-bar" id="pb-bar"></div>
        <div class="pb-legend">
          <span><i style="background:var(--sleep)"></i>Sleep</span>
          <span><i style="background:var(--read)"></i>Read</span>
          <span><i style="background:var(--tx)"></i>TX</span>
          <span><i style="background:var(--tail)"></i>Tail</span>
        </div>
        <div class="pb-stat-row"><span>Reads / day</span><span id="pb-statReads">—</span></div>
        <div class="pb-stat-row"><span>Transmissions / day</span><span id="pb-statTx">—</span></div>
        <div class="pb-stat-row"><span>Avg. current draw</span><span id="pb-statAvg">—</span></div>
        <div class="pb-stat-row"><span>Charge used / day</span><span id="pb-statCharge">—</span></div>
        <p class="pb-note">Formula: capacity ÷ (sleep_current × sleep_time + Σ active_current × active_time per cycle, per day). Real-world life varies with temperature, coverage, and battery age/self-discharge.</p>
      </div>
    </div>
  </div>
</div>

<script>
(function(){
  var presets = {
    nbiot: {sleep:20, readI:80, readT:2.5, txI:180, txT:4, tailT:0, showTail:true},
    lora:  {sleep:15, readI:80, readT:2.5, txI:120, txT:1.2, tailT:0, showTail:false},
    wifi:  {sleep:20, readI:80, readT:2.5, txI:140, txT:2.5, tailT:0, showTail:false}
  };
  var el = {};
  ["latency","acc","sleep","readI","readT","txI","txT","tailT","cap"].forEach(function(id){ el[id]=document.getElementById("pb-"+id); });

  document.querySelectorAll(".pb-tab").forEach(function(t){
    t.addEventListener("click", function(){
      document.querySelectorAll(".pb-tab").forEach(function(x){ x.dataset.active = "false"; });
      t.dataset.active = "true";
      var p = presets[t.dataset.tech];
      el.sleep.value = p.sleep; el.readI.value = p.readI; el.readT.value = p.readT;
      el.txI.value = p.txI; el.txT.value = p.txT; el.tailT.value = p.tailT;
      document.getElementById("pb-tail-field").style.display = p.showTail ? "block" : "none";
      update();
    });
  });

  function fmt(n, d){ d = d===undefined?0:d; return Number(n).toLocaleString(undefined,{minimumFractionDigits:d,maximumFractionDigits:d}); }

  function update(){
    var latency = +el.latency.value, acc = +el.acc.value;
    var sleepUA = +el.sleep.value, readI = +el.readI.value, readT = +el.readT.value;
    var txI = +el.txI.value, txT = +el.txT.value, tailT = +el.tailT.value;
    var cap = +el.cap.value;

    document.getElementById("pb-out-latency").textContent = latency + " min";
    document.getElementById("pb-out-acc").textContent = acc + " reads/tx";
    document.getElementById("pb-out-sleep").textContent = sleepUA + " µA";
    document.getElementById("pb-out-readI").textContent = readI + " mA";
    document.getElementById("pb-out-readT").textContent = fmt(readT,1) + " s";
    document.getElementById("pb-out-txI").textContent = txI + " mA";
    document.getElementById("pb-out-txT").textContent = fmt(txT,1) + " s";
    document.getElementById("pb-out-tailT").textContent = tailT + " s" + (tailT===0 ? " (RAI on)" : "");
    document.getElementById("pb-out-cap").textContent = fmt(cap,0) + " mAh";

    var readsDay = 1440 / latency;
    var txDay = readsDay / acc;

    var tReadS = readsDay * readT;
    var tTxS = txDay * txT;
    var tTailS = txDay * tailT;
    var tSleepS = Math.max(0, 86400 - tReadS - tTxS - tTailS);

    var chargeMAh = (sleepUA/1000) * (tSleepS/3600)
                  + readI * (tReadS/3600)
                  + txI * (tTxS/3600)
                  + txI * (tTailS/3600);

    var lifeDays = cap / chargeMAh;
    var avgMA = chargeMAh / 24;

    document.getElementById("pb-lifeNum").textContent = lifeDays >= 1000 ? fmt(lifeDays/365,1) : fmt(lifeDays,0);
    document.getElementById("pb-lifeUnit").textContent = lifeDays >= 1000 ? " years" : " days";
    document.getElementById("pb-lifeAlt").textContent = fmt(lifeDays/30.44,1) + " months · " + fmt(lifeDays/365.25,2) + " years";

    document.getElementById("pb-statReads").textContent = fmt(readsDay,1) + " /day";
    document.getElementById("pb-statTx").textContent = fmt(txDay,2) + " /day";
    document.getElementById("pb-statAvg").textContent = fmt(avgMA,3) + " mA";
    document.getElementById("pb-statCharge").textContent = fmt(chargeMAh,3) + " mAh";

    var totalS = tSleepS + tReadS + tTxS + tTailS;
    var bar = document.getElementById("pb-bar");
    bar.innerHTML =
      '<div style="width:'+(100*tSleepS/totalS)+'%;background:var(--sleep)"></div>' +
      '<div style="width:'+(100*tReadS/totalS)+'%;background:var(--read)"></div>' +
      '<div style="width:'+(100*tTxS/totalS)+'%;background:var(--tx)"></div>' +
      '<div style="width:'+(100*tTailS/totalS)+'%;background:var(--tail)"></div>';
  }

  Object.keys(el).forEach(function(id){ el[id].addEventListener("input", update); });
  update();
})();
</script>
