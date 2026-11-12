import { chromium } from 'playwright-core';
import fs from 'node:fs';

console.log('Generating 75s Ambient Keynote Music Bed...');
const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const page = await browser.newPage();

const audioB64 = await page.evaluate(async () => {
  const sr = 48000;
  const dur = 75.0;
  const ctx = new OfflineAudioContext(2, Math.ceil(sr * dur), sr);

  const master = ctx.createGain();
  master.gain.value = 0.55; // Sit gently under voiceover
  master.connect(ctx.destination);

  function playPad(time, dur, freqs, gainLevel = 0.08) {
    freqs.forEach(f => {
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();

      osc.type = 'sawtooth';
      osc2.type = 'sine';
      osc.frequency.setValueAtTime(f, time);
      osc2.frequency.setValueAtTime(f * 1.002, time);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(400, time);
      filter.frequency.exponentialRampToValueAtTime(1200, time + dur * 0.4);
      filter.frequency.exponentialRampToValueAtTime(450, time + dur);

      gain.gain.setValueAtTime(0.0001, time);
      gain.gain.linearRampToValueAtTime(gainLevel / freqs.length, time + 1.2);
      gain.gain.setValueAtTime(gainLevel / freqs.length, time + dur - 1.2);
      gain.gain.linearRampToValueAtTime(0.0001, time + dur);

      osc.connect(filter);
      osc2.connect(filter);
      filter.connect(gain);
      gain.connect(master);

      osc.start(time);
      osc2.start(time);
      osc.stop(time + dur);
      osc2.stop(time + dur);
    });
  }

  function playBell(time, freq, dur = 0.3, vol = 0.04) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, time);

    gain.gain.setValueAtTime(vol, time);
    gain.gain.exponentialRampToValueAtTime(0.0001, time + dur);

    osc.connect(gain);
    gain.connect(master);
    osc.start(time);
    osc.stop(time + dur);
  }

  function playKick(time, vol = 0.25) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.frequency.setValueAtTime(130, time);
    osc.frequency.exponentialRampToValueAtTime(45, time + 0.25);

    gain.gain.setValueAtTime(vol, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.35);

    osc.connect(gain);
    gain.connect(master);
    osc.start(time);
    osc.stop(time + 0.35);
  }

  function playWhoosh(time, dur = 1.0, vol = 0.12) {
    const bufSize = Math.floor(ctx.sampleRate * dur);
    const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < bufSize; i++) data[i] = Math.random() * 2 - 1;
    const src = ctx.createBufferSource();
    src.buffer = buf;

    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.Q.value = 3.0;
    filter.frequency.setValueAtTime(200, time);
    filter.frequency.exponentialRampToValueAtTime(1600, time + dur * 0.5);
    filter.frequency.exponentialRampToValueAtTime(300, time + dur);

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.001, time);
    gain.gain.linearRampToValueAtTime(vol, time + dur * 0.4);
    gain.gain.linearRampToValueAtTime(0.0001, time + dur);

    src.connect(filter);
    filter.connect(gain);
    gain.connect(master);
    src.start(time);
  }

  // Chords across 75s
  playPad(0.0, 10.0, [146.83, 220.0, 261.63, 349.23]); // Dm7
  playPad(10.0, 9.5, [174.61, 220.0, 261.63, 329.63]); // Fmaj7
  playWhoosh(10.0, 1.2, 0.2);
  playKick(10.5, 0.4);

  playPad(19.5, 9.5, [130.81, 196.0, 261.63, 329.63]); // C
  playWhoosh(19.8, 0.8, 0.15);
  playBell(20.4, 880, 0.15, 0.08); // Glass pop

  playPad(29.0, 9.0, [146.83, 220.0, 293.66, 349.23]); // Dm
  playBell(32.4, 1046.5, 0.1, 0.1); // Click
  for (let k = 0; k < 14; k++) {
    playBell(33.0 + k * 0.16, 587.33 + (k % 4) * 50, 0.04, 0.025);
  }

  playPad(38.0, 10.0, [116.54, 174.61, 233.08, 293.66]); // Bbmaj7
  playWhoosh(40.0, 1.4, 0.15);
  playKick(44.5, 0.35); // Drop

  playPad(48.0, 10.5, [146.83, 220.0, 261.63, 392.0]); // Dm9
  playWhoosh(48.5, 1.0, 0.15);

  playPad(58.5, 8.5, [174.61, 220.0, 261.63, 349.23]); // F

  playPad(67.0, 8.0, [146.83, 220.0, 293.66, 349.23, 440.0], 0.14);
  playKick(67.5, 0.4);
  playBell(68.0, 1174.66, 2.0, 0.12);
  playBell(68.3, 1760.0, 2.2, 0.1);

  // Rhythmic kick pulses
  for (let t = 10.5; t < 67.0; t += 2.0) {
    playKick(t, 0.2);
    playBell(t + 0.5, 1318.5, 0.05, 0.015);
    playBell(t + 1.0, 1760.0, 0.05, 0.015);
  }

  const b = await ctx.startRendering();
  const L = b.getChannelData(0);
  const R = b.getChannelData(1);
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
});

await page.close();
await browser.close();

fs.writeFileSync('ambient_bed.pcm', Buffer.from(audioB64, 'base64'));
console.log('Saved ambient_bed.pcm successfully.');
