// Renderiza el logo animado (5 s, 60 fps, fondo transparente) -> logo.mov (ProRes 4444) + logo_preview.mp4 (con jingle)
// Uso: node render_logo.mjs
import { createRequire } from 'node:module'
import { mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
const { chromium } = createRequire(import.meta.url)('playwright')
const AQUI = path.dirname(fileURLToPath(import.meta.url))
const dir = path.join(AQUI, 'salida/logo_frames')
rmSync(dir, { recursive: true, force: true }); mkdirSync(dir, { recursive: true })
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } })
page.on('pageerror', (e) => console.error('ERROR página:', e.message))
await page.goto('file://' + path.join(AQUI, 'logo.html'))
await page.waitForFunction(() => window.__listo === true, null, { timeout: 30000 })
for (let n = 0; n < 300; n++) {
  const url = await page.evaluate((n) => window.__fotograma(n), n)
  writeFileSync(`${dir}/f_${String(n).padStart(5, '0')}.png`, Buffer.from(url.split(',')[1], 'base64'))
}
await browser.close()
const ff = (a) => execFileSync('ffmpeg', ['-y', '-v', 'error', ...a], { stdio: 'inherit' })
ff(['-framerate', '60', '-i', `${dir}/f_%05d.png`, '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', path.join(AQUI, 'salida/logo.mov')])
ff(['-f', 'lavfi', '-i', 'color=c=0x8EE3F5:s=1920x1080:r=60', '-framerate', '60', '-i', `${dir}/f_%05d.png`,
    '-i', path.join(AQUI, '../audio/jingle_saltamundos.wav'),
    '-filter_complex', '[0][1]overlay=shortest=1,format=yuv420p[v]', '-map', '[v]', '-map', '2:a',
    '-c:v', 'libx264', '-crf', '20', '-c:a', 'aac', '-shortest', path.join(AQUI, 'salida/logo_preview.mp4')])
rmSync(dir, { recursive: true, force: true })
console.log('✅ intro/salida/logo.mov + logo_preview.mp4')
