#!/usr/bin/env python3
"""
build_apple_saas_video.py
Generates clipboard_apple_video.html:
A premier 1920x1080 Apple-Keynote style SaaS promo & product walkthrough video for ClipBoard for macOS.
"""

import base64
import os

with open("appicon_b64.txt", "r") as f:
    appicon_b64 = f.read().strip()

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ClipBoard for macOS — Apple-Style SaaS Showcase</title>
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
    background: radial-gradient(circle at 50% 35%, #0e1526 0%, #060911 65%, #020306 100%);
    overflow: hidden;
    transform-origin: top left;
  }}

  /* Background Ambient Caustics & Grid */
  .ambient-glow {{
    position: absolute;
    border-radius: 50%;
    filter: blur(140px);
    pointer-events: none;
    opacity: 0.45;
  }}
  .glow-cyan {{
    width: 900px;
    height: 700px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.22) 0%, rgba(30, 58, 138, 0.05) 70%, transparent 100%);
    top: -150px;
    left: 50%;
    transform: translateX(-50%);
  }}
  .glow-purple {{
    width: 800px;
    height: 600px;
    background: radial-gradient(circle, rgba(168, 85, 247, 0.15) 0%, transparent 70%);
    bottom: -100px;
    right: 100px;
  }}

  .grid-pattern {{
    position: absolute;
    inset: 0;
    background-image: 
      linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 60px 60px;
    opacity: 0.6;
    pointer-events: none;
  }}

  /* Global Typography */
  .tagline {{
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.24em;
    color: #38bdf8;
    margin-bottom: 12px;
  }}
  .hero-title {{
    font-size: 82px;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.05;
    background: linear-gradient(180deg, #ffffff 30%, #a1a1aa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .hero-sub {{
    font-size: 32px;
    font-weight: 400;
    color: #94a3b8;
    letter-spacing: -0.015em;
    margin-top: 18px;
    line-height: 1.35;
  }}
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

  /* Scene Wrappers */
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

  /* PROLOGUE SCENE */
  #scene-prologue .prologue-card-container {{
    position: relative;
    width: 600px;
    height: 220px;
    margin-top: 50px;
  }}
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
  .prologue-badge {{
    font-size: 11px;
    font-weight: 600;
    color: #38bdf8;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  /* HERO SCENE */
  #scene-hero .icon-wrapper {{
    position: relative;
    width: 170px;
    height: 170px;
    margin-bottom: 24px;
  }}
  #scene-hero .app-icon {{
    width: 100%;
    height: 100%;
    border-radius: 38px;
    box-shadow: 0 35px 80px rgba(0,0,0,0.85), 0 0 50px rgba(56, 189, 248, 0.35);
  }}

  /* CLIPBOARD REALISTIC UI COMPONENT */
  .clipboard-window {{
    width: 340px;
    height: 440px;
    background: rgba(18, 22, 31, 0.78);
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
  .clear-btn {{
    color: rgba(255, 255, 255, 0.4);
    font-size: 11px;
    padding: 4px;
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
  .win-search-icon {{
    color: rgba(255, 255, 255, 0.4);
    font-size: 11px;
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
  .section-label.pinned {{
    color: #61ccff;
  }}
  .section-label.recent {{
    color: rgba(255, 255, 255, 0.45);
  }}

  .clip-card {{
    position: relative;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 7px 10px 7px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    transition: background 0.15s ease;
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
  .clip-card.selected .accent-bar {{
    opacity: 1;
  }}
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
    color: rgba(255, 255, 255, 0.35);
    font-size: 10px;
  }}
  .pin-icon-btn.active {{
    color: #61ccff;
  }}

  /* Image card */
  .clip-card-image {{
    display: flex;
    flex-direction: column;
    gap: 5px;
  }}
  .image-thumb-preview {{
    width: 100%;
    height: 70px;
    border-radius: 4px;
    object-fit: cover;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: #111;
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

  /* REALISTIC MACOS CURSOR */
  .macos-cursor {{
    position: absolute;
    width: 28px;
    height: 28px;
    pointer-events: none;
    z-index: 1000;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));
  }}

  /* IDE CODE EDITOR MOCKUP */
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
    user-select: none;
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
    animation: rotateSlow 20s linear infinite;
  }}
  .shield-icon-svg {{
    width: 100px;
    height: 100px;
    color: #38bdf8;
    filter: drop-shadow(0 0 30px rgba(56, 189, 248, 0.6));
  }}

  /* FEATURE PILLS & CALLOUTS */
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
  .feature-pill-icon {{
    font-size: 20px;
  }}
  .feature-pill-title {{
    font-size: 16px;
    font-weight: 700;
    color: #fff;
  }}
  .feature-pill-sub {{
    font-size: 13px;
    color: #94a3b8;
  }}

  /* PREVIEW SCRUBBER UI (when not ?render) */
  #preview-bar {{
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px);
    border-radius: 999px;
    padding: 8px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    z-index: 99999;
    box-shadow: 0 10px 40px rgba(0,0,0,0.6);
  }}
  #preview-bar button {{
    background: #38bdf8;
    color: #000;
    border: none;
    border-radius: 999px;
    padding: 6px 16px;
    font-weight: 600;
    cursor: pointer;
  }}
  #scrubber {{
    width: 400px;
    cursor: pointer;
  }}
  #time-display {{
    font-family: monospace;
    font-size: 13px;
    color: #cbd5e1;
    min-width: 90px;
  }}
</style>
</head>
<body>

<div id="stage">
  <!-- Dynamic Ambient Glows -->
  <div class="ambient-glow glow-cyan" id="ambient-cyan"></div>
  <div class="ambient-glow glow-purple" id="ambient-purple"></div>
  <div class="grid-pattern"></div>

  <!-- ==================== SCENE 1: PROLOGUE (0 - 5.0s) ==================== -->
  <div class="scene" id="scene-prologue">
    <div class="tagline" style="opacity: 0.8;">The Universal Clipboard Flaw</div>
    <div class="hero-title" style="text-align: center; max-width: 1200px;">
      Why does your clipboard<br>only remember one thing?
    </div>
    <div class="hero-sub" style="text-align: center; max-width: 800px;">
      Copying something new overwrites your previous work. Lost snippets. Lost time.
    </div>

    <div class="prologue-card-container">
      <!-- Card 1 -->
      <div class="prologue-card" id="prologue-card-1" style="top: 0;">
        <div class="prologue-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
          COPIED TO CLIPBOARD
        </div>
        <div style="font-family: monospace; font-size: 14px; color: #f8fafc;">
          const API_SECRET = "sk_live_9942a0f8b1...";
        </div>
        <div style="font-size: 11px; color: #64748b;">10:41 AM • 34 characters</div>
      </div>

      <!-- Card 2 -->
      <div class="prologue-card" id="prologue-card-2" style="top: 45px; opacity: 0; transform: translateX(-50%) translateY(30px);">
        <div class="prologue-badge" style="color: #fb7185;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
          NEW COPY OVERWRITE
        </div>
        <div style="font-family: monospace; font-size: 14px; color: #f8fafc;">
          "Meeting notes: launch ready for Friday"
        </div>
        <div style="font-size: 11px; color: #fb7185;">Previous snippet permanently lost ⚠️</div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 2: HERO PRODUCT REVEAL (5.0s - 10.5s) ==================== -->
  <div class="scene" id="scene-hero">
    <div class="icon-wrapper">
      <img src="data:image/png;base64,{appicon_b64}" class="app-icon" id="hero-icon" alt="ClipBoard">
    </div>
    <div class="tagline">Introducing</div>
    <div class="hero-title" style="margin-bottom: 8px;">ClipBoard.</div>
    <div class="hero-sub" style="text-align: center; margin-top: 4px; margin-bottom: 28px;">
      Infinite history. Zero friction. Crafted for macOS.
    </div>

    <div class="shortcut-badge" id="hero-shortcut">
      <span>Global Hotkey:</span>
      <span class="keycap">⌥ Option</span>
      <span>+</span>
      <span class="keycap">V</span>
      <span style="color: #64748b; font-size: 14px; margin-left: 6px;">or ⌘ Shift V</span>
    </div>
  </div>

  <!-- ==================== SCENE 3: CURSOR-ANCHORED LAUNCHER & ACRYLIC GLASS (10.5s - 18.0s) ==================== -->
  <div class="scene" id="scene-ui-showcase">
    <!-- Background Desktop Context -->
    <div style="position: absolute; top: 80px; left: 140px; text-align: left;">
      <div class="tagline">Native macOS Architecture</div>
      <div class="hero-title" style="font-size: 56px;">Opens at your cursor.<br>Stays out of your way.</div>
      <div class="hero-sub" style="font-size: 22px; max-width: 580px; margin-top: 14px;">
        Floating NSPanel with dark acrylic frosted glass backing. Event-reactive 0.25s polling with 0% CPU footprint.
      </div>

      <div style="margin-top: 36px; display: flex; flex-direction: column; gap: 14px;">
        <div class="feature-pill" style="padding: 10px 22px;">
          <div class="feature-pill-icon">⚡</div>
          <div>
            <div class="feature-pill-title">Zero-CPU Monitoring</div>
            <div class="feature-pill-sub">Pasteboard changeCount observation • Zero battery drain</div>
          </div>
        </div>
        <div class="feature-pill" style="padding: 10px 22px;">
          <div class="feature-pill-icon">📌</div>
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
          <div class="tab-btn active" id="tab-clip">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
            Clipboard
            <div class="tab-indicator" id="tab-clip-indicator"></div>
          </div>
          <div class="tab-btn" id="tab-emoji">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
            Emojis
          </div>
        </div>
        <div class="clear-btn">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
        </div>
      </div>

      <div class="win-search-box">
        <svg class="win-search-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <span style="color: rgba(255,255,255,0.4);">Search history...</span>
      </div>

      <div class="win-card-list">
        <!-- Pinned Section -->
        <div class="section-label pinned">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/></svg>
          PINNED <span style="opacity: 0.5; font-size: 9px; margin-left: auto;">2</span>
        </div>

        <div class="clip-card" id="card-pinned-1">
          <div class="accent-bar"></div>
          <div class="pin-icon-btn active">📌</div>
          <div class="clip-card-text">#61CCFF (Fluent Cyan Brand Accent)</div>
          <div class="clip-card-meta">10:35 AM • 32 chars</div>
        </div>

        <div class="clip-card" id="card-pinned-2">
          <div class="accent-bar"></div>
          <div class="pin-icon-btn active">📌</div>
          <div class="clip-card-text">https://github.com/zenrakib/ClipBoard-macOS</div>
          <div class="clip-card-meta">10:38 AM • 45 chars</div>
        </div>

        <!-- Recent Section -->
        <div class="section-label recent" style="margin-top: 4px;">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          RECENT
        </div>

        <div class="clip-card" id="card-recent-img">
          <div class="accent-bar"></div>
          <div class="clip-card-image">
            <svg class="image-thumb-preview" viewBox="0 0 300 120" style="background: linear-gradient(135deg, #1e3a8a, #0284c7);">
              <circle cx="60" cy="60" r="30" fill="rgba(255,255,255,0.2)"/>
              <rect x="120" y="40" width="140" height="16" rx="4" fill="rgba(255,255,255,0.4)"/>
              <rect x="120" y="65" width="90" height="12" rx="4" fill="rgba(255,255,255,0.2)"/>
            </svg>
            <div style="display: flex; align-items: center; justify-content: space-between;">
              <span class="image-meta-pill">🖼 1920 × 1080</span>
              <span style="font-size: 9px; color: rgba(255,255,255,0.4);">1.4 MB • 10:42 AM</span>
            </div>
          </div>
        </div>

        <div class="clip-card selected" id="card-recent-code">
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

  <!-- ==================== SCENE 4: UNIVERSAL AUTO-PASTE (18.0s - 25.0s) ==================== -->
  <div class="scene" id="scene-autopaste">
    <div style="position: absolute; top: 70px; text-align: center;">
      <div class="tagline">Universal Auto-Paste</div>
      <div class="hero-title" style="font-size: 60px;">Click once. Pasted in your app.</div>
      <div class="hero-sub" style="font-size: 22px;">
        Automatically restores target app focus and injects Cmd+V with 200ms DOM stabilization.
      </div>
    </div>

    <!-- IDE Mockup (VS Code / Xcode) -->
    <div class="ide-window" id="ide-mockup" style="left: 180px; top: 290px;">
      <div class="ide-titlebar">
        <div class="window-dots">
          <div class="dot dot-red"></div>
          <div class="dot dot-yellow"></div>
          <div class="dot dot-green"></div>
        </div>
        <div class="ide-tab">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
          ClipboardService.swift
        </div>
      </div>
      <div class="ide-body">
        <div class="line-numbers">
          1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14
        </div>
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

    <!-- Mini Floating Panel next to editor -->
    <div class="clipboard-window" id="autopaste-clipboard-window" style="right: 220px; top: 320px; transform: scale(1.05);">
      <div class="win-drag-handle"></div>
      <div class="win-tab-bar">
        <div class="tab-group">
          <div class="tab-btn active">Clipboard</div>
        </div>
        <div style="font-size: 10px; color: #61ccff;">Auto-Paste Active</div>
      </div>
      <div class="win-card-list">
        <div class="clip-card selected" id="autopaste-target-card" style="margin-top: 10px;">
          <div class="accent-bar" style="opacity: 1;"></div>
          <div class="clip-card-text" style="font-weight: 600; color: #fff;">
            ClipboardMonitor.shared.copyToPasteboard(item)
          </div>
          <div class="clip-card-meta">Click to Auto-Paste ↵</div>
        </div>
        <div class="clip-card">
          <div class="clip-card-text">let status = "Production Ready"</div>
        </div>
      </div>
      <div class="win-footer">
        <div>Yielding focus to VS Code...</div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 5: APP-KIT DRAG & DROP (25.0s - 31.5s) ==================== -->
  <div class="scene" id="scene-dragdrop">
    <div style="position: absolute; top: 60px; text-align: center;">
      <div class="tagline">Creative Post-Production Workflow</div>
      <div class="hero-title" style="font-size: 58px;">Direct AppKit Drag & Drop.</div>
      <div class="hero-sub" style="font-size: 22px;">
        Drag images, audio & text straight into Premiere Pro, After Effects, Photoshop & Finder.
      </div>
    </div>

    <!-- NLE Video Editor Mockup -->
    <div class="nle-window" id="nle-mockup" style="top: 290px;">
      <div class="ide-titlebar" style="background: #121316;">
        <div class="window-dots">
          <div class="dot dot-red"></div>
          <div class="dot dot-yellow"></div>
          <div class="dot dot-green"></div>
        </div>
        <div style="font-size: 12px; font-weight: 600; color: #94a3b8; margin-left: 10px;">
          Adobe Premiere Pro 2026 — Project: Commercial_Cut_Final.prproj
        </div>
      </div>
      <div class="nle-timeline">
        <div class="nle-track">
          <div class="nle-track-header">Video 2</div>
          <!-- Target drop destination -->
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

    <!-- Small ClipBoard panel from which drag starts -->
    <div class="clipboard-window" id="drag-clipboard-window" style="left: 120px; top: 350px; width: 280px; height: 360px;">
      <div class="win-drag-handle"></div>
      <div class="win-card-list">
        <div class="clip-card" id="drag-source-card" style="background: rgba(255,255,255,0.08);">
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

    <!-- Ghost Dragging Element -->
    <div id="drag-ghost" style="position: absolute; pointer-events: none; opacity: 0; z-index: 999; transform: translate(-50%, -50%);">
      <div style="background: rgba(2, 132, 199, 0.9); border: 2px solid #38bdf8; border-radius: 8px; padding: 12px 18px; box-shadow: 0 20px 40px rgba(0,0,0,0.8); display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 18px;">🖼</span>
        <span style="font-weight: 600; font-size: 13px;">Hero_Design_Render.png</span>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 6: PRIVACY GUARD (31.5s - 36.5s) ==================== -->
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

  <!-- ==================== SCENE 7: EMOJI SUITE (36.5s - 39.5s) ==================== -->
  <div class="scene" id="scene-emojis">
    <div style="position: absolute; top: 80px; text-align: center;">
      <div class="tagline">Integrated Expression Suite</div>
      <div class="hero-title" style="font-size: 60px;">Every Emoji. Every Kaomoji.</div>
      <div class="hero-sub" style="font-size: 22px;">
        Windows 11 inspired expressiveness, built with native Apple smoothness.
      </div>
    </div>

    <!-- Emojis Window -->
    <div class="clipboard-window" id="emoji-window" style="top: 320px; width: 440px; height: 460px;">
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

      <div style="display: flex; gap: 6px; padding: 10px 12px; overflow-x: hidden; border-bottom: 1px solid rgba(255,255,255,0.06);">
        <span style="background: #38bdf8; color: #000; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 600;">Smileys</span>
        <span style="background: rgba(255,255,255,0.08); padding: 3px 10px; border-radius: 99px; font-size: 11px;">Gestures</span>
        <span style="background: rgba(255,255,255,0.08); padding: 3px 10px; border-radius: 99px; font-size: 11px;">Objects</span>
        <span style="background: rgba(255,255,255,0.08); padding: 3px 10px; border-radius: 99px; font-size: 11px;">Kaomoji</span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; padding: 18px; font-size: 32px; text-align: center;" id="emoji-grid">
        <div class="emoji-cell">🚀</div>
        <div class="emoji-cell">✨</div>
        <div class="emoji-cell">🔥</div>
        <div class="emoji-cell">💡</div>
        <div class="emoji-cell">💻</div>
        <div class="emoji-cell">⚡</div>
        <div class="emoji-cell">🎯</div>
        <div class="emoji-cell">💎</div>
        <div class="emoji-cell">🎨</div>
        <div class="emoji-cell">🎉</div>
        <div class="emoji-cell">🌈</div>
        <div class="emoji-cell">🪐</div>
      </div>

      <div class="win-footer" style="margin-top: auto;">
        <div>Click to Paste into any text field</div>
        <div>(｡◕‿◕｡) Kaomoji Supported</div>
      </div>
    </div>
  </div>

  <!-- ==================== SCENE 8: GRAND FINALE (39.5s - 42.0s) ==================== -->
  <div class="scene" id="scene-finale">
    <div class="icon-wrapper" style="width: 150px; height: 150px; margin-bottom: 20px;">
      <img src="data:image/png;base64,{appicon_b64}" class="app-icon" style="border-radius: 34px;" alt="ClipBoard">
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

  <!-- Universal Animated Cursor -->
  <div class="macos-cursor" id="global-cursor" style="opacity: 0;">
    <svg viewBox="0 0 24 24" width="28" height="28" fill="none">
      <path d="M4 3l14 11-6.5.5 3.5 7-3 1.5-3.5-7-4.5 4.5V3z" fill="#000"/>
      <path d="M5.5 5.5l10.5 8.2-5 .4 3.5 7-1.5.8-3.5-7-3.5 3.5V5.5z" fill="#fff"/>
    </svg>
  </div>
</div>

<!-- Interactive Live Preview Controller -->
<div id="preview-bar">
  <button id="btn-play">Play / Pause</button>
  <input type="range" id="scrubber" min="0" max="42" step="0.05" value="0">
  <span id="time-display">00:00.0 / 00:42.0</span>
</div>

<script>
// ==================== DETERMINISTIC TIME & INTERPOLATION ENGINE ====================
window.VIDEO = {{
  w: 1920,
  h: 1080,
  duration: 42.0,
  fps: 30
}};

function clamp(x, a = 0, b = 1) {{ return Math.min(b, Math.max(a, x)); }}
function lerp(a, b, t) {{ return a + (b - a) * t; }}
function easeOutQuad(t) {{ return 1 - (1 - t) * (1 - t); }}
function easeInOutCubic(t) {{ return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }}
function easeOutExpo(t) {{ return t === 1 ? 1 : 1 - Math.pow(2, -10 * t); }}
function easeOutBack(t) {{
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}}
function spring(t, w = 14, z = 0.82) {{
  if (t <= 0) return 0;
  if (z >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + (z * w / wd) * Math.sin(wd * t));
}}
function seg(t, a, b) {{ return clamp((t - a) / (b - a)); }}

// Hide preview bar in render mode
const isRenderMode = window.location.search.includes('render');
if (isRenderMode) {{
  document.getElementById('preview-bar').style.display = 'none';
}}

// ==================== SCENE ANIMATION LOGIC ====================
const el = id => document.getElementById(id);

window.seek = function(t) {{
  t = clamp(t, 0, window.VIDEO.duration);

  // Background subtle drift
  const bgDriftX = Math.sin(t * 0.15) * 60;
  const bgDriftY = Math.cos(t * 0.12) * 40;
  el('ambient-cyan').style.transform = `translateX(calc(-50% + ${{bgDriftX}}px)) translateY(${{bgDriftY}}px)`;
  el('ambient-purple').style.transform = `translateX(${{-bgDriftX}}px) translateY(${{-bgDriftY}}px)`;

  // Default cursor hidden
  el('global-cursor').style.opacity = 0;

  // ----------------------------------------------------
  // 1. SCENE PROLOGUE (0.0s - 5.2s)
  // ----------------------------------------------------
  const s1In = seg(t, 0.0, 0.8);
  const s1Out = seg(t, 4.5, 5.2);
  const s1Op = (1 - s1Out) * easeOutQuad(s1In);
  el('scene-prologue').style.opacity = s1Op;
  el('scene-prologue').style.transform = `scale(${{lerp(0.96, 1.02, easeInOutCubic(seg(t, 0.0, 5.0)))}})`;

  if (s1Op > 0) {{
    // Card 1 enters at 1.0s
    const c1Prog = seg(t, 0.8, 1.6);
    el('prologue-card-1').style.opacity = easeOutQuad(c1Prog);
    el('prologue-card-1').style.transform = `translateX(-50%) translateY(${{lerp(30, 0, easeOutBack(c1Prog))}}px)`;

    // Card 2 enters at 2.4s and dissolves Card 1
    const c2Prog = seg(t, 2.4, 3.2);
    if (t >= 2.4) {{
      el('prologue-card-2').style.opacity = easeOutQuad(c2Prog);
      el('prologue-card-2').style.transform = `translateX(-50%) translateY(${{lerp(50, 45, easeOutBack(c2Prog))}}px)`;
      // Card 1 turns reddish and fades out
      const c1Dissolve = seg(t, 2.7, 3.4);
      el('prologue-card-1').style.filter = `brightness(${{1 - c1Dissolve * 0.4}}) blur(${{c1Dissolve * 6}}px)`;
      el('prologue-card-1').style.opacity = 1 - c1Dissolve * 0.85;
    }}
  }}

  // ----------------------------------------------------
  // 2. SCENE HERO (5.0s - 10.8s)
  // ----------------------------------------------------
  const s2In = seg(t, 5.0, 5.8);
  const s2Out = seg(t, 10.0, 10.8);
  const s2Op = (1 - s2Out) * easeOutQuad(s2In);
  el('scene-hero').style.opacity = s2Op;

  if (s2Op > 0) {{
    const iconScale = lerp(0.7, 1.0, easeOutBack(seg(t, 5.2, 6.2)));
    const iconFloat = Math.sin((t - 5.0) * 2.0) * 8;
    el('hero-icon').style.transform = `scale(${{iconScale}}) translateY(${{iconFloat}}px)`;
    el('scene-hero').style.transform = `scale(${{lerp(0.97, 1.04, easeInOutCubic(seg(t, 5.0, 10.5)))}})`;

    // Shortcut badge pop
    const badgeProg = seg(t, 7.0, 7.8);
    el('hero-shortcut').style.opacity = easeOutQuad(badgeProg);
    el('hero-shortcut').style.transform = `scale(${{lerp(0.85, 1.0, easeOutBack(badgeProg))}})`;
  }}

  // ----------------------------------------------------
  // 3. SCENE UI SHOWCASE (10.5s - 18.0s)
  // ----------------------------------------------------
  const s3In = seg(t, 10.5, 11.4);
  const s3Out = seg(t, 17.2, 18.0);
  const s3Op = (1 - s3Out) * easeOutQuad(s3In);
  el('scene-ui-showcase').style.opacity = s3Op;

  if (s3Op > 0) {{
    // The clipboard panel springs open at 11.2s right at cursor
    const winProg = seg(t, 11.2, 12.0);
    const winScale = lerp(0.85, 1.0, easeOutBack(winProg));
    const winOp = easeOutQuad(winProg);
    const winEl = el('showcase-clipboard-window');
    winEl.style.opacity = winOp;
    winEl.style.transform = `scale(${{winScale}})`;

    // Camera zooms in smoothly to show the details
    const camZoom = lerp(1.0, 1.15, easeInOutCubic(seg(t, 12.5, 16.5)));
    el('scene-ui-showcase').style.transform = `scale(${{camZoom}})`;

    // Cursor movement over the panel
    const curProg = seg(t, 12.8, 15.0);
    if (curProg > 0 && curProg < 1) {{
      el('global-cursor').style.opacity = 1;
      const curX = lerp(1550, 1420, easeInOutCubic(curProg));
      const curY = lerp(580, 680, easeInOutCubic(curProg));
      el('global-cursor').style.transform = `translate(${{curX}}px, ${{curY}}px)`;
    }}
  }}

  // ----------------------------------------------------
  // 4. SCENE AUTO-PASTE (17.8s - 25.0s)
  // ----------------------------------------------------
  const s4In = seg(t, 17.8, 18.6);
  const s4Out = seg(t, 24.2, 25.0);
  const s4Op = (1 - s4Out) * easeOutQuad(s4In);
  el('scene-autopaste').style.opacity = s4Op;

  if (s4Op > 0) {{
    const camProg = seg(t, 18.0, 24.0);
    el('scene-autopaste').style.transform = `scale(${{lerp(0.98, 1.03, easeInOutCubic(camProg))}})`;

    // Cursor moves towards the target card
    const clickProg = seg(t, 18.6, 20.2);
    const cursor = el('global-cursor');
    cursor.style.opacity = 1;
    const curX = lerp(1100, 1520, easeInOutCubic(clickProg));
    const curY = lerp(450, 430, easeInOutCubic(clickProg));
    cursor.style.transform = `translate(${{curX}}px, ${{curY}}px) ${{t >= 20.2 && t <= 20.4 ? 'scale(0.85)' : 'scale(1)'}}`;

    // At 20.3s, click happens! Panel dismisses
    const dismissProg = seg(t, 20.3, 20.8);
    const panelEl = el('autopaste-clipboard-window');
    panelEl.style.opacity = 1 - easeOutQuad(dismissProg);
    panelEl.style.transform = `scale(${{lerp(1.05, 0.95, easeOutQuad(dismissProg))}})`;

    // At 20.8s, code types out into IDE!
    const typeProg = seg(t, 20.8, 22.8);
    const fullText = "ClipboardMonitor.shared.copyToPasteboard(item)";
    const charCount = Math.floor(fullText.length * easeInOutCubic(typeProg));
    el('ide-pasted-code').textContent = fullText.substring(0, charCount);

    // Blinking caret
    el('ide-caret').style.opacity = (Math.floor(t * 3) % 2 === 0) ? 1 : 0;
  }}

  // ----------------------------------------------------
  // 5. SCENE DRAG & DROP (24.8s - 31.5s)
  // ----------------------------------------------------
  const s5In = seg(t, 24.8, 25.6);
  const s5Out = seg(t, 30.8, 31.5);
  const s5Op = (1 - s5Out) * easeOutQuad(s5In);
  el('scene-dragdrop').style.opacity = s5Op;

  if (s5Op > 0) {{
    el('scene-dragdrop').style.transform = `scale(${{lerp(0.98, 1.02, easeInOutCubic(seg(t, 25.0, 31.0)))}})`;

    // Cursor moves to the image card at 26.2s
    const dragStart = 26.8;
    const dragEnd = 29.2;
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

    // Ghost element follows cursor while dragging
    const ghost = el('drag-ghost');
    if (t >= dragStart && t < dragEnd) {{
      ghost.style.opacity = 0.9;
      ghost.style.left = `${{curX + 20}}px`;
      ghost.style.top = `${{curY + 15}}px`;
    }} else {{
      ghost.style.opacity = 0;
    }}

    // At 29.2s, dropped clip pops into timeline!
    if (t >= dragEnd) {{
      const dropPop = seg(t, dragEnd, dragEnd + 0.5);
      const droppedClip = el('timeline-dropped-clip');
      droppedClip.style.opacity = easeOutQuad(dropPop);
      droppedClip.style.transform = `scale(${{lerp(0.8, 1.0, easeOutBack(dropPop))}})`;
    }}
  }}

  // ----------------------------------------------------
  // 6. SCENE PRIVACY (31.2s - 36.5s)
  // ----------------------------------------------------
  const s6In = seg(t, 31.2, 32.0);
  const s6Out = seg(t, 35.8, 36.5);
  const s6Op = (1 - s6Out) * easeOutQuad(s6In);
  el('scene-privacy').style.opacity = s6Op;

  if (s6Op > 0) {{
    const shieldProg = seg(t, 31.5, 33.0);
    el('scene-privacy').style.transform = `scale(${{lerp(0.92, 1.03, easeOutBack(shieldProg))}})`;
  }}

  // ----------------------------------------------------
  // 7. SCENE EMOJIS (36.2s - 39.5s)
  // ----------------------------------------------------
  const s7In = seg(t, 36.2, 36.8);
  const s7Out = seg(t, 39.0, 39.5);
  const s7Op = (1 - s7Out) * easeOutQuad(s7In);
  el('scene-emojis').style.opacity = s7Op;

  if (s7Op > 0) {{
    const emProg = seg(t, 36.5, 37.5);
    el('emoji-window').style.transform = `scale(${{lerp(0.9, 1.0, easeOutBack(emProg))}})`;
    el('scene-emojis').style.transform = `scale(${{lerp(0.98, 1.02, easeInOutCubic(seg(t, 36.5, 39.5)))}})`;
  }}

  // ----------------------------------------------------
  // 8. SCENE FINALE (39.2s - 42.0s)
  // ----------------------------------------------------
  const s8In = seg(t, 39.2, 40.0);
  const s8Op = easeOutQuad(s8In);
  el('scene-finale').style.opacity = s8Op;

  if (s8Op > 0) {{
    const finaleProg = seg(t, 39.5, 41.5);
    el('scene-finale').style.transform = `scale(${{lerp(0.94, 1.02, easeInOutCubic(finaleProg))}})`;
  }}
}};

// ==================== AUDIO SYNTHESIZER ENGINE ====================
// Pure Web Audio API synthesising Apple keynote music and UI sound effects
window.buildAudio = function(ctx) {{
  const now = 0;

  // Master Gain & Limiter
  const master = ctx.createGain();
  master.gain.value = 0.85;
  master.connect(ctx.destination);

  // Helper: Synthesize an analog warm pad chord
  function playPad(time, dur, freqs, gainLevel = 0.12) {{
    freqs.forEach((f, idx) => {{
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();

      osc.type = 'sawtooth';
      osc2.type = 'sine';
      osc.frequency.setValueAtTime(f, time);
      osc2.frequency.setValueAtTime(f * 1.002, time); // detune

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(450, time);
      filter.frequency.exponentialRampToValueAtTime(1400, time + dur * 0.4);
      filter.frequency.exponentialRampToValueAtTime(500, time + dur);

      gain.gain.setValueAtTime(0.0001, time);
      gain.gain.linearRampToValueAtTime(gainLevel / freqs.length, time + 0.8);
      gain.gain.setValueAtTime(gainLevel / freqs.length, time + dur - 0.8);
      gain.gain.linearRampToValueAtTime(0.0001, time + dur);

      osc.connect(filter);
      osc2.connect(filter);
      filter.connect(gain);
      gain.connect(master);

      osc.start(time);
      osc2.start(time);
      osc.stop(time + dur);
      osc2.stop(time + dur);
    }});
  }}

  // Helper: Tech Arpeggio / Bell Tone
  function playBeep(time, freq, dur = 0.15, vol = 0.05) {{
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
  }}

  // Helper: Soft Kick / Sub impact
  function playKick(time, vol = 0.35) {{
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.frequency.setValueAtTime(140, time);
    osc.frequency.exponentialRampToValueAtTime(45, time + 0.25);

    gain.gain.setValueAtTime(vol, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.35);

    osc.connect(gain);
    gain.connect(master);
    osc.start(time);
    osc.stop(time + 0.35);
  }}

  // Helper: Noise Whoosh
  function playWhoosh(time, dur = 1.0, vol = 0.15) {{
    const bufSize = Math.floor(ctx.sampleRate * dur);
    const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < bufSize; i++) {{
      data[i] = Math.random() * 2 - 1;
    }}
    const src = ctx.createBufferSource();
    src.buffer = buf;

    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.Q.value = 3.0;
    filter.frequency.setValueAtTime(200, time);
    filter.frequency.exponentialRampToValueAtTime(1800, time + dur * 0.5);
    filter.frequency.exponentialRampToValueAtTime(300, time + dur);

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.001, time);
    gain.gain.linearRampToValueAtTime(vol, time + dur * 0.4);
    gain.gain.linearRampToValueAtTime(0.0001, time + dur);

    src.connect(filter);
    filter.connect(gain);
    gain.connect(master);
    src.start(time);
  }}

  // 1. Chords (F major -> C -> D minor -> Bb major)
  // Section 1: Intro
  playPad(0.0, 5.0, [146.83, 220.0, 261.63, 349.23]); // Dm7
  // Section 2: Hero reveal
  playPad(5.0, 5.5, [174.61, 220.0, 261.63, 329.63]); // Fmaj7
  playWhoosh(5.0, 1.2, 0.25);
  playKick(5.5, 0.5);

  // Section 3: UI Showcase
  playPad(10.5, 7.5, [130.81, 196.0, 261.63, 329.63]); // C
  playWhoosh(11.0, 0.8, 0.2);
  playBeep(11.6, 880, 0.1, 0.08); // Glass pop

  // Section 4: Auto-paste
  playPad(18.0, 7.0, [146.83, 220.0, 293.66, 349.23]); // Dm
  playBeep(20.3, 1046.5, 0.08, 0.1); // Click
  for (let k = 0; k < 12; k++) {{
    playBeep(20.8 + k * 0.14, 587.33 + (k % 4) * 60, 0.04, 0.03); // typing ticks
  }}

  // Section 5: Drag & Drop
  playPad(25.0, 6.5, [116.54, 174.61, 233.08, 293.66]); // Bbmaj7
  playWhoosh(27.0, 1.4, 0.18);
  playKick(29.2, 0.4); // Drop impact

  // Section 6: Privacy
  playPad(31.5, 5.0, [146.83, 220.0, 261.63, 392.0]); // Dm9
  playWhoosh(31.5, 1.0, 0.2);

  // Section 7: Emojis
  playPad(36.5, 3.0, [174.61, 220.0, 261.63, 349.23]); // F

  // Section 8: Finale Chime
  playPad(39.5, 2.5, [146.83, 220.0, 293.66, 349.23, 440.0], 0.18); // Grand chord
  playKick(39.8, 0.45);
  playBeep(40.0, 1174.66, 1.5, 0.15); // Celestial bell
  playBeep(40.2, 1760.0, 1.8, 0.12);

  // Rhythmic kick pulses across the core demo
  const kickBeats = [5.5, 7.0, 8.5, 10.0, 11.5, 13.0, 14.5, 16.0, 18.0, 19.5, 21.0, 22.5, 24.0, 25.5, 27.0, 28.5, 30.0, 31.5, 33.0, 34.5, 36.5, 38.0, 39.8];
  kickBeats.forEach(bt => {{
    playKick(bt, 0.28);
    playBeep(bt + 0.375, 1318.5, 0.05, 0.02); // 16th hat/marimba
    playBeep(bt + 0.75, 1760.0, 0.05, 0.02);
  }});
}};

// ==================== LIVE PLAYBACK CONTROLLER ====================
let isPlaying = false;
let startTime = 0;
let pauseOffset = 0;
let audioCtx = null;

const btnPlay = el('btn-play');
const scrubber = el('scrubber');
const timeDisplay = el('time-display');

function formatTime(s) {{
  const m = Math.floor(s / 60);
  const sec = (s % 60).toFixed(1);
  return `${{String(m).padStart(2, '0')}}:${{String(sec).padStart(4, '0')}}`;
}}

function updateLoop() {{
  if (isPlaying) {{
    const current = (audioCtx.currentTime - startTime) + pauseOffset;
    if (current >= window.VIDEO.duration) {{
      isPlaying = false;
      pauseOffset = 0;
      window.seek(0);
      btnPlay.textContent = 'Play';
    }} else {{
      window.seek(current);
      scrubber.value = current;
      timeDisplay.textContent = `${{formatTime(current)}} / ${{formatTime(window.VIDEO.duration)}}`;
      requestAnimationFrame(updateLoop);
    }}
  }}
}}

btnPlay.addEventListener('click', async () => {{
  if (!audioCtx) {{
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    window.buildAudio(audioCtx);
  }}

  if (isPlaying) {{
    isPlaying = false;
    pauseOffset += audioCtx.currentTime - startTime;
    btnPlay.textContent = 'Play';
  }} else {{
    isPlaying = true;
    startTime = audioCtx.currentTime;
    btnPlay.textContent = 'Pause';
    requestAnimationFrame(updateLoop);
  }}
}});

scrubber.addEventListener('input', e => {{
  const t = parseFloat(e.target.value);
  pauseOffset = t;
  if (audioCtx) startTime = audioCtx.currentTime;
  window.seek(t);
  timeDisplay.textContent = `${{formatTime(t)}} / ${{formatTime(window.VIDEO.duration)}}`;
}});

// Initialize at t=0
window.seek(0);
</script>
</body>
</html>
"""

with open("clipboard_apple_video.html", "w") as f:
    f.write(html_content)

print(f"Generated clipboard_apple_video.html successfully! Size: {len(html_content)} bytes")
