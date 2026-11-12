//
//  ClipBoardApp.swift
//  ClipBoard for macOS
//
//  Copyright © 2026 Rakib Hasan (@zenrakib) <zenrakib@gmail.com>. All rights reserved.
//  See LICENSE file for details.
//

import SwiftUI
import AppKit

// MARK: - Application Delegate

/// Coordinates the lifecycle of background monitoring, global hotkeys, floating panel, and auto-paste orchestration.
@MainActor
final class AppDelegate: NSObject, NSApplicationDelegate {

    // MARK: - Core Components

    public private(set) var monitor: ClipboardMonitor!
    public private(set) var panel: FloatingPanel!
    public private(set) var autoPaster: AutoPaster!
    public private(set) var hotkeyManager: HotkeyManager!

    // MARK: - Lifecycle

    func applicationDidFinishLaunching(_ notification: Notification) {
        // 1. Run cleanly as a background agent without a Dock icon (LSUIElement behavior)
        NSApp.setActivationPolicy(.accessory)
        if let appIcon = Bundle.main.image(forResource: "AppIcon") {
            NSApp.applicationIconImage = appIcon
        }

        // 2. Prompt for Accessibility permission on first launch if not yet granted
        if !PermissionManager.shared.isAccessibilityGranted() {
            PermissionManager.shared.requestAccessibilityPermission()
        }

        // 3. Automatically enable Launch at Startup on first run so the app keeps running across reboots
        if !UserDefaults.standard.bool(forKey: "hasConfiguredLaunchAtLogin") {
            LaunchAtLoginManager.shared.enableLaunchAtLogin()
            UserDefaults.standard.set(true, forKey: "hasConfiguredLaunchAtLogin")
        }

        // 4. Initialize ClipboardMonitor and start 0.25s zero-CPU polling (capturing existing clipboard)
        monitor = ClipboardMonitor(captureCurrentOnStart: true)

        // 4. Instantiate FloatingPanel with dynamic, reactive ClipboardLiveView
        let liveView = ClipboardLiveView(
            monitor: monitor,
            onTogglePin: { [weak self] item in
                self?.monitor.togglePin(item: item)
            },
            onSelect: { [weak self] item in
                self?.autoPaster.pasteItem(item)
            }
        )
        panel = FloatingPanel(
            contentRect: NSRect(x: 0, y: 0, width: 340, height: 440),
            rootView: liveView
        )

        // 5. Initialize AutoPaster
        autoPaster = AutoPaster(monitor: monitor, panel: panel)

        // 6. Register global hotkeys (Option + V and Cmd + Shift + V)
        hotkeyManager = HotkeyManager()
        hotkeyManager.registerDefaultHotkeys { [weak self] in
            self?.toggleLauncher()
        }
    }

    // MARK: - Actions

    /// Toggles the floating clipboard launcher panel near the cursor.
    public func toggleLauncher() {
        if panel.isVisible {
            panel.dismiss()
        } else {
            autoPaster.triggerLauncher()
        }
    }

    /// Clears the clipboard history stack.
    public func clearHistory() {
        monitor.clear()
    }

    /// Presents the standard macOS About panel showing developer license and attribution.
    public func showAboutPanel() {
        if #available(macOS 14.0, *) {
            NSApp.activate()
        } else {
            NSApp.activate(ignoringOtherApps: true)
        }
        let credits = NSAttributedString(
            string: "Created & Licensed by Rakib Hasan\nUsername: zenrakib\nEmail: zenrakib@gmail.com\n\nAll Rights Reserved.",
            attributes: [
                .font: NSFont.systemFont(ofSize: 11),
                .foregroundColor: NSColor.secondaryLabelColor
            ]
        )
        NSApp.orderFrontStandardAboutPanel(options: [
            .applicationName: "ClipBoard",
            .applicationVersion: "1.0.0",
            .credits: credits,
            NSApplication.AboutPanelOptionKey(rawValue: "Copyright"): "Copyright © 2026 Rakib Hasan (zenrakib). All rights reserved."
        ])
    }
}

// MARK: - SwiftUI App Entry Point

@main
struct ClipBoardApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    private static let menuBarIcon: NSImage = makeMenuBarIcon()

    private static func makeMenuBarIcon() -> NSImage {
        let img = NSImage(size: NSSize(width: 18, height: 18), flipped: true) { _ in
            guard let cg = NSGraphicsContext.current?.cgContext else { return false }

            // 1. Clipboard U-frame silhouette
            let p = CGMutablePath()
            p.move(to: CGPoint(x: 13.8, y: 8.6))
            p.addLine(to: CGPoint(x: 13.8, y: 6.2))
            p.addArc(tangent1End: CGPoint(x: 13.8, y: 4.2), tangent2End: CGPoint(x: 11.8, y: 4.2), radius: 2.0)
            p.addLine(to: CGPoint(x: 5.5, y: 4.2))
            p.addArc(tangent1End: CGPoint(x: 3.5, y: 4.2), tangent2End: CGPoint(x: 3.5, y: 6.2), radius: 2.0)
            p.addLine(to: CGPoint(x: 3.5, y: 13.2))
            p.addArc(tangent1End: CGPoint(x: 3.5, y: 15.2), tangent2End: CGPoint(x: 5.5, y: 15.2), radius: 2.0)
            p.addLine(to: CGPoint(x: 8.2, y: 15.2))

            cg.setStrokeColor(CGColor(gray: 0, alpha: 1))
            cg.setLineCap(.round)
            cg.setLineJoin(.round)
            cg.setLineWidth(1.8)
            cg.addPath(p)
            cg.strokePath()

            // 2. Top clip
            let clip = CGPath(roundedRect: CGRect(x: 6.4, y: 2.2, width: 4.5, height: 3.2), cornerWidth: 0.9, cornerHeight: 0.9, transform: nil)
            cg.setFillColor(CGColor(gray: 0, alpha: 1))
            cg.addPath(clip)
            cg.fillPath()

            // 3. Dash pill inside
            let dash = CGPath(roundedRect: CGRect(x: 5.3, y: 11.4, width: 3.0, height: 1.3), cornerWidth: 0.65, cornerHeight: 0.65, transform: nil)
            cg.addPath(dash)
            cg.fillPath()

            // 4. Bottom-right split modular badge
            let badgeTop = CGPath(roundedRect: CGRect(x: 9.8, y: 9.8, width: 3.6, height: 2.3), cornerWidth: 0.8, cornerHeight: 0.8, transform: nil)
            let badgeBot = CGPath(roundedRect: CGRect(x: 9.8, y: 12.9, width: 3.6, height: 2.3), cornerWidth: 0.8, cornerHeight: 0.8, transform: nil)
            let badgeRight = CGPath(roundedRect: CGRect(x: 13.9, y: 9.8, width: 2.3, height: 5.4), cornerWidth: 0.8, cornerHeight: 0.8, transform: nil)
            cg.setFillColor(CGColor(gray: 0, alpha: 0.72))
            cg.addPath(badgeTop); cg.fillPath()
            cg.addPath(badgeBot); cg.fillPath()
            cg.setFillColor(CGColor(gray: 0, alpha: 1.0))
            cg.addPath(badgeRight); cg.fillPath()

            return true
        }
        img.isTemplate = true
        return img
    }

    var body: some Scene {
        MenuBarExtra {
            Button("Open Launcher (⌥V / ⌘⇧V)") {
                appDelegate.toggleLauncher()
            }
            .keyboardShortcut("v", modifiers: [.option])

            Divider()

            Button(PermissionManager.shared.isAccessibilityGranted() ? "✓ Accessibility Granted" : "Grant Accessibility Permission...") {
                if !PermissionManager.shared.isAccessibilityGranted() {
                    PermissionManager.shared.requestAccessibilityPermission()
                } else {
                    PermissionManager.shared.openAccessibilitySettings()
                }
            }

            Button(LaunchAtLoginManager.shared.isEnabled ? "✓ Launch on Startup (Auto-start)" : "Launch on Startup (Auto-start)") {
                LaunchAtLoginManager.shared.toggle()
            }

            Button("Clear History") {
                appDelegate.clearHistory()
            }

            Divider()

            Button("About ClipBoard (@zenrakib)...") {
                appDelegate.showAboutPanel()
            }

            Button("Quit ClipBoard") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q", modifiers: [.command])
        } label: {
            Image(nsImage: Self.menuBarIcon)
        }
    }
}
