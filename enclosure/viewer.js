// Enclosure page: viewer toggles and the part picker.
// Each control carries data-viewer (id of a <model-viewer>) and data-src (the GLB to load);
// part buttons also carry data-panel (id of the info panel to show).
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) {
    document.querySelectorAll("model-viewer").forEach(function (v) { v.removeAttribute("auto-rotate"); });
  }

  document.querySelectorAll("[data-viewer]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var viewer = document.getElementById(btn.getAttribute("data-viewer"));
      if (!viewer) { return; }
      viewer.setAttribute("src", btn.getAttribute("data-src"));

      btn.parentNode.querySelectorAll("[data-viewer]").forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });

      var panelId = btn.getAttribute("data-panel");
      if (panelId) {
        document.querySelectorAll(".encl-info").forEach(function (p) { p.hidden = true; });
        var panel = document.getElementById(panelId);
        if (panel) { panel.hidden = false; }
      }
    });
  });
})();

// Videos opened in the lightbox should loop like the inline ones do.
new MutationObserver(function (muts) {
  muts.forEach(function (m) {
    m.addedNodes.forEach(function (n) {
      if (n.nodeType !== 1) { return; }
      var vids = n.matches && n.matches("video") ? [n] : (n.querySelectorAll ? n.querySelectorAll("video") : []);
      Array.prototype.forEach.call(vids, function (v) { v.loop = true; });
    });
  });
}).observe(document.body, { childList: true, subtree: true });

// Hero: slider that assembles / takes apart the enclosure by scrubbing the GLB's "explode" animation.
(function () {
  var hero = document.getElementById("encl-hero");
  var range = document.getElementById("encl-range");
  if (!hero || !range) { return; }

  var presets = document.querySelectorAll("[data-explode]");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var RADIUS_FACTOR = 1.95;   // camera distance when fully exploded, relative to assembled
  var RISE = 0.045;         // metres the model centre moves up when fully exploded
  var t = 0, base = null, userZoomed = false, raf = 0, savedOrbit = null;
  var variants = document.querySelectorAll("[data-variant]");
  var note = document.getElementById("encl-note");

  function apply() {
    hero.pause();
    // stay a hair under the duration: the clip loops, so exactly 1.0 would wrap back to 0
    hero.currentTime = t * (hero.duration || 1) * 0.9999;
    if (!base || userZoomed) { return; }
    var o = hero.getCameraOrbit();
    hero.cameraOrbit = o.theta + "rad " + o.phi + "rad " + (base.radius * (1 + (RADIUS_FACTOR - 1) * t)) + "m";
    hero.cameraTarget = base.x + "m " + (base.y + RISE * t) + "m " + base.z + "m";
  }

  function syncPresets() {
    presets.forEach(function (b) {
      b.setAttribute("aria-pressed", String(parseFloat(b.getAttribute("data-explode")) === t));
    });
  }

  function tweenTo(target) {
    cancelAnimationFrame(raf);
    if (reduce) { t = target; range.value = t * 1000; apply(); syncPresets(); return; }
    var from = t, start = performance.now(), dur = 900;
    (function step(now) {
      var k = Math.min(1, (now - start) / dur);
      var e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      t = from + (target - from) * e;
      range.value = t * 1000;
      apply();
      syncPresets();
      if (k < 1) { raf = requestAnimationFrame(step); }
    })(start);
  }

  hero.addEventListener("load", function () {
    if (!base) {   // framing of the assembled model, measured once: both variants share the same envelope
      var tg = hero.getCameraTarget();
      base = { radius: hero.getCameraOrbit().radius, x: tg.x, y: tg.y, z: tg.z };
    }
    if (savedOrbit) {   // keep the visitor's viewing angle when the battery variant changes
      hero.cameraOrbit = savedOrbit.theta + "rad " + savedOrbit.phi + "rad " + base.radius + "m";
      hero.jumpCameraToGoal();
      savedOrbit = null;
    }
    apply();
  });
  // once the visitor zooms by hand, stop moving the camera for them
  hero.addEventListener("wheel", function () { userZoomed = true; }, { passive: true });
  hero.addEventListener("touchstart", function (e) { if (e.touches.length > 1) { userZoomed = true; } }, { passive: true });

  range.addEventListener("input", function () {
    cancelAnimationFrame(raf);
    t = range.value / 1000;
    apply();
    syncPresets();
  });
  presets.forEach(function (b) {
    b.addEventListener("click", function () { tweenTo(parseFloat(b.getAttribute("data-explode"))); });
  });

  // battery variant: each one is its own GLB (own PCB, cells and interior accessory)
  variants.forEach(function (b) {
    b.addEventListener("click", function () {
      var src = "/enclosure/enclosure-" + b.getAttribute("data-variant") + ".glb";
      if (hero.getAttribute("src") === src) { return; }
      savedOrbit = hero.getCameraOrbit();
      hero.setAttribute("src", src);
      variants.forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
      if (note) { note.textContent = b.getAttribute("data-note"); }
    });
  });
})();

// Hero: try your own colours. Materials are named by role in the GLB ("body", "accent", "mount").
(function () {
  var hero = document.getElementById("encl-hero");
  var swatches = document.querySelectorAll(".encl-sw");
  if (!hero || !swatches.length) { return; }
  var chosen = {};

  function paint() {
    if (!hero.model) { return; }
    hero.model.materials.forEach(function (m) {
      if (chosen[m.name]) { m.pbrMetallicRoughness.setBaseColorFactor(chosen[m.name]); }
    });
  }
  hero.addEventListener("load", paint);   // the battery variants are separate files: repaint after each load

  swatches.forEach(function (b) {
    b.addEventListener("click", function () {
      var role = b.getAttribute("data-role"), color = b.getAttribute("data-color");
      chosen[role] = color;
      b.parentNode.querySelectorAll(".encl-sw").forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
      var legend = document.getElementById("lg-" + role);
      if (legend) { legend.style.background = color; }
      paint();
    });
  });
})();
