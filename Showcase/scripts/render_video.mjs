import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const htmlFile = 'clipboard_apple_video.html';
const finalMp4 = 'ClipBoard_Apple_SaaS_1080p.mp4';
const fps = 30;
const workersCount = 4;
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

console.log('=== ClipBoard Apple SaaS Video Renderer (1920x1080) ===');
console.log(`Input HTML: ${htmlFile}`);
console.log(`Output MP4: ${finalMp4}`);
console.log(`Workers: ${workersCount}, Target FPS: ${fps}`);

const run = (args) => new Promise((res, rej) => {
  const p = spawn('ffmpeg', args, { stdio: 'inherit' });
  p.on('close', c => c ? rej(new Error('ffmpeg error ' + c)) : res());
});

const fileUrl = pathToFileURL(path.resolve(htmlFile)).href + '?render';
const browser = await chromium.launch({
  executablePath: chromePath,
  args: ['--allow-file-access-from-files', '--disable-web-security']
});

// Probe dimensions and duration
const probe = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await probe.goto(fileUrl);
await probe.waitForFunction(() => window.VIDEO && typeof window.seek === 'function');
const V = await probe.evaluate(() => window.VIDEO);
console.log(`Video Specs: ${V.w}x${V.h}, ${V.duration}s (${Math.round(V.duration * fps)} total frames)`);
await probe.close();

const totalFrames = Math.round(V.duration * fps);
const perWorker = Math.ceil(totalFrames / workersCount);
const segs = [];
const t0 = Date.now();
let completedFrames = 0;

console.log('\nRendering video frames across parallel Chrome workers...');

await Promise.all(Array.from({ length: workersCount }, async (_, w) => {
  const startF = w * perWorker;
  const endF = Math.min(totalFrames, startF + perWorker);
  if (startF >= endF) return;

  const segName = `seg_${w}.mp4`;
  segs[w] = segName;

  const page = await browser.newPage({ viewport: { width: V.w, height: V.h }, deviceScaleFactor: 1 });
  await page.goto(fileUrl);
  await page.waitForFunction(() => window.VIDEO && typeof window.seek === 'function');

  const ff = spawn('ffmpeg', [
    '-v', 'error', '-y',
    '-f', 'image2pipe',
    '-framerate', String(fps),
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-crf', '16',
    '-preset', 'fast',
    segName
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  const ffDone = new Promise(r => ff.on('close', r));

  for (let f = startF; f < endF; f++) {
    const t = f / fps;
    await page.evaluate(t => window.seek(t), t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) {
      await new Promise(r => ff.stdin.once('drain', r));
    }
    completedFrames++;
    if (completedFrames % 50 === 0 || completedFrames === totalFrames) {
      const pct = ((completedFrames / totalFrames) * 100).toFixed(1);
      const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
      process.stdout.write(`\rProgress: ${completedFrames}/${totalFrames} frames (${pct}%) in ${elapsed}s`);
    }
  }

  ff.stdin.end();
  await ffDone;
  await page.close();
}));

console.log(`\nAll frames rendered in ${((Date.now() - t0) / 1000).toFixed(1)}s! Stitching segments...`);

const listFile = 'segs_list.txt';
writeFileSync(listFile, segs.filter(Boolean).map(s => `file '${path.resolve(s)}'`).join('\n'));
const silentVideo = 'temp_silent.mp4';
await run(['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c', 'copy', silentVideo]);

// Clean segment files
segs.filter(Boolean).forEach(s => { if (existsSync(s)) rmSync(s); });
if (existsSync(listFile)) rmSync(listFile);

// Synthesize Audio Soundtrack via Web Audio API
console.log('\nSynthesizing master Apple-style electronic soundtrack...');
const audioPage = await browser.newPage();
await audioPage.goto(fileUrl);
const audioData = await audioPage.evaluate(async (dur) => {
  const sr = 48000;
  const ctx = new OfflineAudioContext(2, Math.ceil(sr * dur), sr);
  window.buildAudio(ctx);
  const b = await ctx.startRendering();
  const L = b.getChannelData(0);
  const R = b.getChannelData(b.numberOfChannels > 1 ? 1 : 0);
  const i16 = new Int16Array(L.length * 2);
  for (let i = 0; i < L.length; i++) {
    i16[2 * i] = Math.max(-1, Math.min(1, L[i])) * 32767;
    i16[2 * i + 1] = Math.max(-1, Math.min(1, R[i])) * 32767;
  }
  const u8 = new Uint8Array(i16.buffer);
  let s = '';
  for (let i = 0; i < u8.length; i += 0x8000) {
    s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
  }
  return btoa(s);
}, V.duration);
await audioPage.close();
await browser.close();

const pcmFile = 'master_soundtrack.pcm';
writeFileSync(pcmFile, Buffer.from(audioData, 'base64'));
console.log('Audio PCM extracted successfully.');

// Final Mux with EBU R128 / Apple Loudness Normalization (-16 LUFS)
console.log(`\nMuxing final master MP4: ${finalMp4}...`);
await run([
  '-v', 'info', '-y',
  '-i', silentVideo,
  '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', pcmFile,
  '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
  '-c:v', 'copy',
  '-c:a', 'aac',
  '-b:a', '192k',
  '-shortest',
  finalMp4
]);

if (existsSync(silentVideo)) rmSync(silentVideo);
if (existsSync(pcmFile)) rmSync(pcmFile);

console.log(`\n🎉 SUCCESS! Render completed: ${finalMp4}`);
