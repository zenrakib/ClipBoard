import os
import base64
import subprocess

print("Creating 1200x630 Social Card for Twitter / LinkedIn / OpenGraph...")

with open('AppIcon.png', 'rb') as f:
    app_icon_b64 = 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

sample_img_path = 'docs/screenshots/drag_drop_export.jpg'
with open(sample_img_path, 'rb') as f:
    sample_img_b64 = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('utf-8')

html_card = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ClipBoard for macOS — Twitter/LinkedIn Social Card (1200x630)</title>
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
  }}

  body {{
    background: #040507;
    color: #FFFFFF;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
    width: 1200px;
    height: 630px;
    overflow: hidden;
    position: relative;
    user-select: none;
  }}

  .canvas {{
    width: 1200px;
    height: 630px;
    position: absolute;
    top: 0;
    left: 0;
    background: radial-gradient(ellipse 95% 70% at 50% -10%, #0d2140 0%, #070912 55%, #030406 100%);
    overflow: hidden;
  }}

  .grid-bg {{
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
    background-size: 24px 24px;
    opacity: 0.60;
  }}

  .glow-orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    pointer-events: none;
  }}
  .orb-blue {{
    width: 550px;
    height: 380px;
    background: radial-gradient(circle, rgba(0, 113, 227, 0.35) 0%, transparent 70%);
    top: 100px;
    left: 50%;
    transform: translateX(-50%);
  }}
  .orb-cyan {{
    width: 350px;
    height: 250px;
    background: radial-gradient(circle, rgba(34, 211, 238, 0.18) 0%, transparent 70%);
    bottom: -30px;
    left: 40px;
  }}

  .container {{
    position: relative;
    z-index: 10;
    width: 1200px;
    height: 630px;
    padding: 28px 44px 24px 44px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  .header-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }}
  .brand-pill {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.14);
    padding: 5px 14px 5px 7px;
    border-radius: 30px;
    backdrop-filter: blur(20px);
  }}
  .brand-icon {{
    width: 30px;
    height: 30px;
    border-radius: 7px;
  }}
  .brand-name {{
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
  }}
  .brand-tag {{
    font-size: 10px;
    font-weight: 700;
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.16);
    padding: 2px 7px;
    border-radius: 8px;
  }}

  .apple-pill {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.85);
  }}

  .author-pill {{
    font-size: 11.5px;
    color: rgba(255, 255, 255, 0.70);
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    padding: 6px 14px;
    border-radius: 20px;
  }}
  .author-pill b {{ color: #FFF; }}

  /* Titles */
  .hero-titles {{
    text-align: center;
    margin-top: 4px;
    margin-bottom: 14px;
  }}
  .hero-h1 {{
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -0.9px;
    line-height: 1.15;
    background: linear-gradient(180deg, #FFFFFF 30%, #BFDBFE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .hero-h1 span.highlight {{
    background: linear-gradient(90deg, #38BDF8 0%, #60A5FA 50%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .hero-subtitle {{
    font-size: 13.5px;
    color: rgba(255, 255, 255, 0.70);
    margin-top: 4px;
  }}

  /* Bento 3 Column */
  .showcase-grid {{
    display: grid;
    grid-template-columns: 270px 480px 270px;
    gap: 20px;
    justify-content: center;
    align-items: stretch;
    flex: 1;
    max-height: 410px;
  }}

  .glass-card {{
    background: rgba(18, 22, 32, 0.80);
    border: 1px solid rgba(255, 255, 255, 0.11);
    border-radius: 14px;
    padding: 14px;
    backdrop-filter: blur(30px);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  }}

  .col-side {{
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  .card-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
  }}
  .card-icon-box {{
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }}
  .icon-blue {{ background: linear-gradient(135deg, #0071E3, #0284C7); color: #FFF; }}
  .icon-emerald {{ background: linear-gradient(135deg, #10B981, #059669); color: #FFF; }}
  .icon-purple {{ background: linear-gradient(135deg, #8B5CF6, #6366F1); color: #FFF; }}

  .card-title {{
    font-size: 13px;
    font-weight: 700;
    color: #FFFFFF;
  }}
  .card-desc {{
    font-size: 11px;
    line-height: 1.35;
    color: rgba(255, 255, 255, 0.65);
    margin-bottom: 6px;
  }}

  .keycap-row {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 0, 0, 0.40);
    padding: 6px 10px;
    border-radius: 8px;
  }}
  .keycap {{
    padding: 2px 7px;
    background: #252B3B;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 6px;
    font-size: 12px;
    font-weight: 800;
  }}
  .keycap-label {{
    font-size: 11px;
    color: rgba(255, 255, 255, 0.70);
  }}

  /* App Badges */
  .app-badges-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 6px;
    background: rgba(0, 0, 0, 0.40);
    padding: 7px 4px;
    border-radius: 10px;
    margin-bottom: 4px;
  }}
  .app-sq {{
    width: 32px;
    height: 32px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 900;
  }}
  .sq-pr {{ background: #00005B; color: #EA77FF; }}
  .sq-ae {{ background: #00005B; color: #9999FF; }}
  .sq-ps {{ background: #001E36; color: #31A8FF; }}
  .sq-davinci {{ background: #1C1C1E; color: #FF453A; }}
  .sq-figma {{ background: #242426; color: #0ACF83; }}

  /* Centerpiece Mockup */
  .floating-window {{
    width: 480px;
    background: rgba(22, 26, 36, 0.88);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 14px;
    backdrop-filter: blur(40px);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.80), 0 0 35px rgba(0, 113, 227, 0.25);
    overflow: hidden;
  }}
  .window-topbar {{
    display: flex;
    justify-content: center;
    padding: 6px 0 3px 0;
  }}
  .drag-handle-pill {{
    width: 38px;
    height: 4px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
  }}
  .window-tabs-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 2px 14px 6px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    font-size: 12px;
    font-weight: 600;
  }}
  .tab-item.active {{ color: #FFF; }}
  .active-dot {{
    width: 4px;
    height: 4px;
    background: #0071E3;
    border-radius: 50%;
    margin-top: 2px;
  }}

  .cards-list {{
    padding: 6px 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .clip-card {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 7px;
    padding: 6px 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .clip-card.selected {{
    background: rgba(255, 255, 255, 0.09);
    border-color: #0071E3;
  }}
  .code-text {{
    font-family: monospace;
    font-size: 9.5px;
    color: #67E8F9;
  }}
  .card-meta {{
    font-size: 8.5px;
    color: rgba(255, 255, 255, 0.40);
  }}

  /* Footer Ribbon */
  .footer-ribbon {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    margin-top: 6px;
  }}
  .spec-chip {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
  }}
  .spec-dot {{
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #10B981;
  }}
</style>
</head>
<body>

<div class="canvas">
  <div class="grid-bg"></div>
  <div class="glow-orb orb-blue"></div>
  <div class="glow-orb orb-cyan"></div>

  <div class="container">
    <!-- Header -->
    <div class="header-bar">
      <div class="brand-pill">
        <img class="brand-icon" src="{app_icon_b64}" />
        <span class="brand-name">ClipBoard</span>
        <span class="brand-tag">v1.0.1</span>
      </div>

      <div class="apple-pill">
        <span> Universal for macOS · Apple Silicon & Intel</span>
      </div>

      <div class="author-pill">
        <span>By <b>Rakib Hasan</b> (@zenrakib)</span>
      </div>
    </div>

    <!-- Title -->
    <div class="hero-titles">
      <h1 class="hero-h1">The Clipboard Experience. <span class="highlight">Reimagined for Mac.</span></h1>
      <p class="hero-subtitle">
        Win + V simplicity meets Apple Silicon performance. Instant Auto-Paste & Pro Drag & Drop.
      </p>
    </div>

    <!-- Grid -->
    <div class="showcase-grid">
      <!-- Left -->
      <div class="col-side">
        <div class="glass-card">
          <div>
            <div class="card-header">
              <div class="card-icon-box icon-blue">⚡️</div>
              <div class="card-title">Instant Global Hotkey</div>
            </div>
            <div class="card-desc">Press ⌥V anywhere to open under cursor.</div>
          </div>
          <div class="keycap-row">
            <span class="keycap">⌥</span>
            <span>+</span>
            <span class="keycap">V</span>
            <span class="keycap-label">Option + V</span>
          </div>
        </div>

        <div class="glass-card">
          <div>
            <div class="card-header">
              <div class="card-icon-box icon-emerald">🚀</div>
              <div class="card-title">1-Click Auto-Paste</div>
            </div>
            <div class="card-desc">Click any item and ClipBoard synthesizes ⌘V automatically.</div>
          </div>
          <div style="font-size: 11px; color: #10B981; font-weight: 700;">Zero manual copying needed!</div>
        </div>

        <div class="glass-card">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-size: 14px; font-weight: 800; color: #10B981;">0.0% CPU</div>
              <div style="font-size: 10px; color: rgba(255,255,255,0.6);">Zero idle battery drain</div>
            </div>
            <div style="font-size: 18px;">🔒</div>
          </div>
        </div>
      </div>

      <!-- Center -->
      <div style="display: flex; justify-content: center; align-items: center;">
        <div class="floating-window">
          <div class="window-topbar"><div class="drag-handle-pill"></div></div>
          <div class="window-tabs-bar">
            <div style="display: flex; gap: 14px; align-items: center;">
              <div style="display: flex; flex-direction: column; align-items: center;">
                <span class="tab-item active">Clipboard</span>
                <div class="active-dot"></div>
              </div>
              <span style="color: rgba(255,255,255,0.45);">Emojis</span>
            </div>
            <span style="color: rgba(255,255,255,0.4); font-size: 10.5px;">Pinned: 2</span>
          </div>

          <div class="cards-list">
            <div style="font-size: 9px; font-weight: 700; color: #0071E3;">📌 PINNED FAVORITES</div>
            
            <div class="clip-card selected">
              <div>
                <div class="code-text">swift build -c release --arch arm64</div>
                <div class="card-meta">Terminal Command • Pinned Forever</div>
              </div>
              <span>📌</span>
            </div>

            <div class="clip-card">
              <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 14px; height: 14px; border-radius: 3px; background: #0071E3;"></div>
                <div style="font-size: 11px; font-weight: 600;">#0071E3 — Cupertino Blue</div>
              </div>
              <span>📌</span>
            </div>

            <div style="font-size: 9px; font-weight: 700; color: rgba(255,255,255,0.4); margin-top: 2px;">🕒 RECENT CLIPS</div>

            <div class="clip-card">
              <div style="display: flex; align-items: center; gap: 6px;">
                <img src="{sample_img_b64}" style="width: 38px; height: 26px; border-radius: 4px; object-fit: cover;" />
                <div>
                  <div style="font-size: 11px; font-weight: 600;">Hero_Preview_4K.png</div>
                  <div class="card-meta">1920 × 1080 • 842 KB</div>
                </div>
              </div>
              <span style="opacity: 0.3; font-size: 10px;">📌</span>
            </div>

            <div class="clip-card">
              <div>
                <div style="font-size: 10.5px;">"Ship modern, high-converting video edits effortlessly."</div>
                <div class="card-meta">Text Snippet • Just now</div>
              </div>
              <span style="opacity: 0.3; font-size: 10px;">📌</span>
            </div>
          </div>

          <div style="padding: 6px 12px; background: rgba(0,0,0,0.3); border-top: 1px solid rgba(255,255,255,0.06); font-size: 9px; color: rgba(255,255,255,0.45); display: flex; justify-content: space-between;">
            <span>Click Paste • Drag to Apps</span>
            <span>© zenrakib</span>
          </div>
        </div>
      </div>

      <!-- Right -->
      <div class="col-side">
        <div class="glass-card">
          <div>
            <div class="card-header">
              <div class="card-icon-box icon-blue">🎨</div>
              <div class="card-title">Pro Apps Drag & Drop</div>
            </div>
            <div class="card-desc">Drag photos straight to video tracks & canvas layers.</div>
          </div>
          <div class="app-badges-grid">
            <div class="app-sq sq-pr">Pr</div>
            <div class="app-sq sq-ae">Ae</div>
            <div class="app-sq sq-davinci">🎬</div>
            <div class="app-sq sq-ps">Ps</div>
            <div class="app-sq sq-figma">❖</div>
          </div>
        </div>

        <div class="glass-card">
          <div>
            <div class="card-header">
              <div class="card-icon-box icon-purple">😊</div>
              <div class="card-title">Smart Emoji Search</div>
            </div>
            <div class="card-desc">Search by keyword ("fire", "love", "lol").</div>
          </div>
          <div style="font-size: 16px; display: flex; justify-content: space-between;">
            <span>🔥</span><span>🚀</span><span>⚡️</span><span>❤️</span><span>🎉</span>
          </div>
        </div>

        <div class="glass-card">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-size: 12px; font-weight: 700;">1.8 MB Installer</div>
              <div style="font-size: 9.5px; color: rgba(255,255,255,0.6);">Standalone & 100% Free</div>
            </div>
            <div style="font-size: 18px;">📦</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer-ribbon">
      <div class="spec-chip"><span class="spec-dot"></span><span>Native Swift 5.9</span></div>
      <div class="spec-chip"><span class="spec-dot" style="background:#38BDF8;"></span><span>Universal Apple Silicon & Intel</span></div>
      <div class="spec-chip"><span class="spec-dot" style="background:#F59E0B;"></span><span>github.com/zenrakib/ClipBoard</span></div>
    </div>
  </div>
</div>

</body>
</html>
"""

html_card_path = "Showcase/social_media_card_1200x630.html"
with open(html_card_path, "w", encoding="utf-8") as f:
    f.write(html_card)

chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
png_630p = "Showcase/ClipBoard_Apple_Social_Card_Twitter_1200x630.png"
jpg_630p = "Showcase/ClipBoard_Apple_Social_Card_Twitter_1200x630.jpg"
abs_html_630p = os.path.abspath(html_card_path)

subprocess.run([
    chrome_path, "--headless", "--disable-gpu", "--hide-scrollbars",
    "--window-size=1200,630", f"--screenshot={png_630p}", f"file://{abs_html_630p}"
], check=True)
subprocess.run(["ffmpeg", "-y", "-i", png_630p, "-q:v", "2", jpg_630p], check=True)
print(f"✓ 1200x630 Social Card rendered: {png_630p}")

# Copy to Desktop
subprocess.run(["cp", jpg_630p, "/Users/rakibhasan/Desktop/ClipBoard-Apple-Social-Card-1200x630.jpg"], check=True)
subprocess.run(["cp", png_630p, "/Users/rakibhasan/Desktop/ClipBoard-Apple-Social-Card-1200x630.png"], check=True)
print("✓ Copied 1200x630 to Desktop!")
