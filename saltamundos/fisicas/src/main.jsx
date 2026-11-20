// Motor de render determinista: la física avanza exactamente 1/fps por fotograma
// y Playwright captura cada fotograma con fondo transparente.
import { createRoot } from 'react-dom/client'
import { Canvas, useThree, advance } from '@react-three/fiber'
import { Physics, RigidBody, CuboidCollider, useRapier } from '@react-three/rapier'
import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { ESCENAS } from './escenas.js'
import { OBJETOS, Plato } from './objetos.jsx'

const q = new URLSearchParams(location.search)
const escena = ESCENAS[q.get('escena') || 'plato_arcoiris']
const FPS = Number(q.get('fps') || 60)

function Entorno() {
  const { gl, scene, camera } = useThree()
  useEffect(() => {
    const pm = new THREE.PMREMGenerator(gl)
    scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture
    gl.toneMapping = THREE.NeutralToneMapping
    gl.toneMappingExposure = 1.05
    const c = escena.camara
    camera.position.set(...c.pos); camera.fov = c.fov; camera.lookAt(...c.mira); camera.updateProjectionMatrix()
  }, [])
  return (
    <>
      <ambientLight intensity={0.35} />
      <directionalLight castShadow position={[4, 9, 6]} intensity={2.2} shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-8} shadow-camera-right={8} shadow-camera-top={8} shadow-camera-bottom={-8} shadow-bias={-0.0004} />
      <directionalLight position={[-6, 4, -4]} intensity={0.8} color="#bfe9ff" />
      {/* recoge solo las sombras: el fondo sigue siendo transparente */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, escena.suelo + 0.001, 0]} receiveShadow>
        <planeGeometry args={[40, 40]} />
        <shadowMaterial opacity={0.22} />
      </mesh>
    </>
  )
}

// Media altura aproximada de cada objeto: el aplastamiento se hace desde la base, no desde el centro
const BASE = { tomate: 0.44, zanahoria: 0.55, brocoli: 0.3, berenjena: 0.51, maiz: 0.54, pato: 0.4, burbuja: 0.6 }

function Caida({ c, i, refs, cuerpos }) {
  const Obj = OBJETOS[c.obj]
  return (
    <RigidBody ref={(r) => (refs.current[i] = r)} colliders={c.obj === 'burbuja' ? 'ball' : 'hull'} position={[1000 + i * 20, 0, 0]}
      gravityScale={0} restitution={escena.rebote} friction={1.2} linearDamping={escena.amortiguacion ?? 0.05}
      lockRotations>
      <group rotation={[0, c.yaw || 0, 0]}>
        <group ref={(g) => (cuerpos.current[i] = g)}>
          <Obj escala={c.escala} color={c.color} />
        </group>
      </group>
    </RigidBody>
  )
}

// Squash & stretch (principios Disney): se estira al caer rápido y se aplasta al chocar.
function deformar(estado, g, vy, base) {
  const prev = estado.vy ?? 0
  if (prev < -2.5 && vy - prev > 2.5) { estado.golpe = 9; estado.fuerza = Math.min(1, -prev / 10) }
  let sy = 1, sxz = 1
  if (estado.golpe > 0) {
    const k = Math.sin((estado.golpe / 9) * Math.PI) * estado.fuerza
    sy = 1 - 0.3 * k; sxz = 1 + 0.2 * k; estado.golpe--
  } else if (Math.abs(vy) > 1) {
    const st = Math.min(0.14, Math.abs(vy) * 0.012); sy = 1 + st; sxz = 1 - st / 2
  }
  g.scale.set(sxz, sy, sxz)
  g.position.y = -base * (1 - sy)
  estado.vy = vy
}

function Motor() {
  const { step } = useRapier()
  const { gl } = useThree()
  const refs = useRef([])
  const cuerpos = useRef([])
  const estados = useRef(escena.caidas.map(() => ({})))
  const hechos = useRef(new Set())
  useEffect(() => {
    window.__info = { fotogramas: Math.round(escena.duracion * FPS), fps: FPS }
    window.__fotograma = (n) => {
      const t = n / FPS
      escena.caidas.forEach((c, i) => {
        const rb = refs.current[i]
        if (!hechos.current.has(i) && t >= c.t && rb) {
          rb.setTranslation({ x: c.pos[0], y: c.pos[1], z: c.pos[2] }, true)
          rb.setLinvel({ x: c.vel[0], y: c.vel[1], z: c.vel[2] }, true)
          rb.setAngvel({ x: (c.giro || [0, 0, 0])[0], y: (c.giro || [0, 0, 0])[1], z: (c.giro || [0, 0, 0])[2] }, true)
          rb.setGravityScale(1, true)
          hechos.current.add(i)
        }
      })
      if (n > 0) step(1 / FPS)
      escena.caidas.forEach((c, i) => {
        if (hechos.current.has(i) && cuerpos.current[i])
          deformar(estados.current[i], cuerpos.current[i], refs.current[i].linvel().y, BASE[c.obj] * (c.escala || 1))
      })
      advance(performance.now())
      return gl.domElement.toDataURL('image/png')
    }
    window.__listo = true
  }, [])
  return (
    <>
      {escena.caidas.map((c, i) => <Caida key={i} c={c} i={i} refs={refs} cuerpos={cuerpos} />)}
      <CuboidCollider args={[30, 0.5, 30]} position={[0, escena.suelo - 0.5, 0]} restitution={escena.rebote} />
      {escena.plato && (
        <RigidBody type="fixed" colliders="trimesh" restitution={escena.rebote}>
          <Plato />
        </RigidBody>
      )}
    </>
  )
}

createRoot(document.getElementById('root')).render(
  <Canvas frameloop="never" shadows dpr={1}
    gl={{ alpha: true, antialias: true, preserveDrawingBuffer: true, premultipliedAlpha: false }}
    camera={{ position: [0, 4, 8], fov: 35 }} onCreated={({ gl }) => gl.setClearColor(0x000000, 0)}>
    <Entorno />
    <Physics paused interpolate={false} timeStep={1 / FPS} gravity={[0, -14, 0]}>
      <Motor />
    </Physics>
  </Canvas>
)
