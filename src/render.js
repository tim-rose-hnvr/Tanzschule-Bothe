/**
 * Renderqualität: Himmel, Umgebungsreflexion, Umgebungsverdeckung (GTAO)
 * und Kantenglättung. Alles über eine Qualitätsstufe schaltbar, damit das
 * Modell auch auf schwächerer Hardware flüssig bleibt.
 */
import * as THREE from 'three';
import { Sky } from '../vendor/three-addons/objects/Sky.js';
import { EffectComposer } from '../vendor/three-addons/postprocessing/EffectComposer.js';
import { RenderPass } from '../vendor/three-addons/postprocessing/RenderPass.js';
import { OutputPass } from '../vendor/three-addons/postprocessing/OutputPass.js';
import { GTAOPass } from '../vendor/three-addons/postprocessing/GTAOPass.js';

/**
 * Sonnenstand: Nachmittagssonne aus Südwesten – wie auf den Fotos.
 * Azimut folgt der Konvention des Sky-Shaders: theta = 0 zeigt nach +Z.
 * In der Modellwelt ist +Z Süden, -X Westen, ein Südwest-Stand liegt also
 * bei 315°. (Ein Wert um 180° würde die Sonne in den Norden setzen.)
 */
export const SONNE = { hoehe: 40, azimut: 313 };

export function sonnenRichtung(entfernung = 100) {
  const phi = THREE.MathUtils.degToRad(90 - SONNE.hoehe);
  const theta = THREE.MathUtils.degToRad(SONNE.azimut);
  return new THREE.Vector3().setFromSphericalCoords(entfernung, phi, theta);
}

/* ------------------------------------------------------------ Himmel */

/**
 * Der Himmel wird einmalig in eine Cubemap gerendert und daraus sowohl der
 * Hintergrund als auch die Umgebungsreflexion abgeleitet. Vorteil gegenüber
 * einer riesigen Himmelskugel in der Szene: die Fernebene der Kamera bleibt
 * klein, was der Tiefengenauigkeit und damit der Umgebungsverdeckung zugute
 * kommt.
 */
export function baueHimmel(scene, renderer) {
  const himmelSzene = new THREE.Scene();
  const sky = new Sky();
  sky.scale.setScalar(90);
  const u = sky.material.uniforms;
  u.turbidity.value = 4.5;
  u.rayleigh.value = 1.35;
  u.mieCoefficient.value = 0.004;
  u.mieDirectionalG.value = 0.82;
  u.sunPosition.value.copy(sonnenRichtung(1).normalize());
  himmelSzene.add(sky);

  const cubeZiel = new THREE.WebGLCubeRenderTarget(512, { type: THREE.HalfFloatType });
  const cubeKamera = new THREE.CubeCamera(0.1, 200, cubeZiel);
  cubeKamera.update(renderer, himmelSzene);
  scene.background = cubeZiel.texture;
  scene.backgroundIntensity = 1.0;

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromCubemap(cubeZiel.texture).texture;
  scene.environmentIntensity = 0.9;
  pmrem.dispose();

  sky.geometry.dispose();
  return cubeZiel.texture;
}

/* ------------------------------------------------ Nachbearbeitungskette */

export const STUFEN = ['hoch', 'mittel', 'aus'];

export class Bildkette {
  constructor(renderer, scene, camera) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    this.stufe = 'hoch';
    this.composer = null;
    this.gtao = null;
    this._baue();
  }

  _baue() {
    const { renderer, scene, camera } = this;
    const gr = renderer.getSize(new THREE.Vector2());

    const ziel = new THREE.WebGLRenderTarget(gr.x, gr.y, {
      type: THREE.HalfFloatType,
      samples: 4,                       // Mehrfachabtastung statt separatem AA-Pass
    });
    const composer = new EffectComposer(renderer, ziel);
    composer.addPass(new RenderPass(scene, camera));

    const gtao = new GTAOPass(scene, camera, gr.x, gr.y);
    gtao.output = GTAOPass.OUTPUT.Default;
    gtao.updateGtaoMaterial({
      radius: 1.6,            // Meter – passend zum Gebäudemaßstab
      distanceExponent: 1.0,
      thickness: 1.4,
      scale: 1.05,
      samples: 16,
      distanceFallOff: 1.0,
      screenSpaceRadius: false,
    });
    gtao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 4, samples: 16 });
    gtao.blendIntensity = 0.9;
    composer.addPass(gtao);
    composer.addPass(new OutputPass());

    this.composer = composer;
    this.gtao = gtao;
  }

  setStufe(stufe) {
    this.stufe = stufe;
    if (this.gtao) this.gtao.enabled = stufe === 'hoch';
    // Mehrfachabtastung bleibt auch auf "mittel" aktiv, sie ist günstig.
    // "aus" umgeht die Kette und verzichtet zusätzlich auf die
    // Überabtastung – das ist der eigentliche Sparhebel.
    this.renderer.setPixelRatio(stufe === 'aus'
      ? Math.min(devicePixelRatio, 1)
      : Math.min(Math.max(devicePixelRatio, 1.5), 2));
  }

  setGroesse(w, h) {
    this.composer.setSize(w, h);
    this.gtao.setSize(w, h);
  }

  render() {
    if (this.stufe === 'aus') this.renderer.render(this.scene, this.camera);
    else this.composer.render();
  }
}

/* ------------------------------------------------- Automatische Stufe */

/**
 * Beobachtet die ersten Sekunden und stuft herunter, wenn die Bildrate
 * einbricht. Meldet jede Änderung über `onWechsel`.
 */
export class Leistungswaechter {
  constructor(kette, onWechsel) {
    this.kette = kette;
    this.onWechsel = onWechsel;
    this.proben = [];
    this.fertig = false;
  }

  tick(dt) {
    if (this.fertig) return;
    this.proben.push(dt);
    if (this.proben.length < 90) return;
    const mittel = this.proben.slice(30).reduce((a, b) => a + b, 0) / (this.proben.length - 30);
    const fps = 1 / mittel;
    this.proben.length = 0;
    if (fps < 24 && this.kette.stufe === 'hoch') this._wechsle('mittel');
    else if (fps < 20 && this.kette.stufe === 'mittel') this._wechsle('aus');
    else this.fertig = true;
  }

  _wechsle(stufe) {
    this.kette.setStufe(stufe);
    this.onWechsel?.(stufe);
    if (stufe === 'aus') this.fertig = true;
  }
}
