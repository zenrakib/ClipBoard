#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# ClipBoard.app Production Packaging Script
# Compiles, bundles, and ad-hoc signs ClipBoard as a standalone macOS agent app.
# Author / Copyright: Rakib Hasan (@zenrakib) <zenrakib@gmail.com>
# ==============================================================================

APP_NAME="ClipBoard"
APP_BUNDLE="${APP_NAME}.app"
BUNDLE_ID="com.zenrakib.clipboard"
VERSION="1.0.1"
SHORT_VERSION="1.0.1"
MIN_MACOS="13.0"

echo "=================================================="
echo "📦 Packaging ${APP_BUNDLE}..."
echo "=================================================="

# Step 1: Compile Universal Release Binary (Apple Silicon arm64 + Intel x86_64)
echo "🔨 Step 1: Compiling universal release binary (arm64 + x86_64)..."
swift build -c release --arch arm64 --arch x86_64

# Locate binary path
BIN_DIR="$(swift build -c release --arch arm64 --arch x86_64 --show-bin-path)"
BIN_PATH="${BIN_DIR}/${APP_NAME}"

if [ ! -f "$BIN_PATH" ]; then
    if [ -f ".build/release/${APP_NAME}" ]; then
        BIN_PATH=".build/release/${APP_NAME}"
    elif [ -f ".build/apple/Products/Release/${APP_NAME}" ]; then
        BIN_PATH=".build/apple/Products/Release/${APP_NAME}"
    elif [ -f ".build/arm64-apple-macosx/release/${APP_NAME}" ]; then
        BIN_PATH=".build/arm64-apple-macosx/release/${APP_NAME}"
    else
        echo "❌ Error: Could not locate compiled binary ${APP_NAME}."
        exit 1
    fi
fi
echo "   ✓ Binary located at: ${BIN_PATH}"

# Step 2: Clean and Set Up Bundle Structure
echo "📂 Step 2: Creating .app bundle structure..."
rm -rf "${APP_BUNDLE}"

MACOS_DIR="${APP_BUNDLE}/Contents/MacOS"
RESOURCES_DIR="${APP_BUNDLE}/Contents/Resources"

mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# Copy binary into bundle
cp "${BIN_PATH}" "${MACOS_DIR}/${APP_NAME}"
chmod +x "${MACOS_DIR}/${APP_NAME}"
echo "   ✓ Installed executable to ${MACOS_DIR}/${APP_NAME}"

# Copy custom macOS app icon if present
if [ -f "AppIcon.icns" ]; then
    cp "AppIcon.icns" "${RESOURCES_DIR}/AppIcon.icns"
    echo "   ✓ Installed custom AppIcon.icns to ${RESOURCES_DIR}/AppIcon.icns"
fi

# Copy software license & copyright notice into bundle
if [ -f "LICENSE" ]; then
    cp "LICENSE" "${RESOURCES_DIR}/LICENSE"
    echo "   ✓ Installed LICENSE to ${RESOURCES_DIR}/LICENSE"
fi

# Step 3: Generate Info.plist
echo "📝 Step 3: Generating Contents/Info.plist..."
cat << EOF > "${APP_BUNDLE}/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>${BUNDLE_ID}</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>${SHORT_VERSION}</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>LSMinimumSystemVersion</key>
    <string>${MIN_MACOS}</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2026 Rakib Hasan (zenrakib) · zenrakib@gmail.com. All rights reserved.</string>
</dict>
</plist>
EOF
echo "   ✓ Created Info.plist with CFBundleIconFile=AppIcon and LSUIElement=true"

# Refresh bundle timestamp for Finder icon recognition
touch "${APP_BUNDLE}"

# Step 4: Ad-Hoc Code Signing
echo "🔐 Step 4: Applying ad-hoc codesign with stable designated identifier..."
codesign --force --deep -s - --identifier "${BUNDLE_ID}" --requirements '=designated => identifier "com.zenrakib.clipboard"' "${APP_BUNDLE}"

echo "🔍 Verifying code signature..."
codesign --verify --deep --strict "${APP_BUNDLE}"
echo "   ✓ Code signature verified successfully!"

# Step 5: Verification & Summary
echo "=================================================="
echo "✅ Successfully created: ${APP_BUNDLE}"
echo "=================================================="
echo ""
echo "App Details:"
echo " - Path:       $(pwd)/${APP_BUNDLE}"
echo " - Executable: $(pwd)/${MACOS_DIR}/${APP_NAME}"
echo " - Bundle ID:  ${BUNDLE_ID}"
echo " - Agent Mode: LSUIElement=true (hidden from Dock & App Switcher)"
echo " - Hotkeys:    ⌥V (Option+V) or ⌘⇧V (Cmd+Shift+V)"
echo ""
echo "Terminal Commands:"
echo " ▶ Launch app: open ${APP_BUNDLE}"
echo " ⏹ Stop app:   pkill -x ${APP_NAME} || true"
echo ""
echo "ℹ️ Accessibility Troubleshooting:"
echo " If auto-paste does not trigger or macOS asks again, reset TCC permissions with:"
echo "   tccutil reset Accessibility ${BUNDLE_ID}"
echo " Then re-enable ClipBoard in System Settings > Privacy & Security > Accessibility."
echo "=================================================="

