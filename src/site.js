/**
 * Außenanlagen – Garten, Terrasse, Parkplatz, Zaun, Bäume, Beschilderung.
 * Grundlage sind ausschließlich die sechs Fotos aus dem Drive-Ordner;
 * in den Grundriss-Renderings sind diese Bereiche nicht enthalten.
 */
import * as THREE from 'three';
import { H } from './data.js';
import { boxMesh, cyl } from './props.js';
import { schildTextur, steleTextur } from './materials.js';

const rnd = (seed => () => (seed = (seed * 48271) % 2147483647) / 2147483647)(7761);

/* ------------------------------------------------------------- Bauteile */

function liegestuhl(g, M, x, y, rot) {
  const s = new THREE.Group();
  const stoff = new THREE.Mesh(new THREE.BoxGeometry(0.60, 0.03, 1.15), M.rot);
  stoff.position.set(0, 0.44, 0); stoff.rotation.x = -0.55; stoff.castShadow = true;
  s.add(stoff);
  for (const [dx, dz, ang] of [[-0.31, 0, 0.5], [0.31, 0, 0.5], [-0.31, 0, -0.5], [0.31, 0, -0.5]]) {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.85, 0.04), M.schwarz);
    leg.position.set(dx, 0.30, dz); leg.rotation.x = ang; s.add(leg);
  }
  s.position.set(x, 0, -y); s.rotation.y = rot;
  g.add(s);
}

function biertisch(g, M, x, y, rot) {
  const s = new THREE.Group();
  s.add(boxMesh(0.72, 0.05, 2.20, M.grau, 0, 0.76, 0));
  for (const dz of [-0.9, 0.9]) {
    s.add(boxMesh(0.06, 0.74, 0.06, M.grauDunkel, -0.30, 0.38, dz));
    s.add(boxMesh(0.06, 0.74, 0.06, M.grauDunkel,  0.30, 0.38, dz));
  }
  for (const dx of [-0.62, 0.62]) {
    s.add(boxMesh(0.28, 0.05, 2.20, M.grau, dx, 0.46, 0));
    for (const dz of [-0.85, 0.85]) s.add(boxMesh(0.05, 0.44, 0.05, M.grauDunkel, dx, 0.23, dz));
  }
  s.position.set(x, 0, -y); s.rotation.y = rot;
  g.add(s);
}

function sonnenschirm(g, M, x, y, r = 2.4) {
  g.add(cyl(0.06, 2.55, M.grauDunkel, x, 1.27, -y, 10));
  const top = new THREE.Mesh(new THREE.ConeGeometry(r, 0.55, 4), M.rot);
  top.position.set(x, 2.70, -y); top.rotation.y = Math.PI / 4; top.castShadow = true;
  g.add(top);
  g.add(boxMesh(0.55, 0.10, 0.55, M.schwarz, x, 0.05, -y));
}

function palme(g, M, x, y, hoehe = 3.4) {
  const st = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.24, hoehe, 9), M.stamm);
  st.position.set(x, hoehe / 2, -y); st.castShadow = true;
  g.add(st);
  for (let i = 0; i < 9; i++) {
    const a = (i / 9) * Math.PI * 2 + rnd();
    const wedel = new THREE.Mesh(new THREE.ConeGeometry(0.26, 1.9, 4), M.gruenD);
    wedel.position.set(x + Math.cos(a) * 0.85, hoehe + 0.15 - (i % 3) * 0.14, -y + Math.sin(a) * 0.85);
    wedel.rotation.set(Math.PI / 2.35, 0, -a + Math.PI / 2);
    wedel.castShadow = true;
    g.add(wedel);
  }
}

function baum(g, M, x, y, h = 8) {
  const st = new THREE.Mesh(new THREE.CylinderGeometry(0.20, 0.34, h * 0.55, 8), M.stamm);
  st.position.set(x, h * 0.275, -y); g.add(st);
  for (let i = 0; i < 4; i++) {
    const k = new THREE.Mesh(new THREE.IcosahedronGeometry(h * 0.26, 0), i % 2 ? M.gruen : M.gruenD);
    k.position.set(x + (rnd() - 0.5) * h * 0.28, h * 0.55 + rnd() * h * 0.26, -y + (rnd() - 0.5) * h * 0.28);
    k.castShadow = true;
    g.add(k);
  }
}

function zaun(g, M, ax, ay, bx, by) {
  const len = Math.hypot(bx - ax, by - ay);
  const n = Math.round(len / 0.14);
  const ry = Math.atan2(bx - ax, -(by - ay)) + Math.PI / 2;
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    g.add(boxMesh(0.035, 1.85, 0.035, M.grau, ax + (bx - ax) * t, 0.93, -(ay + (by - ay) * t)));
  }
  for (const hgt of [0.12, 1.80]) {
    const r = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.06, len), M.grau);
    r.position.set((ax + bx) / 2, hgt, -(ay + by) / 2); r.rotation.y = ry;
    g.add(r);
  }
  for (let i = 0; i <= Math.round(len / 2.6); i++) {
    const t = i / Math.max(1, Math.round(len / 2.6));
    g.add(boxMesh(0.10, 1.95, 0.10, M.grauDunkel, ax + (bx - ax) * t, 0.98, -(ay + (by - ay) * t)));
  }
}

/* ---------------------------------------------------------- Beschilderung */

function beschilderung(g, M) {
  // Leuchtschrift über dem Haupteingang (Südfassade)
  const schild = new THREE.Mesh(
    new THREE.PlaneGeometry(5.4, 1.7),
    new THREE.MeshStandardMaterial({ map: schildTextur(), transparent: true,
      emissive: 0xffffff, emissiveIntensity: 0.28, roughness: 0.6 }));
  schild.position.set(21.4, 5.5, 0.20);
  schild.rotation.y = Math.PI;
  g.add(schild);

  // Freistehende Werbestele an der Zufahrt
  const stele = new THREE.Group();
  stele.add(boxMesh(0.34, 4.6, 1.55, M.rot, 0, 2.3, 0));
  const face = new THREE.Mesh(
    new THREE.PlaneGeometry(1.45, 3.4),
    new THREE.MeshStandardMaterial({ map: steleTextur(), emissive: 0xffffff, emissiveIntensity: 0.22, roughness: 0.6 }));
  face.position.set(0.18, 2.9, 0); face.rotation.y = Math.PI / 2;
  stele.add(face);
  const face2 = face.clone(); face2.position.set(-0.18, 2.9, 0); face2.rotation.y = -Math.PI / 2;
  stele.add(face2);
  stele.position.set(9.5, 0, 12.5); stele.rotation.y = -0.25;
  g.add(stele);

  // Vordach über dem Eingang
  g.add(boxMesh(4.4, 0.16, 1.5, M.grauDunkel, 17.3, 3.35, 2.55));
}

/* ------------------------------------------------------ Externe Treppe */

function aussentreppe(g, M) {
  const x = 27.5, y0 = 31.6;
  for (let i = 0; i < 22; i++)
    g.add(boxMesh(1.25, 0.05, 0.30, M.stahlRot, x, 0.35 + i * 0.19, -(y0 + 0.35 + i * 0.28)));
  for (const dx of [-0.62, 0.62]) {
    const w = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.30, 7.5), M.stahlRot);
    w.position.set(x + dx, 2.4, -(y0 + 3.6)); w.rotation.x = -0.60;
    g.add(w);
    const r = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.05, 7.7), M.stahlRot);
    r.position.set(x + dx, 3.4, -(y0 + 3.6)); r.rotation.x = -0.60;
    g.add(r);
  }
  g.add(boxMesh(1.6, 0.12, 1.6, M.stahlRot, x, 4.45, -(y0 + 0.6)));
}

/* ================================================================ Aufbau */

export function buildSite(M) {
  const g = new THREE.Group();

  /* Gelände */
  const boden = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), M.rasen);
  boden.rotation.x = -Math.PI / 2; boden.position.set(15, -0.10, -15);
  boden.receiveShadow = true;
  g.add(boden);

  /* Parkplatz / Zufahrt im Süden */
  const hof = boxMesh(46, 0.10, 17, M.pflaster, 14, -0.04, 10.5);
  hof.receiveShadow = true; hof.castShadow = false; g.add(hof);
  const strasse = boxMesh(70, 0.08, 8, M.asphalt, 14, -0.05, 22.5);
  strasse.receiveShadow = true; strasse.castShadow = false; g.add(strasse);

  /* Terrasse an der Gartenfassade */
  const terrasse = boxMesh(6.6, 0.10, 21, M.pflaster, 33.4, -0.03, -14.0);
  terrasse.receiveShadow = true; terrasse.castShadow = false; g.add(terrasse);

  /* Terrassenmöblierung + Schirme (Fotos 20/54, 49/54) */
  for (const y of [8.0, 13.5, 19.0]) sonnenschirm(g, M, 33.0, y);
  for (const y of [6.5, 9.5, 12.0, 15.0, 17.5, 20.5]) {
    g.add(boxMesh(0.70, 0.04, 0.70, M.grauDunkel, 31.9, 0.74, -y));
    for (const dx of [-0.6, 0.6]) {
      g.add(boxMesh(0.42, 0.05, 0.42, M.grauDunkel, 31.9 + dx, 0.45, -y));
      g.add(boxMesh(0.42, 0.45, 0.05, M.grauDunkel, 31.9 + dx, 0.68, -y - 0.19));
    }
  }

  /* Palmen entlang der Terrasse */
  for (const [x, y, h] of [[35.4, 5.5, 3.2], [35.6, 11.0, 4.0], [35.2, 17.5, 3.6], [35.8, 22.5, 3.0]])
    palme(g, M, x, y, h);
  palme(g, M, 31.6, 25.4, 2.6);

  /* Garten: Liegestühle, Biertische, Kisten (Fotos 18/54, 20/54, 49/54) */
  const liegen = [[40.5, 6.0, -0.5], [42.4, 7.6, -0.35], [40.8, 10.5, -0.6],
                  [42.8, 12.2, -0.4], [41.2, 16.0, -0.55], [43.2, 17.8, -0.3],
                  [39.8, 21.0, -0.7], [42.0, 22.6, -0.45]];
  for (const [x, y, r] of liegen) liegestuhl(g, M, x, y, r);
  for (const [x, y] of [[41.6, 8.8], [42.0, 14.2], [40.6, 19.0]])
    g.add(boxMesh(0.55, 0.45, 0.55, M.holz, x, 0.22, -y));
  for (const [x, y] of [[45.5, 9.0], [45.5, 12.0], [45.5, 15.0], [45.5, 18.0]])
    biertisch(g, M, x, y, 0);

  /* Zaun & Baumbestand */
  zaun(g, M, 30.0, 30.2, 50.0, 30.2);
  zaun(g, M, 50.0, 30.2, 50.0, 1.0);
  zaun(g, M, 50.0, 1.0, 31.0, 1.0);
  for (const [x, y, h] of [[54, 6, 11], [56, 14, 13], [53, 22, 10], [57, 28, 12],
                           [48, 34, 9], [36, 35, 10], [22, 36, 11], [-8, 20, 12],
                           [-10, 6, 9], [-6, 32, 10], [-12, -6, 11]])
    baum(g, M, x, y, h);

  /* Vorfeld: Fahrradbügel + Pflanzkübel (Foto 3/54) */
  for (let i = 0; i < 6; i++) {
    const b = new THREE.Mesh(new THREE.TorusGeometry(0.32, 0.03, 6, 12, Math.PI), M.stahl);
    b.position.set(11.5 + i * 0.75, 0.32, 2.4); g.add(b);
  }
  for (const x of [15.2, 19.6, 22.4]) {
    g.add(boxMesh(0.6, 0.55, 0.6, M.grau, x, 0.28, 2.3));
    const k = new THREE.Mesh(new THREE.SphereGeometry(0.34, 12, 8), M.gruenD);
    k.position.set(x, 0.72, 2.3); g.add(k);
  }

  /* Firmenwagen (Foto 3/54) – stark vereinfacht */
  const auto = new THREE.Group();
  auto.add(boxMesh(3.5, 0.85, 1.65, M.rot, 0, 0.62, 0));
  auto.add(boxMesh(1.9, 0.60, 1.55, M.schwarz, -0.15, 1.28, 0));
  for (const [dx, dz] of [[-1.15, -0.85], [1.15, -0.85], [-1.15, 0.85], [1.15, 0.85]]) {
    const w = new THREE.Mesh(new THREE.CylinderGeometry(0.31, 0.31, 0.22, 14), M.schwarz);
    w.position.set(dx, 0.31, dz); w.rotation.x = Math.PI / 2; auto.add(w);
  }
  auto.position.set(25.5, 0, 5.5); auto.rotation.y = 0.15;
  g.add(auto);

  beschilderung(g, M);
  aussentreppe(g, M);

  g.traverse(o => { if (o.isMesh) { o.castShadow = o.castShadow ?? true; } });
  return g;
}
