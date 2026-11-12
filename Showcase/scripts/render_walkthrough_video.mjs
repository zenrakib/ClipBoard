import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { writeFileSync, rmSync, existsSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const htmlFile = 'clipboard_apple_walkthrough.html';
const finalMp4 = 'ClipBoard_Apple_Keynote_Walkthrough_1080p.mp4';
const audioFile = 'master_soundtrack_walkthrough.wav';
const fps = 30;
const workersCount = 4;
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

console.log('=== ClipBoard Apple Keynote Deep-Dive Walkthrough Renderer (1920x1080) ===');
console.log(`Input HTML: ${htmlFile}`);
console.log(`Input Audio: ${audioFile}`);
console.log(`Output Video: ${finalMp4}`);
console.log(`Workers: ${workersCount}, FPS: ${fps}`);

const run = (args) => new Promise((res, rej) => {
  const p = spawn('ffmpeg', args, { stdio: 'inherit' });
  p.on('close', c => c ? rej(new Error('ffmpeg error ' + c)) : res());
});

const fileUrl = pathToFileURL(path.resolve(htmlFile)).href;
const browser = await chromium.launch({
  executablePath: chromePath,
  args: ['--allow-file-access-from-files', '--disable-web-security']
});

const probe = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await probe.goto(fileUrl);
await probe.waitForFunction(() => window.VIDEO && typeof window.seek === 'function');
const V = await probe.evaluate(() => window.VIDEO);
console.log(`Walkthrough Specs: ${V.w}x${V.h}, ${V.duration}s (${Math.round(V.duration * fps)} total frames)`);
await probe.close();

const totalFrames = Math.round(V.duration * fps);
const perWorker = Math.ceil(totalFrames / workersCount);
const segs = [];
const t0 = Date.now();
let completedFrames = 0;

console.log('\nRendering frames across parallel Chrome workers...');

await Promise.all(Array.from({ length: workersCount }, async (_, w) => {
  const startF = w * perWorker;
  const endF = Math.min(totalFrames, startF + perWorker);
  if (startF >= endF) return;

  const segName = `wt_seg_${w}.mp4`;
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

await browser.close();

console.log(`\nAll frames rendered in ${((Date.now() - t0) / 1000).toFixed(1)}s! Stitching video segments...`);

const listFile = 'wt_segs_list.txt';
writeFileSync(listFile, segs.filter(Boolean).map(s => `file '${path.resolve(s)}'`).join('\n'));
const silentVideo = 'temp_wt_silent.mp4';
await run(['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c', 'copy', silentVideo]);

segs.filter(Boolean).forEach(s => { if (existsSync(s)) rmSync(s); });
if (existsSync(listFile)) rmSync(listFile);

console.log(`\nMuxing video with Master Voiceover & Ambient Keynote Soundtrack: ${finalMp4}...`);
await run([
  '-v', 'info', '-y',
  '-i', silentVideo,
  '-i', audioFile,
  '-c:v', 'copy',
  '-c:a', 'aac',
  '-b:a', '256k',
  '-shortest',
  finalMp4
]);

if (existsSync(silentVideo)) rmSync(silentVideo);

console.log(`\n🎉 MASTERPIECE RENDER COMPLETE: ${finalMp4}`);
