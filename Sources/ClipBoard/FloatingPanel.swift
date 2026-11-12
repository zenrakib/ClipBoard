//
//  FloatingPanel.swift
//  ClipBoard for macOS
//
//  Copyright © 2026 Rakib Hasan (@zenrakib) <zenrakib@gmail.com>. All rights reserved.
//  See LICENSE file for details.
//

import AppKit
import SwiftUI

/// A specialized borderless, floating `NSPanel` modeled after the Windows 11 (`Win + V`) clipboard popup.
///
/// Features:
/// - **Floating & Non-Activating**: Floats above all windows (`.floating`) and joins all spaces (`.canJoinAllSpaces`, `.fullScreenAuxiliary`).
///   Its `.nonactivatingPanel` mask ensures the underlying target application does not lose focus.
/// - **Cursor-Anchored Positioning**: `showAtCursor()` places the popup adjacent to the cursor while
///   strictly clamping within the current display's `visibleFrame`.
/// - **Auto-Dismiss**: Instantly dismisses on `Escape` keypress, clicking anywhere outside the panel, or window de-focus.
@MainActor
public final class FloatingPanel: NSPanel {

    // MARK: - Event Monitors & Observers

    private var globalMouseMonitor: Any?
    private var localMouseMonitor: Any?
    private var localKeyMonitor: Any?
    private var resignObserver: Any?

    /// Prevents auto-dismissal while the user is actively dragging an item out of the panel.
    public var isDraggingContent: Bool = false

    // MARK: - Initialization

    /// Creates a new `FloatingPanel` with the given content view and dimensions.
    /// - Parameters:
    ///   - contentRect: Initial frame rectangle (defaults to 340x440).
    ///   - rootView: The SwiftUI view hierarchy to host inside the panel.
    public init(
        contentRect: NSRect = NSRect(x: 0, y: 0, width: 340, height: 440),
        rootView: some View
    ) {
        super.init(
            contentRect: contentRect,
            styleMask: [.nonactivatingPanel, .fullSizeContentView, .borderless],
            backing: .buffered,
            defer: false
        )

        // Panel configuration
        self.level = .floating
        self.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        self.isOpaque = false
        self.backgroundColor = .clear
        self.hasShadow = true
        self.isMovable = true
        self.isMovableByWindowBackground = false
        self.hidesOnDeactivate = false

        // Host the SwiftUI content view with rounded corners
        let hostingView = NSHostingView(rootView: AnyView(rootView))
        hostingView.wantsLayer = true
        hostingView.layer?.cornerRadius = 10
        hostingView.layer?.masksToBounds = true
        self.contentView = hostingView
    }

    // MARK: - Window Key Handling

    /// Allows the panel to become key so it can capture arrow key navigation, Enter, and Escape.
    public override var canBecomeKey: Bool {
        return true
    }

    public override var canBecomeMain: Bool {
        return true
    }

    // MARK: - Positioning & Display

    /// Positions and presents the panel immediately adjacent to the cursor location,
    /// clamping within the current display's `visibleFrame` to prevent offscreen overflow.
    public func showAtCursor() {
        let mouseLocation = NSEvent.mouseLocation
        let panelSize = self.frame.size

        // Locate the screen currently containing the mouse cursor
        let screens = NSScreen.screens
        let currentScreen = screens.first(where: { NSMouseInRect(mouseLocation, $0.frame, false) })
            ?? NSScreen.main
            ?? screens.first
        let visibleFrame = currentScreen?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1920, height: 1080)

        // Compute desired origin (right and below cursor)
        let padding: CGFloat = 8
        var originX = mouseLocation.x + padding
        var originY = mouseLocation.y - panelSize.height - padding

        // If overflowing right edge of visible screen, flip to left of cursor
        if originX + panelSize.width > visibleFrame.maxX {
            originX = mouseLocation.x - panelSize.width - padding
        }

        // If overflowing bottom edge of visible screen, flip above cursor
        if originY < visibleFrame.minY {
            originY = mouseLocation.y + padding
        }

        // Strictly clamp within visible screen boundaries
        originX = max(visibleFrame.minX, min(originX, visibleFrame.maxX - panelSize.width))
        originY = max(visibleFrame.minY, min(originY, visibleFrame.maxY - panelSize.height))

        self.setFrameOrigin(NSPoint(x: originX, y: originY))

        // Snappy fade-in presentation
        self.isDraggingContent = false
        self.alphaValue = 0.0
        self.makeKeyAndOrderFront(nil)
        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.10
            self.animator().alphaValue = 1.0
        }

        setupAutoDismiss()
    }

    /// Updates the hosted SwiftUI content view.
    public func setRootView(_ view: some View) {
        let hostingView = NSHostingView(rootView: AnyView(view))
        hostingView.wantsLayer = true
        hostingView.layer?.cornerRadius = 10
        hostingView.layer?.masksToBounds = true
        self.contentView = hostingView
    }

    // MARK: - Auto-Dismissal

    /// Closes the panel with a quick fade-out animation and cleans up event monitors.
    public func dismiss() {
        guard !isDraggingContent else { return }
        cleanupMonitors()
        NSAnimationContext.runAnimationGroup({ context in
            context.duration = 0.10
            self.animator().alphaValue = 0.0
        }, completionHandler: {
            MainActor.assumeIsolated {
                self.orderOut(nil)
                self.alphaValue = 1.0
            }
        })
    }

    /// Configures event monitors and notification observers to automatically dismiss the panel
    /// when the user presses `Escape` or clicks anywhere outside the panel boundaries.
    private func setupAutoDismiss() {
        cleanupMonitors()

        // 1. Global mouse monitor: dismiss on clicks anywhere outside our application windows
        globalMouseMonitor = NSEvent.addGlobalMonitorForEvents(matching: [.leftMouseDown, .rightMouseDown]) { [weak self] _ in
            MainActor.assumeIsolated {
                self?.dismiss()
            }
        }

        // 2. Local mouse monitor: dismiss on clicks outside this panel
        localMouseMonitor = NSEvent.addLocalMonitorForEvents(matching: [.leftMouseDown, .rightMouseDown]) { [weak self] event in
            guard let self = self else { return event }
            if event.window != self {
                self.dismiss()
            }
            return event
        }

        // 3. Local key monitor: dismiss immediately on Escape (keyCode 53)
        localKeyMonitor = NSEvent.addLocalMonitorForEvents(matching: [.keyDown]) { [weak self] event in
            guard let self = self else { return event }
            if event.keyCode == 53 { // ESC
                self.dismiss()
                return nil
            }
            return event
        }

        // 4. Dismiss when panel resigns key window status
        resignObserver = NotificationCenter.default.addObserver(
            forName: NSWindow.didResignKeyNotification,
            object: self,
            queue: .main
        ) { [weak self] _ in
            MainActor.assumeIsolated {
                self?.dismiss()
            }
        }
    }

    /// Removes all active event monitors and notification observers.
    private func cleanupMonitors() {
        if let g = globalMouseMonitor {
            NSEvent.removeMonitor(g)
            globalMouseMonitor = nil
        }
        if let l = localMouseMonitor {
            NSEvent.removeMonitor(l)
            localMouseMonitor = nil
        }
        if let k = localKeyMonitor {
            NSEvent.removeMonitor(k)
            localKeyMonitor = nil
        }
        if let r = resignObserver {
            NotificationCenter.default.removeObserver(r)
            resignObserver = nil
        }
    }

    public override func orderOut(_ sender: Any?) {
        cleanupMonitors()
        super.orderOut(sender)
    }

    public override func close() {
        cleanupMonitors()
        super.close()
    }

    public override func cancelOperation(_ sender: Any?) {
        dismiss()
    }

    // MARK: - Paste Simulation Helper

    /// Utility method to simulate `Cmd + V` keystroke using Quartz Event Services with AppleScript fallback,
    /// pasting the currently active clipboard content into the frontmost application.
    public static func simulatePasteKeystroke() {
        let isTrusted = AXIsProcessTrusted()

        if isTrusted {
            let source = CGEventSource(stateID: .hidSystemState)
            let vKeyCode: CGKeyCode = 9 // Virtual key code for 'V'

            if let keyDown = CGEvent(keyboardEventSource: source, virtualKey: vKeyCode, keyDown: true),
               let keyUp = CGEvent(keyboardEventSource: source, virtualKey: vKeyCode, keyDown: false) {

                keyDown.flags = .maskCommand
                keyUp.flags = .maskCommand

                // 1. Post KeyDown to global HID event tap
                keyDown.post(tap: .cghidEventTap)

                // 2. 25ms hold duration
                usleep(25_000)

                // 3. Post KeyUp to global HID event tap
                keyUp.post(tap: .cghidEventTap)
                return
            }
        }

        // Robust Fallback: AppleScript synthetic keystroke via System Events
        let script = NSAppleScript(source: "tell application \"System Events\" to keystroke \"v\" using command down")
        var error: NSDictionary?
        script?.executeAndReturnError(&error)
    }
}
