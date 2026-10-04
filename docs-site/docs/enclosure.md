# 2. The Enclosure

The ISURLOG enclosure holds the datalogger, its batteries and the wiring in a single 3D-printed box, designed by ISURKI and printed in PETG. The lid closes with four captive quarter-turn closures, and a groove takes a Ø3 mm silicone cord gasket. Inside, you fit either a WAGO rail for the connections or a holder for two ER34615 cells, depending on the battery type. Outside, it mounts on a wall, on a DIN rail or on a pole. Rotate it, zoom in and take it apart below.

## 2.1 Overview

<div class="encl">
  <div class="encl-stage">
    <div class="encl-opts">
      <span>Battery</span>
      <div class="encl-seg encl-seg-inline" role="group" aria-label="Battery">
        <button type="button" aria-pressed="true" data-variant="liion" data-note="Main PCB with on-board cell holders (18650 cells) and the WAGO rail.">Li-ion<small>rechargeable</small></button>
        <button type="button" aria-pressed="false" data-variant="lisocl2" data-note="Main PCB without on-board cell holders, plus the battery holder with two ER34615 cells.">Li-SOCl₂<small>non-rechargeable</small></button>
      </div>
    </div>
    <div class="encl-canvas">
      <model-viewer id="encl-hero" src="/enclosure/enclosure-liion.glb" alt="3D model of the ISURLOG enclosure" animation-name="explode" camera-controls touch-action="pan-y" auto-rotate auto-rotate-delay="3000" rotation-per-second="12deg" camera-orbit="-35deg 68deg 105%" min-camera-orbit="auto auto 0.12m" max-camera-orbit="auto auto 2m" environment-image="neutral" shadow-intensity="0.8" shadow-softness="0.9" exposure="0.7" loading="lazy"></model-viewer>
      <div class="encl-seg" role="group" aria-label="View">
        <button type="button" aria-pressed="true" data-explode="0">Assembled</button>
        <button type="button" aria-pressed="false" data-explode="1">Exploded</button>
      </div>
      <span class="encl-hint">Drag to rotate · scroll or pinch to zoom</span>
    </div>
    <div class="encl-bar">
      <span>Assembled</span>
      <input type="range" class="encl-range" id="encl-range" min="0" max="1000" value="0" aria-label="Assemble or take apart the enclosure">
      <span>Exploded</span>
    </div>
  </div>
  <p class="encl-note" id="encl-note">Main PCB with on-board cell holders (18650 cells) and the WAGO rail.</p>
  <div class="encl-colors">
    <span class="encl-colors-label">Try your colours</span>
    <div class="encl-swatches" role="group" aria-label="Box and lid"><small>Box and lid</small><button type="button" class="encl-sw" data-role="body" data-color="#EDE6CC" style="--c:#EDE6CC" aria-label="Ivory" aria-pressed="true"></button><button type="button" class="encl-sw" data-role="body" data-color="#F2F2F0" style="--c:#F2F2F0" aria-label="White" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="body" data-color="#9AA0A6" style="--c:#9AA0A6" aria-label="Grey" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="body" data-color="#E8782A" style="--c:#E8782A" aria-label="Orange" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="body" data-color="#2E6DB4" style="--c:#2E6DB4" aria-label="Blue" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="body" data-color="#2B2B2E" style="--c:#2B2B2E" aria-label="Black" aria-pressed="false"></button></div>
    <div class="encl-swatches" role="group" aria-label="Closures, screwdriver and inner accessories"><small>Closures, screwdriver and inner accessories</small><button type="button" class="encl-sw" data-role="accent" data-color="#00A838" style="--c:#00A838" aria-label="Green" aria-pressed="true"></button><button type="button" class="encl-sw" data-role="accent" data-color="#F28C28" style="--c:#F28C28" aria-label="Orange" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="accent" data-color="#2E6DB4" style="--c:#2E6DB4" aria-label="Blue" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="accent" data-color="#C8372D" style="--c:#C8372D" aria-label="Red" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="accent" data-color="#E8C21A" style="--c:#E8C21A" aria-label="Yellow" aria-pressed="false"></button><button type="button" class="encl-sw" data-role="accent" data-color="#F2F2F0" style="--c:#F2F2F0" aria-label="White" aria-pressed="false"></button></div>
  </div>
  <div class="encl-legend">
    <span><i id="lg-body" style="background:#EDE6CC"></i>Box, lid and cover screw</span>
    <span><i id="lg-accent" style="background:#00A838"></i>Closures, screwdriver, lid cover and interior accessories</span>
    <span><i style="background:#0F522B"></i>Main PCB</span>
    <span><i style="background:#2F6FB8"></i>Batteries</span>
    <span><i style="background:#212124"></i>Mounting brackets</span>
  </div>
</div>

## 2.2 The pieces

Pick a piece to inspect it. Each one can be rotated and zoomed.

<div class="encl">
  <div class="encl-stage is-short">
    <model-viewer id="encl-part" src="/enclosure/parts/box.glb" alt="3D model of the selected enclosure piece" camera-controls touch-action="pan-y" auto-rotate rotation-per-second="14deg" camera-orbit="-35deg 68deg auto" environment-image="neutral" shadow-intensity="0.8" shadow-softness="0.9" exposure="0.7" loading="lazy"></model-viewer>
    <span class="encl-hint">Drag to rotate · scroll or pinch to zoom</span>
  </div>
  <div class="encl-parts" role="group" aria-label="Pieces">
    <button type="button" class="encl-part" aria-pressed="true" data-viewer="encl-part" data-src="/enclosure/parts/box.glb" data-panel="p-box">Box<small>× 1</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/lid.glb" data-panel="p-lid">Lid and closures<small>× 1 + 4</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/cover.glb" data-panel="p-cover">Lid cover<small>× 1 + screw</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/key.glb" data-panel="p-key">Screwdriver<small>× 1</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/wago.glb" data-panel="p-wago">WAGO rail<small>optional</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/battery.glb" data-panel="p-battery">Battery holder<small>optional</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/din.glb" data-panel="p-din">DIN rail mount<small>optional</small></button>
    <button type="button" class="encl-part" aria-pressed="false" data-viewer="encl-part" data-src="/enclosure/parts/pole.glb" data-panel="p-pole">Pole mount<small>optional</small></button>
  </div>

  <div class="encl-info" id="p-box">
    <h3>Box</h3>
    <p>The main body. It carries the L-shaped anchors that hold the interior accessories, the PCB standoffs, the C-ring on the front where the screwdriver is stored, and five M12 holes for cable glands on the rear wall (four in the upper row and one in the lower row).</p>
    <dl><dt>Quantity</dt><dd>1</dd><dt>Material</dt><dd>PETG</dd></dl>
  </div>
  <div class="encl-info" id="p-lid" hidden>
    <h3>Lid and closures</h3>
    <p>The lid has the gasket groove, a housing for the magnet, a frame for the desiccant and a recess for the label. The four quarter-turn closures are printed already assembled (print in place) and stay captive in the lid, so they cannot be lost, for example in an inspection chamber.</p>
    <dl><dt>Quantity</dt><dd>1 lid + 4 closures</dd><dt>Material</dt><dd>PETG</dd><dt>Gasket</dt><dd>Ø3 mm silicone cord (not printed)</dd></dl>
  </div>
  <div class="encl-info" id="p-cover" hidden>
    <h3>Lid cover</h3>
    <p>It sits under the lid and is held to the lid's central bushing by a quarter-turn screw.</p>
    <dl><dt>Quantity</dt><dd>1 cover + 1 screw</dd></dl>
  </div>
  <div class="encl-info" id="p-key" hidden>
    <h3>Screwdriver</h3>
    <p>It turns the quarter-turn closures. It is stored snapped into the C-ring on the front of the box, so it always travels with the enclosure.</p>
    <dl><dt>Quantity</dt><dd>1</dd></dl>
  </div>
  <div class="encl-info" id="p-wago" hidden>
    <h3>WAGO rail</h3>
    <p>A rail for WAGO 221 connectors. It snaps into the L-shaped anchors of the box. It uses the same holes as the battery holder, so you fit one or the other.</p>
    <dl><dt>Quantity</dt><dd>1 (alternative to the battery holder)</dd></dl>
  </div>
  <div class="encl-info" id="p-battery" hidden>
    <h3>Battery holder (2 × ER34615)</h3>
    <p>A base plus a clamp with the two cradles: the clamp's legs go through slots in the base and hook on top. It uses the same holes as the WAGO rail, so you fit one or the other.</p>
    <dl><dt>Quantity</dt><dd>1 base + 1 clamp (alternative to the WAGO rail)</dd></dl>
  </div>
  <div class="encl-info" id="p-din" hidden>
    <h3>DIN rail mount</h3>
    <p>A plate with a spring latch, printed in place. It is fixed to the base of the box with M6 stainless-steel bolts and nuts; the nuts sit in hexagonal pockets in the mount.</p>
    <dl><dt>Quantity</dt><dd>1</dd></dl>
  </div>
  <div class="encl-info" id="p-pole" hidden>
    <h3>Pole mount</h3>
    <p>Fixed to the base of the box with M6 stainless-steel bolts and nuts. Two mounts are printed per enclosure, plus four spacer cylinders (two per mount). The cylinders have two hole positions, the inner one for thin poles. The model shows one mount and one cylinder.</p>
    <dl><dt>Quantity</dt><dd>2 mounts + 4 cylinders</dd></dl>
  </div>
</div>

## 2.3 Assembly and use

<div class="encl">
  <div class="encl-videos">
    <figure><a class="glightbox" href="/enclosure/video/01-overview.mp4" data-type="video" data-title="Overview" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/01-overview.mp4" type="video/mp4"></video></a><figcaption><b>Overview</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/02-open-close.mp4" data-type="video" data-title="Opening and closing" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/02-open-close.mp4" type="video/mp4"></video></a><figcaption><b>Opening and closing</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/03-cover.mp4" data-type="video" data-title="Lid cover" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/03-cover.mp4" type="video/mp4"></video></a><figcaption><b>Lid cover</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/04-wago.mp4" data-type="video" data-title="WAGO rail" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/04-wago.mp4" type="video/mp4"></video></a><figcaption><b>WAGO rail</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/05-battery.mp4" data-type="video" data-title="Battery holder" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/05-battery.mp4" type="video/mp4"></video></a><figcaption><b>Battery holder</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/06-din.mp4" data-type="video" data-title="DIN rail mount" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/06-din.mp4" type="video/mp4"></video></a><figcaption><b>DIN rail mount</b></figcaption></figure>
    <figure><a class="glightbox" href="/enclosure/video/07-pole.mp4" data-type="video" data-title="Pole mount" data-desc-position="bottom"><video autoplay loop muted playsinline preload="metadata"><source src="/enclosure/video/07-pole.mp4" type="video/mp4"></video></a><figcaption><b>Pole mount</b></figcaption></figure>
  </div>
</div>

Click a video to enlarge it.

## 2.4 Why a printed enclosure

A printed enclosure is not a compromise. It allows things that are hard to do with an injection-moulded box, and it puts the design in your hands.

### 2.4.1 Make it yours

<div class="grid cards" markdown>

- **Your colours and your logo.** Print the box, the closures and the mounts in any filament colour: match your brand or colour-code your installations. The lid already has a recess for a label, and with the STL files you can add your logo or an identification number using your slicer or any 3D modelling tool. Try the colours on the model in [2.1](#21-overview).
- **Your own parts.** The WAGO rail and the battery holder are built on the same frame and use the same anchors in the box, so an interior accessory of your own can use them too.
- **Your own openings.** The box already has five M12 holes for cable glands on the rear wall (four in the upper row and one in the lower row). If you need more, or other sizes, you can add your own with your slicer or any 3D modelling tool. Every opening has to be sealed, with a cable gland or a blind plug, including the ones you do not use.
- **Your own material.** The base material is PETG, but you can experiment: ASA, or filaments reinforced with glass or carbon fibre, if your installation environment is more demanding. Reinforced filaments are abrasive and need a hardened nozzle. The print-in-place clearance is worth checking again with any new material. Filaments that conduct electricity, such as some carbon-fibre or metal-filled ones, can weaken the signal of the antennas inside the box. Check the signal quality after changing material.
- **Mods and remixes.** You can modify the parts for your own use. If you share a modification, credit ISURKI, say what you changed and use the same license ([2.5.3](#253-license)).

</div>

### 2.4.2 Easy to keep running

<div class="grid cards" markdown>

- **Repairable.** A broken piece is a print job, not a spare-parts order. Reprint it and swap it.
- **Closures that cannot get lost.** The four quarter-turn closures are printed already assembled and stay captive in the lid.
- **Modular.** Wall, DIN rail or pole outside; WAGO rail or battery holder inside. The same box in every case.

</div>

## 2.5 Print it yourself

!!! success "Available on MakerWorld"
    The files (STL and ready-to-print Bambu Studio projects) are published on [MakerWorld](https://makerworld.com/es/models/3392577-isurlog-enclosure-iot-datalogger-ip66-box#profileId-3861558){ target="_blank" rel="noopener" } under the license described in [2.5.3](#253-license).

### 2.5.1 Print projects

The print settings come inside Bambu Studio projects, so there is no list of settings to copy. Choose the one that matches where the enclosure will live:

| Where it will live | Project | Status |
| :--- | :--- | :--- |
| **Sheltered**, for example inside a building | **Indoor** | Ready |
| **Outdoors or adverse weather** (water, sun) | **Outdoor**. The box, the lid and the closures printed with it are the parts that keep water and dust out, so this project prints them with a more demanding profile | Ready |

The projects are set up for a Bambu Lab P2S with a 0.4 mm nozzle and Sunlu PETG, with one plate per part: box, lid with closures, lid cover, lid cover screw, screwdriver, WAGO rail, battery holder, DIN mount and pole mount. With another printer or filament, open the project in Bambu Studio, choose yours, slice again and check each plate before printing.

### 2.5.2 Before you print

* **Hardware that is not printed.**
    * Silicone cord gasket, Ø3 mm.
    * M6 × 15 mm stainless-steel screws and nuts for the mounts, 4 per mount.
    * A magnet, Ø18 × 4 mm, for the housing in the lid.
* **Print in place.** The closures and the DIN latch are printed already assembled, with a 0.2 mm clearance. Your printer has to hold that clearance without fusing the parts together.
* **Material.** PETG; the projects are set up for [Sunlu PETG](https://i.refs.cc/uja9Haai){ target="_blank" rel="sponsored nofollow noopener" }. Other materials are possible (see [2.4.1](#241-make-it-yours)); the same brand also makes PETG-CF and ASA. The print settings are already in the projects of [2.5.1](#251-print-projects). *(Referral link: buying through it supports the project.)*
* **Warranty.** If you fit the ISURLOG in an enclosure that ISURKI did not supply, the warranty on the electronics stays in force. Only failures caused by that enclosure are excluded, for example water or dust getting in and damaging the board.

### 2.5.3 License

The files are licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). In addition, ISURKI allows, free of charge:

* printing the parts for ISURLOG devices that you own or operate, for personal or business use;
* professionals servicing customers' ISURLOG devices to print and fit the parts and charge for their work, but not for the printed parts as products on their own;
* modifying the parts for those uses. If you share a modification, credit ISURKI, say what you changed and use the same license.

Selling printed parts, enclosures or kits, or selling the files, needs a commercial license: write to [tecnica@isurki.com](mailto:tecnica@isurki.com). The names and logos ISURKI and ISURLOG are not covered by the license.

<link rel="stylesheet" href="/enclosure/enclosure.css">
<script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@4.3.1/dist/model-viewer.min.js"></script>
<script src="/enclosure/viewer.js" defer></script>
