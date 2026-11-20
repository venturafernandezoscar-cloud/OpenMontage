// Escenas de física. Tiempos en segundos desde el inicio de cada escena.
// Cada escena se renderiza con fondo transparente para superponerla sobre los clips de IA.
export const ESCENAS = {
  // «¡Verdurita, Sí!» 2:13–2:17 — las verduras saltan al plato formando un arcoíris
  plato_arcoiris: {
    duracion: 4.5,
    camara: { pos: [0, 4.4, 5.8], mira: [0, 0.55, 0], fov: 36 },
    plato: true,
    suelo: 0,
    caidas: [
      { t: 0.20, obj: 'tomate',    pos: [-1.2, 5.5, 0.35], vel: [0, -2, 0], yaw: 0.25 },
      { t: 0.75, obj: 'zanahoria', pos: [-0.6, 5.5, -0.75], vel: [0, -2, 0], yaw: 0.1 },
      { t: 1.30, obj: 'brocoli',   pos: [0.0, 5.5, 0.6],   vel: [0, -2, 0], yaw: 0 },
      { t: 1.85, obj: 'berenjena', pos: [0.65, 5.5, -0.75], vel: [0, -2, 0], yaw: -0.1 },
      { t: 2.40, obj: 'maiz',      pos: [1.2, 5.5, 0.35],  vel: [0, -2, 0], yaw: -0.25 },
    ],
    rebote: 0.4,
  },
  // «¡Burbujas, Burbujas!» puente — «¡Patitos al agua! Uno… dos… tres… cuatro… ¡y CINCO!»
  patitos: {
    duracion: 7,
    camara: { pos: [0, 3.4, 10], mira: [0, 0.9, 0], fov: 38 },
    plato: false,
    suelo: 0,
    caidas: [
      { t: 0.5, obj: 'pato', pos: [-3.2, 6, 0.4],  vel: [0, 0, 0], escala: 0.8, yaw: 0.35 },
      { t: 1.5, obj: 'pato', pos: [-1.6, 6, 0.8],  vel: [0, 0, 0], escala: 0.8, yaw: 0.15 },
      { t: 2.5, obj: 'pato', pos: [1.6, 6, 0.8],   vel: [0, 0, 0], escala: 0.8, yaw: -0.15 },
      { t: 3.5, obj: 'pato', pos: [3.2, 6, 0.4],   vel: [0, 0, 0], escala: 0.8, yaw: -0.35 },
      { t: 5.0, obj: 'pato', pos: [0, 8, -0.6],    vel: [0, -2, 0], escala: 1.7, yaw: 0 },
    ],
    rebote: 0.5,
  },
  // INTRO 0,00–0,80 s — caen 5 burbujas de colores con rebote elástico (Do-Mi-Sol)
  burbujas_intro: {
    duracion: 2.5,
    camara: { pos: [0, 2.6, 11], mira: [0, 2.4, 0], fov: 38 },
    plato: false,
    suelo: 0,
    caidas: [
      { t: 0.00, obj: 'burbuja', pos: [-3.0, 7, 0],  vel: [0, -4, 0], giro: [0, 0, 0], color: '#7FD8BE' },
      { t: 0.10, obj: 'burbuja', pos: [-1.5, 7.5, 0], vel: [0, -4, 0], giro: [0, 0, 0], color: '#FFD23F' },
      { t: 0.20, obj: 'burbuja', pos: [0, 7, 0],     vel: [0, -4, 0], giro: [0, 0, 0], color: '#FF6F59' },
      { t: 0.30, obj: 'burbuja', pos: [1.5, 7.5, 0], vel: [0, -4, 0], giro: [0, 0, 0], color: '#9B5DE5' },
      { t: 0.40, obj: 'burbuja', pos: [3.0, 7, 0],   vel: [0, -4, 0], giro: [0, 0, 0], color: '#F4A259' },
    ],
    rebote: 0.72,
    amortiguacion: 0.35,
  },
}
