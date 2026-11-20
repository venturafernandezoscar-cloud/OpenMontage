// Uso: node render.mjs <escena> [ancho] [alto]
// Salida: salida/<escena>.mov (ProRes 4444 con transparencia, para el montaje)
//         salida/<escena>_preview.mp4 (sobre fondo de cuadros, para revisar)
import { createRequire } from 'node:module'
const { chromium } = createRequire(import.meta.url)('playwright')
import { createServer } from 'vite'
import { mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { execFileSync } from 'node:child_process'

const [escena = 'plato_arcoiris', W = '1920', H = '1080'] = process.argv.slice(2)
const dir = `salida/${escena}_frames`
rmSync(dir, { recursive: true, force: true }); mkdirSync(dir, { recursive: true })

const server = await createServer({ logLevel: 'error' }); await server.listen()
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
const page = await browser.newPage({ viewport: { width: +W, height: +H } })
page.on('pageerror', (e) => console.error('ERROR página:', e.message))
await page.goto(`http://localhost:5199/?escena=${escena}`)
await page.waitForFunction(() => window.__listo === true, null, { timeout: 120000 })
const { fotogramas, fps } = await page.evaluate(() => window.__info)
const t0 = Date.now()
for (let n = 0; n < fotogramas; n++) {
  const url = await page.evaluate((n) => window.__fotograma(n), n)
  writeFileSync(`${dir}/f_${String(n).padStart(5, '0')}.png`, Buffer.from(url.split(',')[1], 'base64'))
  if (n % 30 === 0) console.log(`  ${escena}: ${n}/${fotogramas}  (${((Date.now() - t0) / 1000).toFixed(0)} s)`)
}
await browser.close(); await server.close()

const ff = (args) => execFileSync('ffmpeg', ['-y', '-v', 'error', ...args], { stdio: 'inherit' })
ff(['-framerate', `${fps}`, '-i', `${dir}/f_%05d.png`, '-c:v', 'prores_ks', '-profile:v', '4444',
    '-pix_fmt', 'yuva444p10le', '-vendor', 'apl0', `salida/${escena}.mov`])
ff(['-f', 'lavfi', '-i', `color=c=0xdde6ee:s=${W}x${H}:r=${fps}`, '-framerate', `${fps}`, '-i', `${dir}/f_%05d.png`,
    '-filter_complex', '[0][1]overlay=shortest=1,format=yuv420p', '-c:v', 'libx264', '-crf', '20', `salida/${escena}_preview.mp4`])
console.log(`✅ salida/${escena}.mov  (${fotogramas} fotogramas @ ${fps} fps)`)
