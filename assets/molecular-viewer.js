/* Project Asma: experimental coordinates, educational representations.
   Three.js 0.170.0 / MIT, vendored locally; see vendor/README.md.
   No remote requests, simulation, molecular dynamics, or clinical inference. */
import * as THREE from './vendor/three.module.min.js';

const MODEL_URLS = {
  insulin: new URL('./models/insulin.json', import.meta.url),
  dna: new URL('./models/dna.json', import.meta.url),
};
const CHAIN_COLORS = [0xe9b653, 0x63cbd3];
const ELEMENT_COLORS = { C: 0x9aa8b5, N: 0x648cfa, O: 0xf37775, S: 0xf2cb61, P: 0xf3a156 };
const ELEMENT_RADII = { C: 0.46, N: 0.43, O: 0.41, S: 0.57, P: 0.55 };
const Y_AXIS = new THREE.Vector3(0, 1, 0);

function setupViewer(root) {
  const find = (name) => root.querySelector(`[data-molecule-${name}]`);
  const canvas = find('canvas');
  const fallback = find('fallback');
  const status = find('status');
  const selector = find('select');
  const display = find('display');
  const controls = find('controls');
  const loading = find('loading');
  if (!canvas || !fallback) return;

  let renderer, model, molecule, modelRadius = 20, baseDistance = 65;
  let requestedFrame = 0, requestId = 0, ready = false, lost = false;
  let autoRotate = false, visible = true, lastFrame = 0;
  let mode = display?.value === 'atoms' ? 'atoms' : 'backbone';
  const initialRotation = new THREE.Quaternion();
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 2000);
  const points = new Map();
  let pinchDistance = 0;

  const announce = (text) => { if (status) status.textContent = text; };
  const motionAllowed = () => !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    && (!window.F0?.motion || window.F0.motion());
  function setReady(value) {
    ready = value;
    root.dataset.moleculeReady = String(value);
    canvas.style.visibility = value ? 'visible' : 'hidden';
    canvas.setAttribute('aria-hidden', String(!value));
    canvas.tabIndex = value ? 0 : -1;
    fallback.hidden = value;
    if (controls) controls.disabled = !value;
    root.querySelectorAll('[data-molecule-action], [data-molecule-display]').forEach((control) => {
      control.disabled = !value;
    });
  }
  function fail(message) {
    setReady(false);
    stopRotation();
    if (loading) loading.hidden = true;
    root.setAttribute('aria-busy', 'false');
    announce(message);
  }
  function stopRotation() {
    autoRotate = false;
    root.querySelectorAll('[data-molecule-action="rotate"]').forEach((button) => {
      button.setAttribute('aria-pressed', 'false');
    });
  }
  function render(time = 0) {
    requestedFrame = 0;
    if (!renderer || !molecule || lost) return;
    if (autoRotate && (!motionAllowed() || !visible || document.hidden)) stopRotation();
    if (autoRotate) {
      const elapsed = lastFrame ? Math.min(40, time - lastFrame) : 0;
      molecule.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(Y_AXIS, elapsed * 0.00016));
    }
    lastFrame = time;
    try { renderer.render(scene, camera); }
    catch { fail('The 3D view could not be drawn. The structure explanation remains available below.'); return; }
    if (autoRotate) schedule();
  }
  function schedule() {
    if (!requestedFrame && !lost) requestedFrame = requestAnimationFrame(render);
  }
  function resize() {
    if (!renderer) return;
    const width = Math.max(1, canvas.clientWidth || canvas.parentElement.clientWidth);
    const height = Math.max(1, canvas.clientHeight || 400);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    // Fit the same bounding sphere in either portrait or landscape canvases.
    const angle = Math.atan(Math.tan(camera.fov * Math.PI / 360) * Math.min(1, camera.aspect));
    const previous = baseDistance;
    baseDistance = modelRadius / Math.sin(angle) * 1.12;
    camera.position.z = previous ? camera.position.z * baseDistance / previous : baseDistance;
    camera.near = Math.max(0.1, modelRadius * 0.01);
    camera.far = modelRadius * 35;
    camera.updateProjectionMatrix();
    schedule();
  }
  function rotate(dx, dy) {
    if (!ready || !molecule) return;
    stopRotation();
    const qx = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), dy);
    const qy = new THREE.Quaternion().setFromAxisAngle(Y_AXIS, dx);
    molecule.quaternion.premultiply(qx).premultiply(qy).normalize();
    schedule();
  }
  function zoom(factor) {
    camera.position.z = Math.max(modelRadius * 1.75, Math.min(baseDistance * 2.5, camera.position.z * factor));
    schedule();
  }
  function action(name) {
    if (!ready) return;
    const step = Math.PI / 12;
    if (name === 'left') rotate(-step, 0);
    if (name === 'right') rotate(step, 0);
    if (name === 'up') rotate(0, -step);
    if (name === 'down') rotate(0, step);
    if (name === 'zoom-in') zoom(0.85);
    if (name === 'zoom-out') zoom(1 / 0.85);
    if (name === 'reset') {
      stopRotation();
      molecule.quaternion.copy(initialRotation);
      camera.position.set(0, 0, baseDistance);
      announce(`${model.title}. View reset.`);
      schedule();
    }
    if (name === 'rotate') {
      if (!motionAllowed()) {
        stopRotation();
        announce('Automatic rotation is off because reduced motion is selected. Drag or use the rotation buttons to explore.');
        return;
      }
      autoRotate = !autoRotate;
      root.querySelectorAll('[data-molecule-action="rotate"]').forEach((button) => button.setAttribute('aria-pressed', String(autoRotate)));
      lastFrame = 0;
      schedule();
    }
  }

  setReady(false);
  try {
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    renderer.setClearColor(0x000000, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
  } catch {
    fail('Interactive 3D is unavailable in this browser. Read the structure explanation below.');
    return;
  }
  scene.add(new THREE.HemisphereLight(0xe1f5ff, 0x1c2737, 2.0));
  const key = new THREE.DirectionalLight(0xffedd3, 3.2);
  key.position.set(-25, 35, 55); scene.add(key);
  const rim = new THREE.DirectionalLight(0x67d9f4, 2.3);
  rim.position.set(25, -5, -25); scene.add(rim);
  const fill = new THREE.DirectionalLight(0xffffff, 0.9);
  fill.position.set(15, -25, 40); scene.add(fill);

  function material(extra = {}) {
    return new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.37, metalness: 0.13, ...extra });
  }
  function dispose(group) {
    group.traverse((object) => {
      object.geometry?.dispose();
      if (Array.isArray(object.material)) object.material.forEach((mat) => mat.dispose());
      else object.material?.dispose();
      object.dispose?.();
    });
  }
  function createStructure(data) {
    const group = new THREE.Group();
    const bounds = new THREE.Box3();
    data.atoms.forEach((atom) => bounds.expandByPoint(new THREE.Vector3(atom.x, atom.y, atom.z)));
    const center = bounds.getCenter(new THREE.Vector3());
    const positions = data.atoms.map((atom) => new THREE.Vector3(atom.x, atom.y, atom.z).sub(center));
    modelRadius = Math.max(...positions.map((point) => point.length())) + 0.8;
    const chains = [...new Set(data.atoms.map((atom) => atom.chain))];
    const chainColor = (index) => CHAIN_COLORS[chains.indexOf(data.atoms[index].chain) % CHAIN_COLORS.length];
    const elementColor = (index) => ELEMENT_COLORS[data.atoms[index].element] || 0xc4cbd0;
    const dummy = new THREE.Object3D();
    function spheres(indices, radius, colors, mat) {
      if (!indices.length) return;
      const mesh = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 16, 12), mat, indices.length);
      indices.forEach((index, instance) => {
        dummy.position.copy(positions[index]);
        dummy.quaternion.identity();
        dummy.scale.setScalar(typeof radius === 'function' ? radius(index) : radius);
        dummy.updateMatrix(); mesh.setMatrixAt(instance, dummy.matrix);
        mesh.setColorAt(instance, new THREE.Color(colors(index)));
      });
      group.add(mesh);
    }
    function rods(edges, radius, colors, mat, split = false) {
      if (!edges.length) return;
      const mesh = new THREE.InstancedMesh(new THREE.CylinderGeometry(1, 1, 1, 8, 1), mat, edges.length * (split ? 2 : 1));
      let instance = 0;
      function segment(start, end, color) {
        const direction = new THREE.Vector3().subVectors(end, start);
        dummy.position.copy(start).add(end).multiplyScalar(0.5);
        dummy.quaternion.setFromUnitVectors(Y_AXIS, direction.clone().normalize());
        dummy.scale.set(radius, direction.length(), radius);
        dummy.updateMatrix(); mesh.setMatrixAt(instance, dummy.matrix);
        mesh.setColorAt(instance++, new THREE.Color(color));
      }
      edges.forEach((edge) => {
        const start = positions[edge.a], end = positions[edge.b];
        if (split) {
          const middle = start.clone().add(end).multiplyScalar(0.5);
          segment(start, middle, colors(edge.a)); segment(middle, end, colors(edge.b));
        } else segment(start, end, colors(edge.a));
      });
      group.add(mesh);
    }
    const all = data.atoms.map((_, index) => index);
    if (mode === 'atoms') {
      spheres(all, (index) => ELEMENT_RADII[data.atoms[index].element] || 0.45, elementColor, material());
      rods(data.bonds, 0.105, elementColor, material({ roughness: 0.46 }), true);
      if (data.contacts?.length) {
        const vertices = data.contacts.flatMap(({ a, b }) => [...positions[a].toArray(), ...positions[b].toArray()]);
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        const contacts = new THREE.LineSegments(geometry, new THREE.LineDashedMaterial({ color: 0xbfd0db, transparent: true, opacity: 0.55, dashSize: 0.20, gapSize: 0.17 }));
        contacts.computeLineDistances(); group.add(contacts);
      }
    } else {
      // A translucent covalent skeleton gives the representative-atom guide context.
      rods(data.bonds, 0.052, chainColor, material({ transparent: true, opacity: 0.20, depthWrite: false }));
      spheres(all, 0.12, chainColor, material({ transparent: true, opacity: 0.23, depthWrite: false }));
      const backbone = data.backbone || [];
      const radius = data.id === 'dna' ? 0.47 : 0.42;
      // Smooth guides interpolate deposited representative atoms. They describe
      // the fold; the interpolated tube is not a chemical bond or atomic surface.
      const next = new Map(backbone.map(({ a, b }) => [a, b]));
      const destinations = new Set(backbone.map(({ b }) => b));
      const starts = backbone.map(({ a }) => a).filter((a) => !destinations.has(a));
      starts.forEach((start) => {
        const indices = [start];
        while (next.has(indices.at(-1)) && indices.length <= data.atoms.length) indices.push(next.get(indices.at(-1)));
        const curve = new THREE.CatmullRomCurve3(indices.map((index) => positions[index]), false, 'centripetal');
        const geometry = new THREE.TubeGeometry(curve, Math.max(32, indices.length * 10), radius, 10, false);
        group.add(new THREE.Mesh(geometry, material({ color: chainColor(start) })));
        spheres([start, indices.at(-1)], radius, chainColor, material());
      });
      const disulfides = data.bonds.filter((edge) => edge.kind === 'disulfide');
      rods(disulfides, 0.18, () => ELEMENT_COLORS.S, material());
      spheres([...new Set(disulfides.flatMap(({ a, b }) => [a, b]))], 0.38, () => ELEMENT_COLORS.S, material());
    }
    // A rigid rotation only: coordinates and molecular handedness are preserved.
    // Orient the longest principal axis vertically, then tilt slightly for depth.
    let axis = new THREE.Vector3(0.43, 0.71, 0.56).normalize();
    for (let iteration = 0; iteration < 24; iteration++) {
      const next = new THREE.Vector3();
      positions.forEach((point) => next.addScaledVector(point, point.dot(axis)));
      if (next.lengthSq() > 0) axis = next.normalize();
    }
    if (axis.y < 0) axis.negate();
    group.quaternion.setFromUnitVectors(axis, Y_AXIS);
    group.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), -0.24));
    group.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(Y_AXIS, 0.28));
    return group;
  }
  function updateCopy(data) {
    const write = (name, value) => { const node = find(name); if (node) node.textContent = value; };
    write('name', data.title);
    write('description', data.description);
    const explanation = find('explanation');
    if (explanation) {
      explanation.replaceChildren();
      (data.explanation || []).forEach((text) => {
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        explanation.appendChild(paragraph);
      });
    }
    write('limits', Array.isArray(data.limits) ? data.limits.join(' ') : data.limits);
    write('count', `${data.atoms.length} atoms · ${data.accession} · experimental coordinates`);
    const fallbackImage = fallback.querySelector('img');
    if (fallbackImage && Object.hasOwn(MODEL_URLS, data.id)) {
      fallbackImage.src = new URL(`./models/${data.id}-preview.svg`, import.meta.url).href;
      fallbackImage.alt = `A static projection of ${data.title.toLowerCase()}, drawn from ${data.accession} deposited atomic coordinates.`;
    }
    const fallbackCaption = fallback.querySelector('p');
    if (fallbackCaption) fallbackCaption.textContent = `${data.title} · ${data.accession} experimental coordinates`;
    write('legend', mode === 'atoms'
      ? 'Elements: carbon gray · nitrogen blue · oxygen coral · sulfur yellow · phosphorus orange. Solid sticks join chemically bonded atoms; they do not distinguish single from double bonds. Dotted DNA lines mark hydrogen bonds between matching bases. Sphere sizes are illustrative.'
      : `Gold: chain A · cyan: chain B. ${data.id === 'dna' ? 'Curves trace one selected sugar atom in each building block.' : 'Curves trace one selected carbon atom in each building block. Yellow links mark sulfur-to-sulfur bonds.'} Curves guide the eye along each chain; the faint sticks show the actual chemical connections.`);
    const source = find('source');
    if (source) { source.href = data.sourceUrl; source.textContent = `View experimental structure · ${data.accession}`; }
    canvas.setAttribute('aria-label', `${data.title}, interactive ${mode === 'atoms' ? 'ball-and-stick model' : 'backbone guide'}. Drag to rotate, arrow keys to rotate, plus and minus to zoom, R to reset. Source ${data.accession}.`);
  }
  function showModel(data, preserveView = false) {
    const previous = molecule;
    molecule = createStructure(data);
    if (preserveView && previous) molecule.quaternion.copy(previous.quaternion);
    else initialRotation.copy(molecule.quaternion);
    scene.add(molecule);
    if (previous) { scene.remove(previous); dispose(previous); }
    if (!preserveView) camera.position.set(0, 0, baseDistance);
    resize();
    updateCopy(data);
    // The static alternative remains visible until an actual render succeeds.
    renderer.render(scene, camera);
    if (renderer.getContext().isContextLost()) throw new Error('WebGL context lost');
    setReady(true);
    if (loading) loading.hidden = true;
    root.setAttribute('aria-busy', 'false');
    announce(`${data.title} loaded. ${data.atoms.length} deposited atoms. ${mode === 'atoms' ? 'Ball-and-stick view.' : 'Backbone guide view.'}`);
  }
  async function load(id) {
    const currentRequest = ++requestId;
    stopRotation();
    setReady(false);
    if (loading) loading.hidden = false;
    root.setAttribute('aria-busy', 'true');
    announce('Loading locally stored experimental coordinates…');
    try {
      if (!Object.hasOwn(MODEL_URLS, id)) throw new Error('Unknown structure');
      const response = await fetch(MODEL_URLS[id], { credentials: 'same-origin' });
      if (!response.ok) throw new Error('Structure unavailable');
      const data = await response.json();
      if (currentRequest !== requestId || lost) return;
      if (!Array.isArray(data.atoms) || !data.atoms.length || data.atoms.length > 2000
        || !Array.isArray(data.bonds) || !data.atoms.every((atom) => [atom.x, atom.y, atom.z].every(Number.isFinite))) throw new Error('Invalid coordinates');
      for (const edge of [...data.bonds, ...(data.backbone || []), ...(data.contacts || [])]) {
        if (![edge.a, edge.b].every((index) => Number.isInteger(index) && index >= 0 && index < data.atoms.length)) throw new Error('Invalid connectivity');
      }
      model = data;
      showModel(data);
    } catch {
      if (currentRequest !== requestId || lost) return;
      // Keep the selected name aligned with the last structure whose explanation
      // and static projection remain visible after a failed replacement request.
      if (selector) selector.value = model?.id || root.dataset.model || 'insulin';
      fail('The 3D structure could not load. The structure explanation remains available; reload the page to try again.');
    }
  }

  root.querySelectorAll('[data-molecule-action]').forEach((button) => button.addEventListener('click', () => action(button.dataset.moleculeAction)));
  selector?.addEventListener('change', () => load(selector.value));
  display?.addEventListener('change', () => {
    if (!model || lost) return;
    mode = display.value === 'atoms' ? 'atoms' : 'backbone';
    stopRotation();
    try { showModel(model, true); } catch { fail('The 3D view is unavailable. The structure explanation remains available below.'); }
  });
  canvas.addEventListener('keydown', (event) => {
    const keys = { ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'up', ArrowDown: 'down', '+': 'zoom-in', '=': 'zoom-in', '-': 'zoom-out', '_': 'zoom-out', r: 'reset', R: 'reset' };
    if (!ready || event.ctrlKey || event.metaKey || event.altKey || !keys[event.key]) return;
    event.preventDefault(); action(keys[event.key]);
  });
  canvas.addEventListener('pointerdown', (event) => {
    if (!ready || (event.pointerType === 'mouse' && event.button !== 0)) return;
    stopRotation();
    canvas.focus({ preventScroll: true });
    canvas.setPointerCapture(event.pointerId);
    points.set(event.pointerId, { x: event.clientX, y: event.clientY });
    pinchDistance = 0;
  });
  canvas.addEventListener('pointermove', (event) => {
    if (!points.has(event.pointerId) || !ready) return;
    const previous = points.get(event.pointerId);
    points.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (points.size === 1) rotate((event.clientX - previous.x) * 0.008, (event.clientY - previous.y) * 0.008);
    else if (points.size === 2) {
      const [a, b] = [...points.values()];
      const distance = Math.hypot(a.x - b.x, a.y - b.y);
      if (pinchDistance > 0 && distance > 0) zoom(pinchDistance / distance);
      pinchDistance = distance;
    }
  });
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach((name) => canvas.addEventListener(name, (event) => { points.delete(event.pointerId); pinchDistance = 0; }));
  // Wheel zoom is deliberate: un-focused canvases preserve normal page scrolling.
  canvas.addEventListener('wheel', (event) => {
    if (!ready || document.activeElement !== canvas || event.ctrlKey) return;
    event.preventDefault(); zoom(Math.exp(Math.max(-100, Math.min(100, event.deltaY)) * 0.002));
  }, { passive: false });
  canvas.addEventListener('webglcontextlost', (event) => {
    event.preventDefault(); lost = true; requestId++;
    if (requestedFrame) cancelAnimationFrame(requestedFrame);
    requestedFrame = 0;
    fail('The browser paused the 3D graphics. The structure explanation remains available; reload to restore the interactive view.');
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopRotation(); });
  new MutationObserver(() => { if (!motionAllowed()) stopRotation(); }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-motion', 'data-motion-pref'] });
  window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', () => { if (!motionAllowed()) stopRotation(); });
  if ('IntersectionObserver' in window) new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (!visible) stopRotation();
  }, { threshold: 0 }).observe(canvas);
  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(canvas);
  else window.addEventListener('resize', resize, { passive: true });
  camera.position.set(0, 0, baseDistance);
  resize();
  load(selector?.value || root.dataset.model || 'insulin');
}

document.querySelectorAll('[data-molecule-viewer]').forEach(setupViewer);
