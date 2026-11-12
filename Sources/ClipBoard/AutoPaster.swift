//
//  AutoPaster.swift
//  ClipBoard for macOS
//
//  Copyright © 2026 Rakib Hasan (@zenrakib) <zenrakib@gmail.com>. All rights reserved.
//  See LICENSE file for details.
//

import AppKit
import Foundation
import ApplicationServices

/// Orchestrates target application tracking, clipboard synchronization, and synthetic keystroke paste injection.
@MainActor
public final class AutoPaster {

    // MARK: - Properties

    private weak var monitor: ClipboardMonitor?
    private weak var panel: FloatingPanel?

    /// The frontmost application captured immediately prior to presenting the clipboard launcher.
    public private(set) var targetApplication: NSRunningApplication?

    /// Continuously tracks the most recent non-ClipBoard active application.
    public private(set) var lastActiveApplication: NSRunningApplication?

    private var workspaceObserver: Any?

    // MARK: - Initialization

    /// Initializes a new `AutoPaster`.
    /// - Parameters:
    ///   - monitor: The `ClipboardMonitor` responsible for clipboard synchronization.
    ///   - panel: The `FloatingPanel` presenting the UI.
    public init(monitor: ClipboardMonitor, panel: FloatingPanel) {
        self.monitor = monitor
        self.panel = panel
        self.lastActiveApplication = NSWorkspace.shared.frontmostApplication

        // Continuously track active applications so we always know where to paste
        self.workspaceObserver = NSWorkspace.shared.notificationCenter.addObserver(
            forName: NSWorkspace.didActivateApplicationNotification,
            object: nil,
            queue: .main
        ) { [weak self] notification in
            if let app = notification.userInfo?[NSWorkspace.applicationUserInfoKey] as? NSRunningApplication,
               app.bundleIdentifier != Bundle.main.bundleIdentifier {
                MainActor.assumeIsolated {
                    self?.lastActiveApplication = app
                }
            }
        }
    }

    #if swift(>=6.0)
    isolated deinit {
        if let observer = workspaceObserver {
            NotificationCenter.default.removeObserver(observer)
        }
    }
    #else
    deinit {
        if let observer = workspaceObserver {
            NotificationCenter.default.removeObserver(observer)
        }
    }
    #endif

    // MARK: - Launcher Trigger & Focus Tracking

    /// Records the currently focused application and presents the floating panel adjacent to the cursor.
    public func triggerLauncher() {
        // Record frontmost application before showing the panel
        recordTargetApplication()

        // Display panel at cursor
        panel?.showAtCursor()
    }

    /// Records the frontmost application, filtering out this process.
    public func recordTargetApplication() {
        if let frontmost = NSWorkspace.shared.frontmostApplication,
           frontmost.bundleIdentifier != Bundle.main.bundleIdentifier {
            self.targetApplication = frontmost
        } else if let last = lastActiveApplication, !last.isTerminated {
            self.targetApplication = last
        }
    }

    // MARK: - Auto-Paste Orchestration

    /// Executes the complete Windows 11 style paste injection workflow:
    /// 1. Immediately hides and dismisses the floating panel: calls `panel.orderOut(nil)` to yield system key focus.
    /// 2. Synchronizes the chosen item (text or image) to `NSPasteboard.general` (writing both .png and .tiff for images).
    /// 3. Deactivates our agent process and re-activates the target application.
    /// 4. Waits ~200ms for browser / application DOM focus stabilization, then injects `Cmd + V`.
    ///
    /// - Parameter item: The selected `ClipboardItem` to paste.
    public func pasteItem(_ item: ClipboardItem) {
        // Step 1: Strictly hide and dismiss the panel immediately to yield system key focus
        panel?.orderOut(nil)
        panel?.alphaValue = 1.0

        // Step 2: Write item to NSPasteboard.general first (guaranteeing clipboard sync)
        if let monitor = monitor {
            monitor.copyToPasteboard(item)
        } else {
            writeItemToPasteboard(item)
        }

        // Step 3: Resolve destination target application
        let targetApp = resolveTargetApp()

        // Yield OS focus: deactivate our agent app and activate the destination target
        NSApp.deactivate()
        if let target = targetApp, !target.isTerminated {
            if #available(macOS 14.0, *) {
                target.activate()
            } else {
                target.activate(options: [.activateIgnoringOtherApps])
            }
        }

        // Step 4: Wait a reliable 200ms for focus stabilization before injecting keystroke
        Task { @MainActor in
            try? await Task.sleep(nanoseconds: 200_000_000) // 200 milliseconds (optimal for browser renderers)
            FloatingPanel.simulatePasteKeystroke()
        }
    }

    private func resolveTargetApp() -> NSRunningApplication? {
        if let target = targetApplication, !target.isTerminated {
            return target
        }
        if let last = lastActiveApplication, !last.isTerminated {
            return last
        }
        return NSWorkspace.shared.runningApplications.first {
            $0.isActive && $0.bundleIdentifier != Bundle.main.bundleIdentifier
        }
    }

    private func writeItemToPasteboard(_ item: ClipboardItem) {
        let pb = NSPasteboard.general
        pb.clearContents()
        if item.isImage, let data = item.imageData {
            pb.setData(data, forType: .png)
            if let rep = NSBitmapImageRep(data: data)?.converting(to: .sRGB, renderingIntent: .default),
               let tiff = rep.representation(using: .tiff, properties: [:]) {
                pb.setData(tiff, forType: .tiff)
            }
        } else {
            pb.setString(item.text, forType: .string)
        }
    }
}
