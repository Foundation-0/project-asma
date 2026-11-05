# Three.js browser runtime

`three.module.min.js` is a locally bundled, tree-shaken subset of **Three.js
0.170.0** (MIT). Copyright and permission terms are retained in
`THREE-LICENSE.txt`. Upstream: <https://github.com/mrdoob/three/tree/r170>.
There are no external runtime requests or telemetry.

Built once with esbuild 0.25.5 (`--bundle --minify --format=esm
--target=es2020 --legal-comments=inline`) from this entry point:

```js
export {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Color, HemisphereLight,
  DirectionalLight, AmbientLight, InstancedMesh, SphereGeometry, CylinderGeometry,
  MeshStandardMaterial, Object3D, Vector3, Quaternion, Box3, Matrix4,
  BufferGeometry, Float32BufferAttribute, LineSegments, LineDashedMaterial,
  TubeGeometry, CatmullRomCurve3, Mesh, SRGBColorSpace, ACESFilmicToneMapping
} from 'three';
```

The static site needs no package manager or build step. To reproduce, install
the exact package versions into a temporary directory, save the entry point
there, and run its esbuild binary. Geometry coordinates and provenance are
separate files in `../models/`.
