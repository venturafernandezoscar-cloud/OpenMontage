// Objetos de Saltamundos: verduras con ojitos, patito de goma, plato, burbuja.
// Materiales PBR suaves (clearcoat) para casar con el look 3D de los clips de IA.
import * as THREE from 'three'
import { useMemo } from 'react'

const mat = (color, extra = {}) =>
  new THREE.MeshPhysicalMaterial({ color, roughness: 0.38, clearcoat: 0.6, clearcoatRoughness: 0.25, ...extra })

const M = {
  negro: mat('#1a1a2e', { roughness: 0.15, clearcoat: 1 }),
  blanco: new THREE.MeshBasicMaterial({ color: '#ffffff' }),
  tomate: mat('#ff3b3b'), hojita: mat('#3fbf4f'),
  zanahoria: mat('#ff8c1a'), brocoli: mat('#4cc24a', { roughness: 0.6 }), tallo: mat('#9be37a'),
  berenjena: mat('#7b3fe4', { roughness: 0.25, clearcoat: 1 }), maiz: mat('#ffd23f'),
  pato: mat('#ffd60a', { roughness: 0.3, clearcoat: 0.9 }), pico: mat('#ff8c42'),
  plato: mat('#ffffff', { roughness: 0.2, clearcoat: 1 }), bordePlato: mat('#7fd8be'),
}

// Ojitos sonrientes (sin boca, según la biblia): dos esferas negras con brillo blanco.
export function Ojos({ y = 0, z = 0.5, sep = 0.16, s = 0.075 }) {
  return (
    <group position={[0, y, z]}>
      {[-1, 1].map((k) => (
        <group key={k} position={[k * sep, 0, 0]}>
          <mesh material={M.negro}><sphereGeometry args={[s, 24, 16]} /></mesh>
          <mesh material={M.blanco} position={[s * 0.35, s * 0.35, s * 0.8]}><sphereGeometry args={[s * 0.3, 12, 8]} /></mesh>
        </group>
      ))}
    </group>
  )
}

export function Tomate() {
  return (
    <group>
      <mesh castShadow material={M.tomate} scale={[1, 0.88, 1]}><sphereGeometry args={[0.5, 48, 32]} /></mesh>
      {[0, 1, 2, 3, 4].map((i) => (
        <mesh key={i} castShadow material={M.hojita} position={[0, 0.44, 0]} rotation={[0.9, (i * Math.PI * 2) / 5, 0]}>
          <coneGeometry args={[0.06, 0.28, 8]} />
        </mesh>
      ))}
      <Ojos y={0.06} z={0.44} />
    </group>
  )
}

export function Zanahoria() {
  return (
    <group rotation={[0, 0, 0]}>
      <mesh castShadow material={M.zanahoria} rotation={[Math.PI, 0, 0]}><coneGeometry args={[0.28, 1.1, 32]} /></mesh>
      {[-0.3, 0, 0.3].map((r, i) => (
        <mesh key={i} castShadow material={M.hojita} position={[r * 0.3, 0.68, 0]} rotation={[0, 0, r]}>
          <coneGeometry args={[0.07, 0.36, 8]} />
        </mesh>
      ))}
      <Ojos y={0.25} z={0.22} sep={0.1} s={0.055} />
    </group>
  )
}

export function Brocoli() {
  const bolas = useMemo(() => {
    const out = []
    for (let i = 0; i < 9; i++) {
      const a = i * 2.4, r = i === 0 ? 0 : 0.22 + (i % 2) * 0.08
      out.push([Math.cos(a) * r, 0.42 + (i === 0 ? 0.12 : 0), Math.sin(a) * r, i === 0 ? 0.26 : 0.2])
    }
    return out
  }, [])
  return (
    <group>
      <mesh castShadow material={M.tallo} position={[0, 0, 0]}><cylinderGeometry args={[0.13, 0.18, 0.6, 20]} /></mesh>
      {bolas.map(([x, y, z, r], i) => (
        <mesh key={i} castShadow material={M.brocoli} position={[x, y, z]}><sphereGeometry args={[r, 20, 14]} /></mesh>
      ))}
      <Ojos y={0.42} z={0.42} sep={0.13} s={0.06} />
    </group>
  )
}

export function Berenjena() {
  return (
    <group>
      <mesh castShadow material={M.berenjena} scale={[1, 1.35, 1]}><sphereGeometry args={[0.38, 40, 28]} /></mesh>
      <mesh castShadow material={M.hojita} position={[0, 0.52, 0]}><cylinderGeometry args={[0.05, 0.16, 0.18, 12]} /></mesh>
      <Ojos y={0.08} z={0.36} />
    </group>
  )
}

export function Maiz() {
  return (
    <group>
      <mesh castShadow material={M.maiz}><capsuleGeometry args={[0.24, 0.6, 12, 24]} /></mesh>
      {[-1, 1].map((k) => (
        <mesh key={k} castShadow material={M.hojita} position={[k * 0.16, -0.25, 0.05]} rotation={[0, 0, -k * 0.35]} scale={[0.5, 1, 0.25]}>
          <sphereGeometry args={[0.3, 16, 12]} />
        </mesh>
      ))}
      <Ojos y={0.12} z={0.23} sep={0.1} s={0.055} />
    </group>
  )
}

export function Pato({ escala = 1 }) {
  return (
    <group scale={escala}>
      <mesh castShadow material={M.pato} scale={[1.15, 0.8, 0.95]}><sphereGeometry args={[0.5, 40, 28]} /></mesh>
      <mesh castShadow material={M.pato} position={[0.05, 0.25, -0.3]} rotation={[-0.8, 0, 0]} scale={[0.6, 0.35, 0.5]}>
        <sphereGeometry args={[0.4, 24, 16]} />
      </mesh>
      <mesh castShadow material={M.pato} position={[0, 0.55, 0.22]}><sphereGeometry args={[0.32, 36, 24]} /></mesh>
      <mesh castShadow material={M.pico} position={[0, 0.5, 0.52]} scale={[1, 0.45, 1]}><sphereGeometry args={[0.14, 20, 12]} /></mesh>
      <Ojos y={0.64} z={0.47} sep={0.12} s={0.055} />
    </group>
  )
}

export function Plato() {
  const geo = useMemo(() => {
    const p = [[0, 0], [1.6, 0], [1.75, 0.04], [2.1, 0.22], [2.25, 0.3], [2.2, 0.34], [2.0, 0.28], [1.6, 0.1], [0, 0.1]]
    return new THREE.LatheGeometry(p.map(([x, y]) => new THREE.Vector2(x, y)), 96)
  }, [])
  return (
    <group>
      <mesh receiveShadow castShadow geometry={geo} material={M.plato} />
      <mesh position={[0, 0.3, 0]} rotation={[Math.PI / 2, 0, 0]} material={M.bordePlato}>
        <torusGeometry args={[2.18, 0.035, 12, 96]} />
      </mesh>
    </group>
  )
}

export function Burbuja({ color = '#7fd8be', radio = 0.6 }) {
  const m = useMemo(() => new THREE.MeshPhysicalMaterial({
    color, emissive: color, emissiveIntensity: 0.3, transmission: 0.15, thickness: 0.6,
    roughness: 0.08, ior: 1.3, iridescence: 0.8, iridescenceIOR: 1.35, clearcoat: 1,
    clearcoatRoughness: 0.05, transparent: true, opacity: 0.93,
  }), [color])
  return (
    <group>
      <mesh castShadow material={m}><sphereGeometry args={[radio, 48, 32]} /></mesh>
      <mesh position={[-radio * 0.35, radio * 0.4, radio * 0.75]} material={M.blanco}>
        <sphereGeometry args={[radio * 0.12, 12, 8]} />
      </mesh>
    </group>
  )
}

export const OBJETOS = { tomate: Tomate, zanahoria: Zanahoria, brocoli: Brocoli, berenjena: Berenjena, maiz: Maiz, pato: Pato, burbuja: Burbuja }
