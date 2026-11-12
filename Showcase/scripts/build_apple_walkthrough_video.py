#!/usr/bin/env python3
"""
build_apple_walkthrough_video.py
Generates clipboard_apple_walkthrough.html:
A 75-second comprehensive 1080p Apple Keynote & SaaS Deep-Dive Video for ClipBoard for macOS,
with synchronized visual system badges, live captions, animated UI interactions, and audio voiceover narration.
"""

import os

with open("appicon_b64.txt", "r") as f:
    appicon_b64 = f.read().strip()

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ClipBoard for macOS — System Deep Dive & Keynote Walkthrough</title>
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  body {{
    background: #000;
    color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
    overflow: hidden;
    user-select: none;
    width: 100vw;
    height: 100vh;
  }}

  #stage {{
    position: absolute;
    top: 0;
    left: 0;
    width: 1920px;
    height: 1080px;
    background: radial-gradient(circle at 50% 32%, #0f172a 0%, #060912 65%, #020306 100%);
    overflow: hidden;
    transform-origin: top left;
  }}

  /* Ambient Dynamic Glows */
  .ambient-glow {{
    position: absolute;
    border-radius: 50%;
    filter: blur(140px);
    pointer-events: none;
    opacity: 0.45;
  }}
  .glow-cyan {{
    width: 950px;
    height: 750px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.24) 0%, rgba(30, 58, 138, 0.05) 70%, transparent 100%);
    top: -150px;
    left: 50%;
    transform: translateX(-50%);
  }}
  .glow-purple {{
    width: 850px;
    height: 650px;
    background: radial-gradient(circle, rgba(168, 85, 247, 0.16) 0%, transparent 70%);
    bottom: -100px;
    right: 80px;
  }}

  .grid-pattern {{
    position: absolute;
    inset: 0;
    background-image: 
      linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px);
    background-size: 60px 60px;
    opacity: 0.6;
    pointer-events: none;
  }}

  /* Top Technical HUD Banner */
  .hud-banner {{
    position: absolute;
    top: 36px;
    left: 60px;
    right: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 100;
  }}
  .system-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(56, 189, 248, 0.3);
    backdrop-filter: blur(20px);
    border-radius: 999px;
    padding: 6px 16px;
    font-family: monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #38bdf8;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }}
  .hud-title {{
    font-size: 13px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.5);
    letter-spacing: 0.15em;
    text-transform: uppercase;
  }}

  /* Typography */
  .tagline {{
    font-size: 15px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    color: #38bdf8;
    margin-bottom: 12px;
  }}
  .hero-title {{
    font-size: 76px;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.05;
    background: linear-gradient(180deg, #ffffff 30%, #a1a1aa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .hero-sub {{
    font-size: 30px;
    font-weight: 400;
    color: #94a3b8;
    letter-spacing: -0.015em;
    margin-top: 16px;
    line-height: 1.35;
  }}

  /* Live Voiceover Subtitles Pill */
  .subtitle-pill {{
    position: absolute;
    bottom: 40px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(30px);
    border-radius: 999px;
    padding: 12px 32px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.7);
    z-index: 1000;
    max-width: 1400px;
    transition: opacity 0.3s ease;
  }}
  .subtitle-icon {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #38bdf8;
    box-shadow: 0 0 10px #38bdf8;
    flex-shrink: 0;
  }}
  .subtitle-text {{
    font-size: 18px;
    font-weight: 500;
    color: #f1f5f9;
    letter-spacing: -0.01em;
    text-align: center;
    white-space: nowrap;
  }}

  /* Scenes */
  .scene {{
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    pointer-events: none;
    opacity: 0;
    transform-origin: center center;
  }}

  /* CLIPBOARD WINDOW UI */
  .clipboard-window {{
    width: 340px;
    height: 440px;
    background: rgba(18, 22, 31, 0.82);
    backdrop-filter: blur(45px);
    -webkit-backdrop-filter: blur(45px);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 10px;
    box-shadow: 0 35px 90px rgba(0, 0, 0, 0.8), 0 0 1px 1px rgba(255, 255, 255, 0.15);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: absolute;
  }}
  .win-drag-handle {{
    width: 40px;
    height: 4px;
    background: rgba(255, 255, 255, 0.28);
    border-radius: 2px;
    margin: 6px auto 4px auto;
  }}
  .win-tab-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 2px 10px 4px 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }}
  .tab-group {{
    display: flex;
    gap: 4px;
  }}
  .tab-btn {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.65);
    background: transparent;
    border: none;
    position: relative;
  }}
  .tab-btn.active {{
    color: #fff;
    background: rgba(255, 255, 255, 0.08);
  }}
  .tab-indicator {{
    position: absolute;
    bottom: -4px;
    left: 12px;
    right: 12px;
    height: 2px;
    background: #61ccff;
    border-radius: 1px;
    box-shadow: 0 0 8px #61ccff;
  }}
  .win-search-box {{
    margin: 7px 10px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 6px 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.85);
  }}
  .win-card-list {{
    flex: 1;
    overflow-y: hidden;
    padding: 2px 8px 6px 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .section-label {{
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 2px 4px 0 4px;
    display: flex;
    align-items: center;
    gap: 5px;
  }}
  .section-label.pinned {{ color: #61ccff; }}
  .section-label.recent {{ color: rgba(255, 255, 255, 0.45); }}

  .clip-card {{
    position: relative;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 7px 10px 7px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .clip-card.selected {{
    background: rgba(255, 255, 255, 0.09);
    border-color: rgba(97, 204, 255, 0.3);
  }}
  .accent-bar {{
    position: absolute;
    left: 2px;
    top: 6px;
    bottom: 6px;
    width: 3px;
    border-radius: 1.5px;
    background: #61ccff;
    box-shadow: 0 0 6px #61ccff;
    opacity: 0;
  }}
  .clip-card.selected .accent-bar {{ opacity: 1; }}
  .clip-card-text {{
    font-size: 11.5px;
    line-height: 1.35;
    color: rgba(255, 255, 255, 0.9);
    word-break: break-all;
  }}
  .clip-card-meta {{
    font-size: 9.5px;
    color: rgba(255, 255, 255, 0.38);
    display: flex;
    align-items: center;
    gap: 5px;
  }}
  .pin-icon-btn {{
    position: absolute;
    top: 7px;
    right: 8px;
    color: #61ccff;
    font-size: 10px;
  }}
  .image-thumb-preview {{
    width: 100%;
    height: 70px;
    border-radius: 4px;
    object-fit: cover;
    border: 1px solid rgba(255, 255, 255, 0.12);
  }}
  .image-meta-pill {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 255, 255, 0.1);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9px;
    color: rgba(255, 255, 255, 0.85);
    font-family: monospace;
  }}
  .win-footer {{
    height: 26px;
    background: rgba(0, 0, 0, 0.25);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 0 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 9.5px;
    color: rgba(255, 255, 255, 0.45);
  }}

  /* CURSOR */
  .macos-cursor {{
    position: absolute;
    width: 28px;
    height: 28px;
    pointer-events: none;
    z-index: 1000;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));
  }}

  /* IDE MOCKUP */
  .ide-window {{
    position: absolute;
    width: 780px;
    height: 520px;
    background: #1e1e24;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.7);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}
  .ide-titlebar {{
    height: 38px;
    background: #16161a;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    padding: 0 14px;
    gap: 12px;
  }}
  .window-dots {{
    display: flex;
    gap: 7px;
  }}
  .dot {{
    width: 11px;
    height: 11px;
    border-radius: 50%;
  }}
  .dot-red {{ background: #ff5f56; }}
  .dot-yellow {{ background: #ffbd2e; }}
  .dot-green {{ background: #27c93f; }}
  .ide-tab {{
    background: #1e1e24;
    padding: 5px 14px;
    border-radius: 6px 6px 0 0;
    font-size: 12px;
    color: #e2e8f0;
    display: flex;
    align-items: center;
    gap: 6px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-bottom: none;
  }}
  .ide-body {{
    flex: 1;
    display: flex;
    font-family: "JetBrains Mono", Menlo, Monaco, monospace;
    font-size: 13px;
    line-height: 1.6;
    padding: 16px 0;
  }}
  .line-numbers {{
    width: 48px;
    color: #4b5563;
    text-align: right;
    padding-right: 14px;
  }}
  .code-content {{
    flex: 1;
    color: #d1d5db;
  }}
  .kw {{ color: #f472b6; }}
  .type {{ color: #38bdf8; }}
  .str {{ color: #34d399; }}
  .func {{ color: #fbbf24; }}
  .comment {{ color: #6b7280; }}

  /* PREMIERE PRO MOCKUP */
  .nle-window {{
    position: absolute;
    width: 1040px;
    height: 520px;
    background: #18191d;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 35px 90px rgba(0, 0, 0, 0.75);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}
  .nle-timeline {{
    flex: 1;
    background: #131417;
    display: flex;
    flex-direction: column;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }}
  .nle-track {{
    height: 60px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    align-items: center;
    padding-left: 90px;
    position: relative;
  }}
  .nle-track-header {{
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 85px;
    background: #1c1d22;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    padding-left: 12px;
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
  }}
  .timeline-clip {{
    height: 48px;
    background: #2563eb;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    padding: 0 12px;
    font-size: 11px;
    font-weight: 500;
    color: #fff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  }}

  /* SECURITY SHIELD */
  .shield-container {{
    position: relative;
    width: 220px;
    height: 220px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .shield-ring {{
    position: absolute;
    inset: 0;
    border: 2px dashed rgba(56, 189, 248, 0.4);
    border-radius: 50%;
  }}
  .shield-icon-svg {{
    width: 100px;
    height: 100px;
    color: #38bdf8;
    filter: drop-shadow(0 0 30px rgba(56, 189, 248, 0.6));
  }}

  /* FEATURE PILLS */
  .feature-pill {{
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(56, 189, 248, 0.3);
    backdrop-filter: blur(25px);
    border-radius: 999px;
    padding: 12px 28px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.6), 0 0 30px rgba(56, 189, 248, 0.15);
  }}
  .feature-pill-title {{ font-size: 16px; font-weight: 700; color: #fff; }}
  .feature-pill-sub {{ font-size: 13px; color: #94a3b8; }}

  /* PROLOGUE CARDS */
  .prologue-card {{
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: 480px;
    background: rgba(30, 41, 59, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(20px);
    border-radius: 12px;
    padding: 18px 24px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}

  /* SHORTCUT BADGE */
  .shortcut-badge {{
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(20px);
    border-radius: 999px;
    padding: 10px 24px;
    font-size: 18px;
    font-weight: 600;
    color: #e2e8f0;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255,255,255,0.25);
  }}
  .keycap {{
    background: linear-gradient(180deg, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0.06) 100%);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 6px;
    padding: 3px 10px;
    font-family: -apple-system, monospace;
    font-size: 15px;
    color: #38bdf8;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }}
</style>
</head>
<body>

<div id="stage">
  <!-- Dynamic Caustics -->
  <div class="ambient-glow glow-cyan" id="ambient-cyan"></div>
  <div class="ambient-glow glow-purple" id="ambient-purple"></div>
  <div class="grid-pattern"></div>

  <!-- Technical HUD System Tracker -->
  <div class="hud-banner">
    <div class="system-badge" id="hud-badge">SYSTEM 01 // NATIVE PASTEBOARD OBSERVATION</div>
    <div class="hud-title">ClipBoard for macOS • System Architecture Tour</div>
  </div>

  <!-- Synchronized Subtitles Pill -->
  <div class="subtitle-pill" id="subtitle-pill">
    <div class="subtitle-icon"></div>
    <div class="subtitle-text" id="subtitle-text">
      On macOS, the standard clipboard has a fatal flaw: it only remembers one thing.
    </div>
  </div>

  <!-- ==================== SCENE 1: THE FLAW (0.0s - 10.0s) ==================== -->
  <div class="scene" id="scene-prologue">
    <div class="tagline">The Universal Clipboard Flaw</div>
    <div class="hero-title" style="text-align: center; max-width: 1200px;">
      Why does your clipboard<br>only remember one thing?
    </div>
    <div class="hero-sub" style="text-align: center; max-width: 800px;">
      Copying something new overwrites your previous work. Lost snippets. Lost time.
    </div>

    <div style="position: relative; width: 600px; height: 220px; margin-top: 40px;">
      <div class="prologue-card" id="prologue-card-1" style="top: 0;">
        <div style="font-size: 11px; font-weight: 600; color: #38bdf8;">COPIED TO CLIPBOARD</div>
        <div style="font-family: monospace; font-size: 14px; color: #f8fafc;">
          const API_SECRET = "sk_live_9942a0f8b1...";
        </div>
        <div style="font-size: 11px; color: #64748b;">10:41 AM • 34 characters</div>
      </div>

      <div class="prologue-card" id="prologue-card-2" style="top: 45px; opacity: 0; transform: translateX(-50%) translateY(30px);">
        <div style="font-size: 11px; font-weight: 600; color: #fb7185;">NEW COPY OVERWRITE</div>
        <div style="font-family: monospace; font-size: 14px; color: #f8fafc;">
          "Meeting notes: launch ready for Friday"
        </div>
        <div style="font-size: 11px; color: #fb7185;">Previous snippet permanently lost ⚠️</div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 2: HERO PRODUCT REVEAL (10.0s - 19.5s) ==================== -->
  <div class="scene" id="scene-hero">
    <div style="width: 170px; height: 170px; margin-bottom: 24px;">
      <img src="data:image/png;base64,{appicon_b64}" id="hero-icon" style="width: 100%; height: 100%; border-radius: 38px; box-shadow: 0 35px 80px rgba(0,0,0,0.85), 0 0 50px rgba(56, 189, 248, 0.35);" alt="ClipBoard">
    </div>
    <div class="tagline">Introducing</div>
    <div class="hero-title" style="margin-bottom: 8px;">ClipBoard for macOS.</div>
    <div class="hero-sub" style="text-align: center; margin-top: 4px; margin-bottom: 28px;">
      Infinite history. Zero friction. Crafted for macOS.
    </div>

    <div class="shortcut-badge">
      <span>Global Hotkey:</span>
      <span class="keycap">⌥ Option</span>
      <span>+</span>
      <span class="keycap">V</span>
      <span style="color: #64748b; font-size: 14px; margin-left: 6px;">or ⌘ Shift V</span>
    </div>
  </div>

  <!-- ==================== SCENE 3: CURSOR-ANCHORED UI (19.5s - 29.0s) ==================== -->
  <div class="scene" id="scene-ui-showcase">
    <div style="position: absolute; top: 110px; left: 140px; text-align: left;">
      <div class="tagline">Native macOS Architecture</div>
      <div class="hero-title" style="font-size: 56px;">Opens at your cursor.<br>Stays out of your way.</div>
      <div class="hero-sub" style="font-size: 22px; max-width: 580px; margin-top: 14px;">
        Floating NSPanel with dark acrylic frosted glass backing. Event-reactive 0.25s polling with 0% CPU footprint.
      </div>

      <div style="margin-top: 36px; display: flex; flex-direction: column; gap: 14px;">
        <div class="feature-pill" style="padding: 10px 22px;">
          <div style="font-size: 20px;">⚡</div>
          <div>
            <div class="feature-pill-title">Zero-CPU Monitoring</div>
            <div class="feature-pill-sub">Pasteboard changeCount observation • Zero battery drain</div>
          </div>
        </div>
        <div class="feature-pill" style="padding: 10px 22px;">
          <div style="font-size: 20px;">📌</div>
          <div>
            <div class="feature-pill-title">Permanent Pinning</div>
            <div class="feature-pill-sub">Keep crucial credentials & snippets always at the top</div>
          </div>
        </div>
      </div>
    </div>

    <!-- The Floating Clipboard Window -->
    <div class="clipboard-window" id="showcase-clipboard-window" style="right: 280px; top: 320px;">
      <div class="win-drag-handle"></div>
      <div class="win-tab-bar">
        <div class="tab-group">
          <div class="tab-btn active">
            Clipboard
            <div class="tab-indicator"></div>
          </div>
          <div class="tab-btn">Emojis</div>
        </div>
      </div>

      <div class="win-search-box">
        <span style="color: rgba(255,255,255,0.4);">🔍 Search history...</span>
      </div>

      <div class="win-card-list">
        <div class="section-label pinned">
          📌 PINNED <span style="opacity: 0.5; font-size: 9px; margin-left: auto;">2</span>
        </div>
        <div class="clip-card">
          <div class="accent-bar"></div>
          <div class="pin-icon-btn">📌</div>
          <div class="clip-card-text">#61CCFF (Fluent Cyan Brand Accent)</div>
          <div class="clip-card-meta">10:35 AM • 32 chars</div>
        </div>
        <div class="clip-card">
          <div class="accent-bar"></div>
          <div class="pin-icon-btn">📌</div>
          <div class="clip-card-text">https://github.com/zenrakib/ClipBoard-macOS</div>
          <div class="clip-card-meta">10:38 AM • 45 chars</div>
        </div>

        <div class="section-label recent" style="margin-top: 4px;">⏱ RECENT</div>
        <div class="clip-card">
          <div class="clip-card-image">
            <svg class="image-thumb-preview" viewBox="0 0 300 120" style="background: linear-gradient(135deg, #1e3a8a, #0284c7);">
              <circle cx="60" cy="60" r="30" fill="rgba(255,255,255,0.2)"/>
              <rect x="120" y="40" width="140" height="16" rx="4" fill="rgba(255,255,255,0.4)"/>
            </svg>
            <div style="display: flex; justify-content: space-between;">
              <span class="image-meta-pill">🖼 1920 × 1080</span>
              <span style="font-size: 9px; color: rgba(255,255,255,0.4);">1.4 MB</span>
            </div>
          </div>
        </div>
        <div class="clip-card selected">
          <div class="accent-bar" style="opacity: 1;"></div>
          <div class="clip-card-text" style="font-family: monospace; font-size: 11px;">
            func simulatePasteKeystroke() &#123; ... &#125;
          </div>
          <div class="clip-card-meta">10:44 AM • 38 chars</div>
        </div>
      </div>

      <div class="win-footer">
        <div>Click Paste • Drag to Apps • Esc Close</div>
        <div style="font-weight: 600; color: rgba(255,255,255,0.45);">© zenrakib</div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 4: AUTO-PASTE (29.0s - 38.0s) ==================== -->
  <div class="scene" id="scene-autopaste">
    <div style="position: absolute; top: 90px; text-align: center;">
      <div class="tagline">Universal Auto-Paste Engine</div>
      <div class="hero-title" style="font-size: 60px;">Click once. Pasted in your app.</div>
      <div class="hero-sub" style="font-size: 22px;">
        Automatically restores target app focus and injects Cmd+V with 200ms DOM stabilization.
      </div>
    </div>

    <!-- IDE Window -->
    <div class="ide-window" style="left: 180px; top: 310px;">
      <div class="ide-titlebar">
        <div class="window-dots">
          <div class="dot dot-red"></div>
          <div class="dot dot-yellow"></div>
          <div class="dot dot-green"></div>
        </div>
        <div class="ide-tab">ClipboardService.swift</div>
      </div>
      <div class="ide-body">
        <div class="line-numbers">1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14</div>
        <div class="code-content">
          <span class="kw">import</span> <span class="type">AppKit</span><br>
          <span class="kw">import</span> <span class="type">SwiftUI</span><br><br>
          <span class="comment">// Auto-paste injection target</span><br>
          <span class="kw">final class</span> <span class="type">DeveloperWorkspace</span> &#123;<br>
          &nbsp;&nbsp;<span class="kw">func</span> <span class="func">handleClipboardInsertion</span>() &#123;<br>
          &nbsp;&nbsp;&nbsp;&nbsp;<span class="comment">// Target cursor ready</span><br>
          &nbsp;&nbsp;&nbsp;&nbsp;<span id="ide-pasted-code" style="color: #61ccff; font-weight: 600;"></span><span id="ide-caret" style="border-right: 2px solid #38bdf8; display: inline-block; height: 14px; vertical-align: middle;"></span><br>
          &nbsp;&nbsp;&#125;<br>
          &#125;
        </div>
      </div>
    </div>

    <!-- Mini Floating Panel -->
    <div class="clipboard-window" id="autopaste-clipboard-window" style="right: 220px; top: 330px; transform: scale(1.05);">
      <div class="win-drag-handle"></div>
      <div class="win-tab-bar">
        <div class="tab-btn active">Clipboard</div>
        <div style="font-size: 10px; color: #61ccff;">Auto-Paste Active</div>
      </div>
      <div class="win-card-list">
        <div class="clip-card selected" style="margin-top: 10px;">
          <div class="accent-bar" style="opacity: 1;"></div>
          <div class="clip-card-text" style="font-weight: 600; color: #fff;">
            ClipboardMonitor.shared.copyToPasteboard(item)
          </div>
          <div class="clip-card-meta">Click to Auto-Paste ↵</div>
        </div>
      </div>
      <div class="win-footer">
        <div>Yielding focus to VS Code...</div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 5: DRAG & DROP (38.0s - 48.0s) ==================== -->
  <div class="scene" id="scene-dragdrop">
    <div style="position: absolute; top: 80px; text-align: center;">
      <div class="tagline">Creative Post-Production Workflow</div>
      <div class="hero-title" style="font-size: 58px;">Direct AppKit Drag & Drop.</div>
      <div class="hero-sub" style="font-size: 22px;">
        Drag images, audio & text straight into Premiere Pro, After Effects, Photoshop & Finder.
      </div>
    </div>

    <!-- NLE Video Editor Mockup -->
    <div class="nle-window" style="top: 310px;">
      <div class="ide-titlebar" style="background: #121316;">
        <div class="window-dots">
          <div class="dot dot-red"></div>
          <div class="dot dot-yellow"></div>
          <div class="dot dot-green"></div>
        </div>
        <div style="font-size: 12px; font-weight: 600; color: #94a3b8; margin-left: 10px;">
          Adobe Premiere Pro 2026 — Commercial_Cut_Final.prproj
        </div>
      </div>
      <div class="nle-timeline">
        <div class="nle-track">
          <div class="nle-track-header">Video 2</div>
          <div id="timeline-dropped-clip" class="timeline-clip" style="width: 260px; background: #0284c7; opacity: 0; transform: scale(0.8);">
            🎬 Hero_Design_Render.png
          </div>
        </div>
        <div class="nle-track">
          <div class="nle-track-header">Video 1</div>
          <div class="timeline-clip" style="width: 480px; background: #4338ca;">
            🎥 A-Roll_TalkingHead_4K.mov
          </div>
        </div>
        <div class="nle-track">
          <div class="nle-track-header">Audio 1</div>
          <div class="timeline-clip" style="width: 520px; background: #059669;">
            🎵 Soundtrack_Apple_Master.wav
          </div>
        </div>
      </div>
    </div>

    <!-- Drag source window -->
    <div class="clipboard-window" style="left: 120px; top: 370px; width: 280px; height: 360px;">
      <div class="win-drag-handle"></div>
      <div class="win-card-list">
        <div class="clip-card" style="background: rgba(255,255,255,0.08);">
          <div class="clip-card-image">
            <svg class="image-thumb-preview" viewBox="0 0 300 120" style="background: linear-gradient(135deg, #0284c7, #38bdf8); height: 80px;">
              <rect x="20" y="20" width="260" height="80" rx="6" fill="rgba(255,255,255,0.2)"/>
              <text x="150" y="65" text-anchor="middle" fill="#fff" font-size="16" font-weight="bold">HERO ASSET</text>
            </svg>
            <div style="font-size: 10px; color: #38bdf8; font-weight: 600; margin-top: 4px;">
              Hero_Design_Render.png
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ghost Dragging Item -->
    <div id="drag-ghost" style="position: absolute; pointer-events: none; opacity: 0; z-index: 999; transform: translate(-50%, -50%);">
      <div style="background: rgba(2, 132, 199, 0.9); border: 2px solid #38bdf8; border-radius: 8px; padding: 12px 18px; box-shadow: 0 20px 40px rgba(0,0,0,0.8); display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 18px;">🖼</span>
        <span style="font-weight: 600; font-size: 13px;">Hero_Design_Render.png</span>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 6: PRIVACY SHIELD (48.0s - 58.5s) ==================== -->
  <div class="scene" id="scene-privacy">
    <div class="shield-container">
      <div class="shield-ring"></div>
      <svg class="shield-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
        <path d="m9 12 2 2 4-4"></path>
      </svg>
    </div>

    <div class="tagline" style="margin-top: 24px;">Uncompromising Privacy</div>
    <div class="hero-title" style="font-size: 64px; text-align: center;">
      Passwords Never Saved.
    </div>
    <div class="hero-sub" style="text-align: center; max-width: 820px; font-size: 24px;">
      Automatic suppression for 1Password, Bitwarden, Keychain & concealed types.
    </div>

    <div style="display: flex; gap: 20px; margin-top: 36px;">
      <div class="feature-pill">
        <span style="color: #38bdf8; font-size: 18px;">🔒</span>
        <div>
          <div class="feature-pill-title">Zero Telemetry</div>
          <div class="feature-pill-sub">No network requests. Ever.</div>
        </div>
      </div>
      <div class="feature-pill">
        <span style="color: #34d399; font-size: 18px;">💾</span>
        <div>
          <div class="feature-pill-title">100% On-Device Storage</div>
          <div class="feature-pill-sub">Stored locally in your Application Support</div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 7: EMOJIS (58.5s - 67.0s) ==================== -->
  <div class="scene" id="scene-emojis">
    <div style="position: absolute; top: 100px; text-align: center;">
      <div class="tagline">Integrated Expression Suite</div>
      <div class="hero-title" style="font-size: 60px;">Every Emoji. Every Kaomoji.</div>
      <div class="hero-sub" style="font-size: 22px;">
        Windows 11 inspired expressiveness, built with native Apple smoothness.
      </div>
    </div>

    <div class="clipboard-window" id="emoji-window" style="top: 330px; width: 440px; height: 460px;">
      <div class="win-drag-handle"></div>
      <div class="win-tab-bar">
        <div class="tab-group">
          <div class="tab-btn">Clipboard</div>
          <div class="tab-btn active">
            Emojis
            <div class="tab-indicator" style="left: 10px; right: 10px;"></div>
          </div>
        </div>
      </div>

      <div style="display: flex; gap: 6px; padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.06);">
        <span style="background: #38bdf8; color: #000; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 600;">Smileys</span>
        <span style="background: rgba(255,255,255,0.08); padding: 3px 10px; border-radius: 99px; font-size: 11px;">Gestures</span>
        <span style="background: rgba(255,255,255,0.08); padding: 3px 10px; border-radius: 99px; font-size: 11px;">Objects</span>
        <span style="background: rgba(255,255,255,0.08); padding: 3px 10px; border-radius: 99px; font-size: 11px;">Kaomoji</span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; padding: 18px; font-size: 32px; text-align: center;">
        <div>🚀</div><div>✨</div><div>🔥</div><div>💡</div><div>💻</div><div>⚡</div>
        <div>🎯</div><div>💎</div><div>🎨</div><div>🎉</div><div>🌈</div><div>🪐</div>
      </div>

      <div class="win-footer" style="margin-top: auto;">
        <div>Click to Paste into any text field</div>
        <div>(｡◕‿◕｡) Kaomoji Supported</div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 8: GRAND FINALE (67.0s - 75.0s) ==================== -->
  <div class="scene" id="scene-finale">
    <div style="width: 150px; height: 150px; margin-bottom: 20px;">
      <img src="data:image/png;base64,{appicon_b64}" style="width: 100%; height: 100%; border-radius: 34px; box-shadow: 0 30px 80px rgba(0,0,0,0.8), 0 0 50px rgba(56, 189, 248, 0.4);" alt="ClipBoard">
    </div>
    <div class="hero-title" style="font-size: 76px; margin-bottom: 8px;">ClipBoard</div>
    <div class="hero-sub" style="font-size: 26px; margin-bottom: 28px;">
      The clipboard manager macOS was always meant to have.
    </div>

    <div class="shortcut-badge" style="margin-bottom: 32px;">
      <span>Press</span>
      <span class="keycap">⌥ Option</span>
      <span>+</span>
      <span class="keycap">V</span>
      <span>to trigger anywhere</span>
    </div>

    <div style="text-align: center; color: #94a3b8; font-size: 15px; line-height: 1.6;">
      <div style="font-weight: 600; color: #f1f5f9; letter-spacing: 0.02em;">Created & Crafted by Rakib Hasan</div>
      <div>GitHub: <span style="color: #38bdf8;">@zenrakib</span> • Email: <span style="color: #38bdf8;">zenrakib@gmail.com</span></div>
      <div style="font-size: 12px; margin-top: 6px; color: #64748b;">Free & Open Source under MIT License • 2026</div>
    </div>
  </div>

  <!-- Universal Cursor -->
  <div class="macos-cursor" id="global-cursor" style="opacity: 0;">
    <svg viewBox="0 0 24 24" width="28" height="28" fill="none">
      <path d="M4 3l14 11-6.5.5 3.5 7-3 1.5-3.5-7-4.5 4.5V3z" fill="#000"/>
      <path d="M5.5 5.5l10.5 8.2-5 .4 3.5 7-1.5.8-3.5-7-3.5 3.5V5.5z" fill="#fff"/>
    </svg>
  </div>
</div>

<script>
window.VIDEO = {{
  w: 1920,
  h: 1080,
  duration: 75.0,
  fps: 30
}};

function clamp(x, a = 0, b = 1) {{ return Math.min(b, Math.max(a, x)); }}
function lerp(a, b, t) {{ return a + (b - a) * t; }}
function easeOutQuad(t) {{ return 1 - (1 - t) * (1 - t); }}
function easeInOutCubic(t) {{ return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }}
function easeOutBack(t) {{
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}}
function seg(t, a, b) {{ return clamp((t - a) / (b - a)); }}

const el = id => document.getElementById(id);

// Subtitles Timeline Mapping
const captions = [
  {{ start: 0.0, end: 10.0, badge: "SYSTEM 01 // NATIVE PASTEBOARD OBSERVATION", text: "On macOS, the standard clipboard has a fatal flaw: it only remembers one thing." }},
  {{ start: 10.0, end: 19.5, badge: "SYSTEM 02 // ACCESSORY AGENT & GLOBAL HOTKEYS", text: "Meet ClipBoard for Mac. An ultra-lightweight, zero-CPU clipboard manager engineered for total focus." }},
  {{ start: 19.5, end: 29.0, badge: "SYSTEM 03 // NON-ACTIVATING ACRYLIC NS-PANEL", text: "It opens instantly right at your cursor using dark frosted acrylic glass, featuring permanent pinning & zero CPU." }},
  {{ start: 29.0, end: 38.0, badge: "SYSTEM 04 // SYNTHETIC KEYSTROKE AUTO-PASTE", text: "With the Universal Auto-Paste engine, clicking any snippet restores your app and injects Cmd V in 200 milliseconds." }},
  {{ start: 38.0, end: 48.0, badge: "SYSTEM 05 // APPKIT DRAGGING SOURCE INTEGRATION", text: "For creative pros, native AppKit drag & drop lets you pull images & code directly into Premiere Pro and Finder." }},
  {{ start: 48.0, end: 58.5, badge: "SYSTEM 06 // CONCEALED TYPE ZERO-TELEMETRY SHIELD", text: "Privacy is non-negotiable. Concealed credentials from 1Password and Keychain are automatically suppressed." }},
  {{ start: 58.5, end: 67.0, badge: "SYSTEM 07 // UNICODE EMOJI & KAOMOJI MATRIX", text: "Switch tabs for a complete Windows 11 style Emoji and Kaomoji suite, ready to paste into any document." }},
  {{ start: 67.0, end: 75.0, badge: "SYSTEM 08 // ARCHITECTURE & MIT ATTRIBUTION", text: "ClipBoard for Mac. Crafted with Swift and AppKit by Rakib Hasan. Free and open source." }}
];

window.seek = function(t) {{
  t = clamp(t, 0, window.VIDEO.duration);

  // Update HUD badge & Subtitle
  const currentCap = captions.find(c => t >= c.start && t < c.end) || captions[captions.length - 1];
  el('hud-badge').textContent = currentCap.badge;
  el('subtitle-text').textContent = currentCap.text;

  // Background subtle drift
  const bgDriftX = Math.sin(t * 0.1) * 60;
  const bgDriftY = Math.cos(t * 0.08) * 40;
  el('ambient-cyan').style.transform = `translateX(calc(-50% + ${{bgDriftX}}px)) translateY(${{bgDriftY}}px)`;
  el('ambient-purple').style.transform = `translateX(${{-bgDriftX}}px) translateY(${{-bgDriftY}}px)`;

  el('global-cursor').style.opacity = 0;

  // 1. SCENE PROLOGUE (0.0s - 10.0s)
  const s1In = seg(t, 0.0, 0.8);
  const s1Out = seg(t, 9.2, 10.0);
  const s1Op = (1 - s1Out) * easeOutQuad(s1In);
  el('scene-prologue').style.opacity = s1Op;
  el('scene-prologue').style.transform = `scale(${{lerp(0.96, 1.02, easeInOutCubic(seg(t, 0.0, 9.5)))}})`;

  if (s1Op > 0) {{
    const c1Prog = seg(t, 1.0, 2.0);
    el('prologue-card-1').style.opacity = easeOutQuad(c1Prog);
    el('prologue-card-1').style.transform = `translateX(-50%) translateY(${{lerp(30, 0, easeOutBack(c1Prog))}}px)`;

    if (t >= 4.5) {{
      const c2Prog = seg(t, 4.5, 5.5);
      el('prologue-card-2').style.opacity = easeOutQuad(c2Prog);
      el('prologue-card-2').style.transform = `translateX(-50%) translateY(${{lerp(50, 45, easeOutBack(c2Prog))}}px)`;
      const c1Dissolve = seg(t, 5.0, 6.0);
      el('prologue-card-1').style.filter = `brightness(${{1 - c1Dissolve * 0.4}}) blur(${{c1Dissolve * 6}}px)`;
      el('prologue-card-1').style.opacity = 1 - c1Dissolve * 0.85;
    }}
  }}

  // 2. SCENE HERO (10.0s - 19.5s)
  const s2In = seg(t, 10.0, 10.8);
  const s2Out = seg(t, 18.8, 19.5);
  const s2Op = (1 - s2Out) * easeOutQuad(s2In);
  el('scene-hero').style.opacity = s2Op;

  if (s2Op > 0) {{
    const iconScale = lerp(0.75, 1.0, easeOutBack(seg(t, 10.2, 11.4)));
    const iconFloat = Math.sin((t - 10.0) * 1.8) * 8;
    el('hero-icon').style.transform = `scale(${{iconScale}}) translateY(${{iconFloat}}px)`;
    el('scene-hero').style.transform = `scale(${{lerp(0.97, 1.03, easeInOutCubic(seg(t, 10.0, 19.0)))}})`;
  }}

  // 3. SCENE UI SHOWCASE (19.5s - 29.0s)
  const s3In = seg(t, 19.5, 20.4);
  const s3Out = seg(t, 28.2, 29.0);
  const s3Op = (1 - s3Out) * easeOutQuad(s3In);
  el('scene-ui-showcase').style.opacity = s3Op;

  if (s3Op > 0) {{
    const winProg = seg(t, 20.0, 21.0);
    const winScale = lerp(0.85, 1.0, easeOutBack(winProg));
    const winEl = el('showcase-clipboard-window');
    winEl.style.opacity = easeOutQuad(winProg);
    winEl.style.transform = `scale(${{winScale}})`;

    const camZoom = lerp(1.0, 1.15, easeInOutCubic(seg(t, 21.5, 27.5)));
    el('scene-ui-showcase').style.transform = `scale(${{camZoom}})`;

    const curProg = seg(t, 22.0, 26.0);
    if (curProg > 0 && curProg < 1) {{
      el('global-cursor').style.opacity = 1;
      const curX = lerp(1550, 1420, easeInOutCubic(curProg));
      const curY = lerp(580, 680, easeInOutCubic(curProg));
      el('global-cursor').style.transform = `translate(${{curX}}px, ${{curY}}px)`;
    }}
  }}

  // 4. SCENE AUTO-PASTE (29.0s - 38.0s)
  const s4In = seg(t, 29.0, 29.8);
  const s4Out = seg(t, 37.2, 38.0);
  const s4Op = (1 - s4Out) * easeOutQuad(s4In);
  el('scene-autopaste').style.opacity = s4Op;

  if (s4Op > 0) {{
    el('scene-autopaste').style.transform = `scale(${{lerp(0.98, 1.03, easeInOutCubic(seg(t, 29.0, 37.0)))}})`;

    const clickProg = seg(t, 30.0, 32.2);
    const cursor = el('global-cursor');
    cursor.style.opacity = 1;
    const curX = lerp(1100, 1520, easeInOutCubic(clickProg));
    const curY = lerp(450, 430, easeInOutCubic(clickProg));
    cursor.style.transform = `translate(${{curX}}px, ${{curY}}px) ${{t >= 32.2 && t <= 32.5 ? 'scale(0.85)' : 'scale(1)'}}`;

    const dismissProg = seg(t, 32.4, 33.0);
    const panelEl = el('autopaste-clipboard-window');
    panelEl.style.opacity = 1 - easeOutQuad(dismissProg);
    panelEl.style.transform = `scale(${{lerp(1.05, 0.95, easeOutQuad(dismissProg))}})`;

    const typeProg = seg(t, 33.0, 36.5);
    const fullText = "ClipboardMonitor.shared.copyToPasteboard(item)";
    const charCount = Math.floor(fullText.length * easeInOutCubic(typeProg));
    el('ide-pasted-code').textContent = fullText.substring(0, charCount);
    el('ide-caret').style.opacity = (Math.floor(t * 3) % 2 === 0) ? 1 : 0;
  }}

  // 5. SCENE DRAG & DROP (38.0s - 48.0s)
  const s5In = seg(t, 38.0, 38.8);
  const s5Out = seg(t, 47.2, 48.0);
  const s5Op = (1 - s5Out) * easeOutQuad(s5In);
  el('scene-dragdrop').style.opacity = s5Op;

  if (s5Op > 0) {{
    el('scene-dragdrop').style.transform = `scale(${{lerp(0.98, 1.02, easeInOutCubic(seg(t, 38.0, 47.0)))}})`;

    const dragStart = 40.0;
    const dragEnd = 44.5;
    const dragProg = seg(t, dragStart, dragEnd);

    const startX = 260;
    const startY = 480;
    const endX = 720;
    const endY = 430;

    const curX = lerp(startX, endX, easeInOutCubic(dragProg));
    const curY = lerp(startY, endY, easeInOutCubic(dragProg));

    const cursor = el('global-cursor');
    cursor.style.opacity = 1;
    cursor.style.transform = `translate(${{curX}}px, ${{curY}}px)`;

    const ghost = el('drag-ghost');
    if (t >= dragStart && t < dragEnd) {{
      ghost.style.opacity = 0.9;
      ghost.style.left = `${{curX + 20}}px`;
      ghost.style.top = `${{curY + 15}}px`;
    }} else {{
      ghost.style.opacity = 0;
    }}

    if (t >= dragEnd) {{
      const dropPop = seg(t, dragEnd, dragEnd + 0.6);
      const droppedClip = el('timeline-dropped-clip');
      droppedClip.style.opacity = easeOutQuad(dropPop);
      droppedClip.style.transform = `scale(${{lerp(0.8, 1.0, easeOutBack(dropPop))}})`;
    }}
  }}

  // 6. SCENE PRIVACY (48.0s - 58.5s)
  const s6In = seg(t, 48.0, 48.8);
  const s6Out = seg(t, 57.8, 58.5);
  const s6Op = (1 - s6Out) * easeOutQuad(s6In);
  el('scene-privacy').style.opacity = s6Op;

  if (s6Op > 0) {{
    const shieldProg = seg(t, 48.5, 50.5);
    el('scene-privacy').style.transform = `scale(${{lerp(0.92, 1.03, easeOutBack(shieldProg))}})`;
  }}

  // 7. SCENE EMOJIS (58.5s - 67.0s)
  const s7In = seg(t, 58.5, 59.2);
  const s7Out = seg(t, 66.2, 67.0);
  const s7Op = (1 - s7Out) * easeOutQuad(s7In);
  el('scene-emojis').style.opacity = s7Op;

  if (s7Op > 0) {{
    const emProg = seg(t, 59.0, 60.5);
    el('emoji-window').style.transform = `scale(${{lerp(0.9, 1.0, easeOutBack(emProg))}})`;
    el('scene-emojis').style.transform = `scale(${{lerp(0.98, 1.02, easeInOutCubic(seg(t, 59.0, 66.5)))}})`;
  }}

  // 8. SCENE FINALE (67.0s - 75.0s)
  const s8In = seg(t, 67.0, 67.8);
  const s8Op = easeOutQuad(s8In);
  el('scene-finale').style.opacity = s8Op;

  if (s8Op > 0) {{
    const finaleProg = seg(t, 67.5, 74.0);
    el('scene-finale').style.transform = `scale(${{lerp(0.94, 1.02, easeInOutCubic(finaleProg))}})`;
  }}
}};

window.seek(0);
</script>
</body>
</html>
"""

with open("clipboard_apple_walkthrough.html", "w") as f:
    f.write(html_content)

print(f"Generated clipboard_apple_walkthrough.html successfully! Size: {len(html_content)} bytes")
