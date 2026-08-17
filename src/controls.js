/**
 * Kamerasteuerung: Umkreisen (Orbit) und Begehen (First Person).
 * Bewusst eigenständig implementiert, damit keine three.js-Addons
 * nachgeladen werden müssen und die Datei offline lauffähig bleibt.
 */
import * as THREE from 'three';

const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp  = (a, b, t) => a + (b - a) * t;

export class Steuerung {
  constructor(camera, dom) {
    this.cam = camera;
    this.dom = dom;
    this.modus = 'orbit';

    // Orbit-Zustand (Kugelkoordinaten um `ziel`)
    this.ziel = new THREE.Vector3(15, 3, -15);
    this.zielSoll = this.ziel.clone();
    this.radius = 62; this.radiusSoll = 62;
    this.theta = -0.85; this.thetaSoll = -0.85;   // Azimut
    this.phi = 0.95;    this.phiSoll = 0.95;      // Polar
    this.minRadius = 4; this.maxRadius = 160;

    // Begehen-Zustand
    this.pos = new THREE.Vector3(17.3, 1.65, 6.0);
    this.yaw = Math.PI; this.pitch = 0;
    this.tasten = new Set();
    this.augenhoehe = 1.65;
    this.etageBasis = 0;

    this.anim = null;          // laufende Kamerafahrt
    this._bind();
  }

  /* ------------------------------------------------------------- Eingabe */
  _bind() {
    const d = this.dom;
    let drag = null, letzte = null, pinch = 0;

    d.addEventListener('contextmenu', e => e.preventDefault());

    d.addEventListener('pointerdown', e => {
      if (e.button === 1) return;
      d.setPointerCapture(e.pointerId);
      drag = { x: e.clientX, y: e.clientY, btn: e.button, moved: 0 };
      this.anim = null;
    });

    d.addEventListener('pointermove', e => {
      if (!drag) return;
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      drag.x = e.clientX; drag.y = e.clientY;
      drag.moved += Math.abs(dx) + Math.abs(dy);
      if (this.modus === 'orbit') {
        if (drag.btn === 2 || e.shiftKey) this._pan(dx, dy);
        else { this.thetaSoll -= dx * 0.006; this.phiSoll = clamp(this.phiSoll - dy * 0.006, 0.06, 1.54); }
      } else {
        this.yaw -= dx * 0.0035;
        this.pitch = clamp(this.pitch - dy * 0.0032, -1.3, 1.3);
      }
    });

    const up = e => {
      if (drag && drag.moved < 6 && this.onKlick) this.onKlick(e);
      drag = null;
    };
    d.addEventListener('pointerup', up);
    d.addEventListener('pointercancel', () => { drag = null; });

    d.addEventListener('wheel', e => {
      e.preventDefault();
      this.anim = null;
      if (this.modus === 'orbit') {
        this.radiusSoll = clamp(this.radiusSoll * (1 + Math.sign(e.deltaY) * 0.11), this.minRadius, this.maxRadius);
      } else {
        const f = new THREE.Vector3(Math.sin(this.yaw), 0, Math.cos(this.yaw));
        this.pos.addScaledVector(f, -Math.sign(e.deltaY) * 1.2);
      }
    }, { passive: false });

    // Zwei-Finger-Zoom
    const touches = new Map();
    d.addEventListener('touchstart', e => { for (const t of e.changedTouches) touches.set(t.identifier, t); }, { passive: true });
    d.addEventListener('touchmove', e => {
      if (e.touches.length === 2) {
        const [a, b] = e.touches;
        const dist = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
        if (pinch) this.radiusSoll = clamp(this.radiusSoll * (pinch / dist), this.minRadius, this.maxRadius);
        pinch = dist;
      }
    }, { passive: true });
    d.addEventListener('touchend', () => { pinch = 0; });

    addEventListener('keydown', e => {
      if (e.target.tagName === 'INPUT') return;
      this.tasten.add(e.code);
      if (this.modus === 'walk' && ['KeyW','KeyA','KeyS','KeyD','Space'].includes(e.code)) e.preventDefault();
    });
    addEventListener('keyup', e => this.tasten.delete(e.code));
    addEventListener('blur', () => this.tasten.clear());
  }

  _pan(dx, dy) {
    const s = this.radius * 0.0016;
    const rechts = new THREE.Vector3(Math.cos(this.theta), 0, -Math.sin(this.theta));
    const vor = new THREE.Vector3(Math.sin(this.theta), 0, Math.cos(this.theta));
    this.zielSoll.addScaledVector(rechts, -dx * s).addScaledVector(vor, -dy * s);
  }

  /* --------------------------------------------------------------- Modus */
  setModus(m) {
    if (m === this.modus) return;
    if (m === 'walk') {
      this.pos.copy(this.cam.position);
      this.pos.y = this.etageBasis + this.augenhoehe;
      const dir = new THREE.Vector3().subVectors(this.ziel, this.cam.position);
      this.yaw = Math.atan2(dir.x, dir.z);
      this.pitch = 0;
    } else {
      this.zielSoll.set(
        this.pos.x + Math.sin(this.yaw) * 12, 2,
        this.pos.z + Math.cos(this.yaw) * 12);
      this.ziel.copy(this.zielSoll);
      this.radiusSoll = this.radius = 34;
      this.thetaSoll = this.theta = this.yaw + Math.PI;
      this.phiSoll = this.phi = 1.15;
    }
    this.modus = m;
  }

  /** Weiche Kamerafahrt zu Position/Ziel (Weltkoordinaten) */
  flyTo(camPos, lookAt, dauer = 1100) {
    if (this.modus === 'walk') this.setModus('orbit');
    const p = new THREE.Vector3(...camPos), z = new THREE.Vector3(...lookAt);
    const d = new THREE.Vector3().subVectors(p, z);
    this.anim = {
      t0: performance.now(), dauer,
      von: { r: this.radius, th: this.theta, ph: this.phi, z: this.ziel.clone() },
      nach: {
        r: d.length(),
        th: Math.atan2(d.x, d.z),
        ph: Math.acos(clamp(d.y / d.length(), -1, 1)),
        z,
      },
    };
    // kürzesten Weg um den Kreis wählen
    let dth = this.anim.nach.th - this.anim.von.th;
    while (dth > Math.PI) dth -= Math.PI * 2;
    while (dth < -Math.PI) dth += Math.PI * 2;
    this.anim.nach.th = this.anim.von.th + dth;
  }

  /* -------------------------------------------------------------- Update */
  update(dt) {
    if (this.anim) {
      const t = Math.min(1, (performance.now() - this.anim.t0) / this.anim.dauer);
      const e = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      const { von, nach } = this.anim;
      this.radiusSoll = this.radius = lerp(von.r, nach.r, e);
      this.thetaSoll = this.theta = lerp(von.th, nach.th, e);
      this.phiSoll = this.phi = lerp(von.ph, nach.ph, e);
      this.ziel.lerpVectors(von.z, nach.z, e);
      this.zielSoll.copy(this.ziel);
      if (t >= 1) this.anim = null;
    }

    if (this.modus === 'orbit') {
      const k = 1 - Math.pow(0.001, dt);
      this.radius = lerp(this.radius, this.radiusSoll, k);
      this.theta  = lerp(this.theta,  this.thetaSoll,  k);
      this.phi    = lerp(this.phi,    this.phiSoll,    k);
      this.ziel.lerp(this.zielSoll, k);
      const sp = Math.sin(this.phi);
      this.cam.position.set(
        this.ziel.x + this.radius * sp * Math.sin(this.theta),
        Math.max(0.6, this.ziel.y + this.radius * Math.cos(this.phi)),
        this.ziel.z + this.radius * sp * Math.cos(this.theta));
      this.cam.lookAt(this.ziel);
    } else {
      const speed = (this.tasten.has('ShiftLeft') ? 9 : 4.2) * dt;
      const vor = new THREE.Vector3(Math.sin(this.yaw), 0, Math.cos(this.yaw));
      const rechts = new THREE.Vector3(Math.cos(this.yaw), 0, -Math.sin(this.yaw));
      if (this.tasten.has('KeyW') || this.tasten.has('ArrowUp'))    this.pos.addScaledVector(vor, speed);
      if (this.tasten.has('KeyS') || this.tasten.has('ArrowDown'))  this.pos.addScaledVector(vor, -speed);
      if (this.tasten.has('KeyA') || this.tasten.has('ArrowLeft'))  this.pos.addScaledVector(rechts, -speed);
      if (this.tasten.has('KeyD') || this.tasten.has('ArrowRight')) this.pos.addScaledVector(rechts, speed);
      if (this.tasten.has('KeyQ')) this.pos.y -= speed;
      if (this.tasten.has('KeyE')) this.pos.y += speed;
      this.pos.y = lerp(this.pos.y, Math.max(this.pos.y, this.etageBasis + this.augenhoehe * 0.4), 0.2);
      this.cam.position.copy(this.pos);
      const d = new THREE.Vector3(
        Math.sin(this.yaw) * Math.cos(this.pitch),
        Math.sin(this.pitch),
        Math.cos(this.yaw) * Math.cos(this.pitch));
      this.cam.lookAt(this.pos.clone().add(d));
    }
  }
}
