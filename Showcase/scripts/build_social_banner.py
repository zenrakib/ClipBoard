import os
import base64
import subprocess

print("Generating ClipBoard Apple-style Social Media Banner...")

# 1. Read AppIcon
with open('AppIcon.png', 'rb') as f:
    app_icon_b64 = 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

# 2. Read Drag/Drop screenshot for sample image card
sample_img_path = 'docs/screenshots/drag_drop_export.jpg'
if not os.path.exists(sample_img_path):
    sample_img_path = 'docs/screenshots/hero_preview.jpg'
with open(sample_img_path, 'rb') as f:
    sample_img_b64 = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('utf-8')

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ClipBoard for macOS — Official Apple Keynote Social Banner</title>
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  body {{
    background: #050608;
    color: #FFFFFF;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
    width: 1920px;
    height: 1080px;
    overflow: hidden;
    position: relative;
    user-select: none;
  }}

  /* Ambient Mesh Background & Gradients */
  .canvas {{
    width: 1920px;
    height: 1080px;
    position: absolute;
    top: 0;
    left: 0;
    background: radial-gradient(ellipse 90% 60% at 50% -10%, #0c1b33 0%, #07090f 50%, #030406 100%);
    overflow: hidden;
  }}

  /* High-end subtle dot grid */
  .grid-bg {{
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
    background-size: 32px 32px;
    opacity: 0.65;
    pointer-events: none;
  }}

  /* Ambient Neon Glow Orbs */
  .glow-orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(140px);
    pointer-events: none;
  }}
  .orb-blue {{
    width: 750px;
    height: 550px;
    background: radial-gradient(circle, rgba(0, 113, 227, 0.28) 0%, rgba(37, 99, 235, 0.08) 60%, transparent 100%);
    top: 180px;
    left: 50%;
    transform: translateX(-50%);
  }}
  .orb-cyan {{
    width: 500px;
    height: 400px;
    background: radial-gradient(circle, rgba(34, 211, 238, 0.18) 0%, transparent 70%);
    bottom: -50px;
    left: 120px;
  }}
  .orb-purple {{
    width: 550px;
    height: 450px;
    background: radial-gradient(circle, rgba(168, 85, 247, 0.16) 0%, transparent 70%);
    top: 250px;
    right: 80px;
  }}

  /* Container */
  .container {{
    position: relative;
    z-index: 10;
    width: 1920px;
    height: 1080px;
    padding: 44px 64px 38px 64px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  /* Top Navigation & Apple Badge Bar */
  .header-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }}
  .brand-pill {{
    display: flex;
    align-items: center;
    gap: 14px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 7px 18px 7px 8px;
    border-radius: 40px;
    backdrop-filter: blur(24px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  }}
  .brand-icon {{
    width: 40px;
    height: 40px;
    border-radius: 9px;
    box-shadow: 0 3px 12px rgba(0, 113, 227, 0.4);
  }}
  .brand-name {{
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: #FFFFFF;
  }}
  .brand-tag {{
    font-size: 12px;
    font-weight: 600;
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.14);
    padding: 3px 9px;
    border-radius: 12px;
    margin-left: 4px;
  }}

  .apple-pill {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.10);
    padding: 8px 18px;
    border-radius: 30px;
    font-size: 12.5px;
    font-weight: 600;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
  }}
  .apple-logo {{
    font-size: 15px;
    color: #FFFFFF;
  }}

  .author-pill {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.10);
    padding: 8px 18px;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(20px);
  }}
  .author-pill b {{
    color: #FFFFFF;
    font-weight: 600;
  }}
  .github-star-badge {{
    background: #0071E3;
    color: #FFF;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 10px;
  }}

  /* Headline Section */
  .hero-titles {{
    text-align: center;
    margin-top: 10px;
    margin-bottom: 24px;
  }}
  .hero-h1 {{
    font-size: 50px;
    font-weight: 800;
    letter-spacing: -1.4px;
    line-height: 1.15;
    background: linear-gradient(180deg, #FFFFFF 30%, #CFE2FE 75%, #93C5FD 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .hero-h1 span.highlight {{
    background: linear-gradient(90deg, #38BDF8 0%, #60A5FA 50%, #A78BFA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .hero-subtitle {{
    font-size: 17.5px;
    font-weight: 400;
    color: rgba(255, 255, 255, 0.68);
    margin-top: 8px;
    letter-spacing: -0.2px;
  }}
  .hero-subtitle strong {{
    color: #FFFFFF;
    font-weight: 600;
  }}

  /* 3-Column Bento Showcase Section */
  .showcase-grid {{
    display: grid;
    grid-template-columns: 390px 620px 390px;
    gap: 32px;
    justify-content: center;
    align-items: stretch;
    flex: 1;
    max-height: 720px;
  }}

  /* Card Styles */
  .glass-card {{
    background: rgba(18, 22, 31, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 20px;
    padding: 22px;
    backdrop-filter: blur(36px);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.12);
    position: relative;
    overflow: hidden;
  }}
  .glass-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  }}

  .col-side {{
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}

  .card-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }}
  .card-icon-box {{
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
  }}
  .icon-blue {{ background: linear-gradient(135deg, #0071E3, #0284C7); color: #FFF; }}
  .icon-emerald {{ background: linear-gradient(135deg, #10B981, #059669); color: #FFF; }}
  .icon-purple {{ background: linear-gradient(135deg, #8B5CF6, #6366F1); color: #FFF; }}
  .icon-amber {{ background: linear-gradient(135deg, #F59E0B, #D97706); color: #FFF; }}

  .card-title {{
    font-size: 17px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: #FFFFFF;
  }}
  .card-desc {{
    font-size: 13px;
    line-height: 1.45;
    color: rgba(255, 255, 255, 0.65);
    margin-bottom: 12px;
  }}

  /* Keycap UI for Global Hotkey Card */
  .keycap-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 10px 14px;
    border-radius: 12px;
  }}
  .keycap {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 36px;
    height: 36px;
    padding: 0 10px;
    background: linear-gradient(180deg, #2D3342 0%, #1A1F2B 100%);
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-bottom: 2px solid rgba(0, 0, 0, 0.6);
    border-radius: 8px;
    font-size: 15px;
    font-weight: 700;
    color: #FFFFFF;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.4);
  }}
  .keycap-label {{
    font-size: 12.5px;
    color: rgba(255, 255, 255, 0.7);
    margin-left: 4px;
  }}

  /* Auto-Paste Workflow Flow Visual */
  .paste-flow-box {{
    background: rgba(0, 0, 0, 0.38);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }}
  .flow-step {{
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 4px;
  }}
  .step-bubble {{
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
  }}
  .step-text {{
    font-size: 10px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.75);
  }}
  .flow-arrow {{
    font-size: 13px;
    color: #38BDF8;
    opacity: 0.8;
  }}

  /* Privacy & 0.0% CPU Metrics */
  .metrics-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }}
  .metric-badge {{
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 8px 10px;
    text-align: center;
  }}
  .metric-val {{
    font-size: 18px;
    font-weight: 800;
    color: #10B981;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
  }}
  .metric-sub {{
    font-size: 10px;
    color: rgba(255, 255, 255, 0.60);
    margin-top: 2px;
  }}

  /* Pro Creative Apps Badges (Premiere, DaVinci, After Effects, Photoshop, Figma) */
  .app-badges-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 10px 8px;
    border-radius: 12px;
    margin-bottom: 8px;
  }}
  .app-pill {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }}
  .app-sq {{
    width: 38px;
    height: 38px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 900;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    border: 1px solid rgba(255, 255, 255, 0.15);
  }}
  .sq-pr {{ background: #00005B; color: #EA77FF; border-color: #EA77FF; }}
  .sq-ae {{ background: #00005B; color: #9999FF; border-color: #9999FF; }}
  .sq-ps {{ background: #001E36; color: #31A8FF; border-color: #31A8FF; }}
  .sq-davinci {{ background: #1A1A1A; color: #FF453A; }}
  .sq-figma {{ background: #2C2C2E; color: #0ACF83; }}
  .app-lbl {{
    font-size: 9px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.70);
  }}

  /* Emoji Showcase Pill */
  .emoji-preview-box {{
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 10px 12px;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .emoji-chips-row {{
    display: flex;
    gap: 6px;
    overflow: hidden;
  }}
  .emoji-chip {{
    font-size: 10px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.85);
  }}
  .emoji-chip.active {{
    background: #0071E3;
    color: #FFF;
  }}
  .emoji-grid-sample {{
    display: flex;
    justify-content: space-between;
    font-size: 20px;
    padding: 4px 6px;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 8px;
  }}

  /* ========================================================== */
  /* CENTERPIECE: ULTRA-REALISTIC FLOATING CLIPBOARD UI MOCKUP  */
  /* ========================================================== */
  .centerpiece-wrapper {{
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
  }}

  .floating-window {{
    width: 580px;
    background: rgba(22, 26, 35, 0.86);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 18px;
    backdrop-filter: blur(48px);
    box-shadow: 0 28px 70px rgba(0, 0, 0, 0.75), 0 0 0 1px rgba(255, 255, 255, 0.12), 0 0 40px rgba(0, 113, 227, 0.20);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  /* Top Drag Pill Handle */
  .window-topbar {{
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px 0 4px 0;
  }}
  .drag-handle-pill {{
    width: 44px;
    height: 4.5px;
    background: rgba(255, 255, 255, 0.28);
    border-radius: 3px;
  }}

  /* Window Header Tabs */
  .window-tabs-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 16px 8px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }}
  .tabs-group {{
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .tab-item {{
    font-size: 13.5px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.50);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    position: relative;
  }}
  .tab-item.active {{
    color: #FFFFFF;
  }}
  .active-dot {{
    width: 4px;
    height: 4px;
    background: #0071E3;
    border-radius: 50%;
    box-shadow: 0 0 6px #0071E3;
  }}
  .window-actions {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.45);
  }}

  /* Search Bar */
  .search-input-box {{
    margin: 8px 14px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 6px 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.40);
  }}

  /* History Cards List */
  .cards-list {{
    padding: 4px 14px 12px 14px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}

  .section-label {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #0071E3;
    padding: 2px 2px;
    margin-top: 2px;
  }}

  /* Minimalist Card */
  .clip-card {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
    display: flex;
    align-items: stretch;
    position: relative;
    overflow: hidden;
  }}
  .clip-card.selected {{
    background: rgba(255, 255, 255, 0.09);
    border-color: rgba(255, 255, 255, 0.18);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
  }}
  .accent-bar {{
    width: 3.5px;
    background: transparent;
    margin: 5px 0;
    border-radius: 2px;
  }}
  .clip-card.selected .accent-bar {{
    background: #0071E3;
    box-shadow: 0 0 8px #0071E3;
  }}

  .card-inner {{
    flex: 1;
    padding: 8px 10px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .card-row-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }}
  .card-text {{
    font-size: 12px;
    line-height: 1.4;
    color: rgba(255, 255, 255, 0.90);
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
  }}
  .code-text {{
    font-family: "SF Mono", Menlo, Consolas, Monaco, monospace;
    font-size: 11px;
    color: #67E8F9;
    background: rgba(0, 0, 0, 0.28);
    padding: 4px 6px;
    border-radius: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .card-meta {{
    font-size: 9.5px;
    color: rgba(255, 255, 255, 0.40);
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .pin-icon {{
    font-size: 11px;
    color: #F59E0B;
    background: rgba(245, 158, 11, 0.15);
    padding: 4px;
    border-radius: 50%;
  }}

  /* Color Swatch Card */
  .color-swatch-box {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .swatch-color {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    background: #0071E3;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }}

  /* Image Thumbnail Card */
  .thumb-preview-box {{
    display: flex;
    gap: 8px;
    align-items: center;
  }}
  .thumb-img {{
    width: 64px;
    height: 42px;
    object-fit: cover;
    border-radius: 5px;
    border: 1px solid rgba(255, 255, 255, 0.15);
  }}

  /* Window Footer */
  .window-footer {{
    padding: 8px 14px;
    background: rgba(0, 0, 0, 0.25);
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 9.5px;
    color: rgba(255, 255, 255, 0.40);
  }}

  /* Drag & Drop Visual Callout Arrow */
  .drag-callout-pill {{
    position: absolute;
    bottom: -18px;
    right: -24px;
    background: linear-gradient(135deg, #0071E3, #38BDF8);
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 20px;
    box-shadow: 0 6px 20px rgba(0, 113, 227, 0.5);
    display: flex;
    align-items: center;
    gap: 6px;
    z-index: 25;
  }}

  /* ========================================================== */
  /* BOTTOM TECH SPECS RIBBON (Apple Hardware Style)            */
  /* ========================================================== */
  .footer-ribbon {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
    margin-top: 12px;
  }}
  .spec-chip {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.09);
    padding: 8px 18px;
    border-radius: 24px;
    font-size: 12.5px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
  }}
  .spec-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 6px #10B981;
  }}

</style>
</head>
<body>

<div class="canvas">
  <div class="grid-bg"></div>
  <div class="glow-orb orb-blue"></div>
  <div class="glow-orb orb-cyan"></div>
  <div class="glow-orb orb-purple"></div>

  <div class="container">

    <!-- 1. HEADER BAR -->
    <div class="header-bar">
      <div class="brand-pill">
        <img class="brand-icon" src="{app_icon_b64}" alt="ClipBoard Icon" />
        <span class="brand-name">ClipBoard</span>
        <span class="brand-tag">v1.0.1</span>
      </div>

      <div class="apple-pill">
        <span class="apple-logo"></span>
        <span>Crafted for macOS Sequoia & Sonoma · Universal M1–M4 & Intel</span>
      </div>

      <div class="author-pill">
        <span>Designed & Developed by <b>Rakib Hasan</b> (@zenrakib)</span>
        <span class="github-star-badge">Open Source MIT</span>
      </div>
    </div>

    <!-- 2. HEADLINE & VALUE PROP -->
    <div class="hero-titles">
      <h1 class="hero-h1">The Clipboard Experience. <span class="highlight">Reimagined for Mac.</span></h1>
      <p class="hero-subtitle">
        Windows 11 <strong>Win + V</strong> simplicity meets Apple Silicon performance. 
        Instant <strong>Auto-Paste</strong>, timeline <strong>Drag & Drop</strong>, and full <strong>Emoji Search</strong> in <strong>0.0% idle CPU</strong>.
      </p>
    </div>

    <!-- 3. MAIN BENTO SHOWCASE GRID -->
    <div class="showcase-grid">

      <!-- LEFT COLUMN: CORE LAUNCH & AUTO-PASTE WORKFLOW -->
      <div class="col-side">

        <!-- Card 1: Global Shortcut -->
        <div class="glass-card">
          <div>
            <div class="card-header">
              <div class="card-icon-box icon-blue">⚡️</div>
              <div class="card-title">Instant Global Hotkey</div>
            </div>
            <div class="card-desc">
              Summon the floating launcher right under your mouse pointer from any app. Press Esc to dismiss smoothly.
            </div>
          </div>
          <div class="keycap-row">
            <span class="keycap">⌥</span>
            <span style="color: rgba(255,255,255,0.4);">+</span>
            <span class="keycap">V</span>
            <span class="keycap-label">Option + V (or ⌘⇧V)</span>
          </div>
        </div>

        <!-- Card 2: 1-Click Auto-Paste -->
        <div class="glass-card">
          <div>
            <div class="card-header">
              <div class="card-icon-box icon-emerald">🚀</div>
              <div class="card-title">1-Click Auto-Paste</div>
            </div>
            <div class="card-desc">
              Zero manual copying. Click any history card and ClipBoard automatically restores focus and simulates ⌘V.
            </div>
          </div>
          <div class="paste-flow-box">
            <div class="flow-step">
              <div class="step-bubble">👆</div>
              <div class="step-text">Click Card</div>
            </div>
            <div class="flow-arrow">➔</div>
            <div class="flow-step">
              <div class="step-bubble">🎯</div>
              <div class="step-text">Focus App</div>
            </div>
            <div class="flow-arrow">➔</div>
            <div class="flow-step">
              <div class="step-bubble" style="background: rgba(16, 185, 129, 0.2); border-color: #10B981; color: #10B981;">⌘V</div>
              <div class="step-text" style="color: #10B981;">Auto-Pasted!</div>
            </div>
          </div>
        </div>

        <!-- Card 3: Privacy Shield & Zero CPU -->
        <div class="glass-card">
          <div>
            <div class="card-header">
              <div class="card-icon-box icon-purple">🔒</div>
              <div class="card-title">Zero CPU & Privacy Shield</div>
            </div>
            <div class="card-desc">
              Event-driven change count monitoring. Password managers (1Password, Bitwarden, Keychain) are strictly suppressed.
            </div>
          </div>
          <div class="metrics-row">
            <div class="metric-badge">
              <div class="metric-val">0.0%</div>
              <div class="metric-sub">Idle CPU Footprint</div>
            </div>
            <div class="metric-badge">
              <div class="metric-val" style="color: #38BDF8;">100%</div>
              <div class="metric-sub">Local & Private</div>
            </div>
          </div>
        </div>

      </div>

      <!-- CENTER: LIFE-SIZED FLOATING CLIPBOARD UI MOCKUP -->
      <div class="centerpiece-wrapper">
        <div class="floating-window">

          <!-- Window Drag Handle -->
          <div class="window-topbar">
            <div class="drag-handle-pill"></div>
          </div>

          <!-- Header Tabs -->
          <div class="window-tabs-bar">
            <div class="tabs-group">
              <div class="tab-item active">
                <span>Clipboard</span>
                <div class="active-dot"></div>
              </div>
              <div class="tab-item">
                <span>Emojis</span>
              </div>
            </div>
            <div class="window-actions">
              <span>Pinned: 2</span>
              <span>•</span>
              <span>🗑️ Clear</span>
            </div>
          </div>

          <!-- Search Bar -->
          <div class="search-input-box">
            <span>🔍</span>
            <span>Search clipboard history or code...</span>
          </div>

          <!-- History Cards -->
          <div class="cards-list">

            <!-- PINNED SECTION -->
            <div class="section-label">
              <span>📌 PINNED FAVORITES</span>
            </div>

            <!-- Pinned Card 1: Swift Code -->
            <div class="clip-card selected">
              <div class="accent-bar"></div>
              <div class="card-inner">
                <div class="card-row-top">
                  <div class="code-text">swift build -c release --arch arm64 --arch x86_64</div>
                  <span class="pin-icon">📌</span>
                </div>
                <div class="card-meta">
                  <span>Terminal Command</span>
                  <span>•</span>
                  <span>Pinned Forever</span>
                  <span>•</span>
                  <span>10:42 AM</span>
                </div>
              </div>
            </div>

            <!-- Pinned Card 2: Color Palette -->
            <div class="clip-card">
              <div class="accent-bar"></div>
              <div class="card-inner">
                <div class="card-row-top">
                  <div class="color-swatch-box">
                    <div class="swatch-color"></div>
                    <span class="card-text" style="font-weight: 600; color: #FFF;">#0071E3 — Apple Cupertino Blue</span>
                  </div>
                  <span class="pin-icon">📌</span>
                </div>
                <div class="card-meta">
                  <span>Design Token</span>
                  <span>•</span>
                  <span>HEX Color</span>
                  <span>•</span>
                  <span>11:15 AM</span>
                </div>
              </div>
            </div>

            <!-- RECENT SECTION -->
            <div class="section-label" style="color: rgba(255,255,255,0.45); margin-top: 4px;">
              <span>🕒 RECENT CLIPS</span>
            </div>

            <!-- Recent Card 1: Copied Image Screenshot (Ready for Drag & Drop) -->
            <div class="clip-card">
              <div class="accent-bar"></div>
              <div class="card-inner">
                <div class="card-row-top">
                  <div class="thumb-preview-box">
                    <img class="thumb-img" src="{sample_img_b64}" alt="Screenshot" />
                    <div>
                      <div class="card-text" style="font-weight: 600;">Hero_Preview_4K_Final.png</div>
                      <div class="card-meta" style="margin-top: 3px;">
                        <span style="background: rgba(255,255,255,0.1); padding: 1px 5px; border-radius: 3px;">1920 × 1080</span>
                        <span>•</span>
                        <span>842 KB PNG</span>
                      </div>
                    </div>
                  </div>
                  <span style="font-size: 11px; opacity: 0.35;">📌</span>
                </div>
              </div>
            </div>

            <!-- Recent Card 2: Text Snippet -->
            <div class="clip-card">
              <div class="accent-bar"></div>
              <div class="card-inner">
                <div class="card-row-top">
                  <div class="card-text">
                    "Ship modern, high-converting fashion apparel & video edits effortlessly with ClipBoard."
                  </div>
                  <span style="font-size: 11px; opacity: 0.35;">📌</span>
                </div>
                <div class="card-meta">
                  <span>Text Snippet</span>
                  <span>•</span>
                  <span>96 chars</span>
                  <span>•</span>
                  <span>Just now</span>
                </div>
              </div>
            </div>

          </div>

          <!-- Window Footer -->
          <div class="window-footer">
            <div>
              <span>Click Paste</span>
              <span style="margin: 0 4px;">•</span>
              <span style="color: #38BDF8; font-weight: 600;">Drag to Apps</span>
              <span style="margin: 0 4px;">•</span>
              <span>Esc Close</span>
            </div>
            <div style="font-weight: 600; color: rgba(255,255,255,0.5);">
              © zenrakib
            </div>
          </div>

        </div>

        <!-- Floating Drag & Drop Callout Pill -->
        <div class="drag-callout-pill">
          <span>✋ Drag directly into Timeline!</span>
          <span style="font-size: 14px;">↘</span>
        </div>

      </div>

      <!-- RIGHT COLUMN: PRO DRAG & DROP + EMOJI LAUNCHER -->
      <div class="col-side">

        <!-- Card 4: Pro Video & Design Drag-and-Drop -->
        <div class="glass-card">
          <div>
            <div class="card-header">
              <div class="card-icon-box icon-blue">🎨</div>
              <div class="card-title">Pro Apps Drag & Drop</div>
            </div>
            <div class="card-desc">
              Drag copied screenshots, graphics, or code straight onto video tracks and canvas layers without saving to disk!
            </div>
          </div>

          <div>
            <div class="app-badges-grid">
              <div class="app-pill">
                <div class="app-sq sq-pr">Pr</div>
                <span class="app-lbl">Premiere</span>
              </div>
              <div class="app-pill">
                <div class="app-sq sq-ae">Ae</div>
                <span class="app-lbl">AfterEffects</span>
              </div>
              <div class="app-pill">
                <div class="app-sq sq-davinci">🎬</div>
                <span class="app-lbl">DaVinci</span>
              </div>
              <div class="app-pill">
                <div class="app-sq sq-ps">Ps</div>
                <span class="app-lbl">Photoshop</span>
              </div>
              <div class="app-pill">
                <div class="app-sq sq-figma">❖</div>
                <span class="app-lbl">Figma</span>
              </div>
            </div>
            <div style="font-size: 11px; color: rgba(255, 255, 255, 0.55); text-align: center;">
              Auto-formats to <code>public.file-url</code> & calibrated sRGB PNG.
            </div>
          </div>
        </div>

        <!-- Card 5: Smart Emoji Engine -->
        <div class="glass-card">
          <div>
            <div class="card-header">
              <div class="card-icon-box icon-amber">😊</div>
              <div class="card-title">Smart Emoji Engine</div>
            </div>
            <div class="card-desc">
              Conversational keyword search finds the right emoji instantly. Wheel-scroll through categories smoothly.
            </div>
          </div>

          <div class="emoji-preview-box">
            <div class="emoji-chips-row">
              <span class="emoji-chip active">Smileys</span>
              <span class="emoji-chip">Gestures</span>
              <span class="emoji-chip">Animals</span>
              <span class="emoji-chip">Objects</span>
            </div>
            <div class="emoji-grid-sample">
              <span>🔥</span>
              <span>🚀</span>
              <span>⚡️</span>
              <span>❤️</span>
              <span>🎉</span>
              <span>✨</span>
              <span>🍕</span>
            </div>
            <div style="font-size: 11px; color: #38BDF8; display: flex; align-items: center; gap: 4px;">
              <span>🔍 Searching "fire"</span>
              <span style="opacity: 0.5;">➔</span>
              <span>Instant Unicode Match</span>
            </div>
          </div>
        </div>

        <!-- Card 6: Permanent Pinning & Organization -->
        <div class="glass-card" style="padding: 16px 20px;">
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-size: 14.5px; font-weight: 700; color: #FFFFFF;">Persistent Local Storage</div>
              <div style="font-size: 11.5px; color: rgba(255,255,255,0.6); margin-top: 2px;">
                Pinned clips survive reboots at <code>~/Library/...</code>
              </div>
            </div>
            <div style="font-size: 22px;">📌</div>
          </div>
        </div>

      </div>

    </div>

    <!-- 4. FOOTER SPECS RIBBON (Apple Hardware Style) -->
    <div class="footer-ribbon">
      <div class="spec-chip">
        <span class="spec-dot"></span>
        <span>Native Swift 5.9 & SwiftUI</span>
      </div>
      <div class="spec-chip">
        <span class="spec-dot" style="background: #38BDF8; box-shadow: 0 0 6px #38BDF8;"></span>
        <span>Universal Binary (Apple Silicon M1–M4 & Intel)</span>
      </div>
      <div class="spec-chip">
        <span class="spec-dot" style="background: #A855F7; box-shadow: 0 0 6px #A855F7;"></span>
        <span>1.8 MB One-Click Standalone Installer</span>
      </div>
      <div class="spec-chip">
        <span class="spec-dot" style="background: #F59E0B; box-shadow: 0 0 6px #F59E0B;"></span>
        <span>github.com/zenrakib/ClipBoard · Free & Open Source</span>
      </div>
    </div>

  </div>
</div>

</body>
</html>
"""

out_html_path = 'Showcase/social_media_banner.html'
with open(out_html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✓ Saved banner HTML to: {out_html_path}")

# 3. Render 1920x1080 screenshot via Google Chrome Headless
chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
out_png_path = "Showcase/ClipBoard_Apple_Social_Banner_1080p.png"
out_jpg_path = "Showcase/ClipBoard_Apple_Social_Banner_1080p.jpg"

abs_html = os.path.abspath(out_html_path)
cmd = [
    chrome_path,
    "--headless",
    "--disable-gpu",
    "--hide-scrollbars",
    f"--window-size=1920,1080",
    f"--screenshot={out_png_path}",
    f"file://{abs_html}"
]

print("Rendering 1920x1080 banner via Headless Chrome...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("Chrome returncode:", res.returncode)

if os.path.exists(out_png_path):
    print(f"✓ Successfully rendered PNG: {out_png_path} ({os.path.getsize(out_png_path)} bytes)")
    # Also convert to high quality JPG for universal social sharing
    subprocess.run(["ffmpeg", "-y", "-i", out_png_path, "-q:v", "2", out_jpg_path], capture_output=True)
    if os.path.exists(out_jpg_path):
        print(f"✓ Successfully converted JPG: {out_jpg_path} ({os.path.getsize(out_jpg_path)} bytes)")
else:
    print("❌ Failed to render PNG with Chrome!")
