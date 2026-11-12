//
//  HotkeyManager.swift
//  ClipBoard for macOS
//
//  Copyright © 2026 Rakib Hasan (@zenrakib) <zenrakib@gmail.com>. All rights reserved.
//  See LICENSE file for details.
//

import Carbon
import AppKit

/// Manages global system-wide hotkeys using the Carbon Event Manager.
///
/// Features:
/// - **Global Interception**: Intercepts hotkeys across any focused application.
/// - **Zero Accessibility Dependency**: Carbon `RegisterEventHotKey` registers globally without requiring Accessibility permissions.
/// - **Clean Event Consumption**: Consumes the event so hotkeys (like `Option + V`) do not emit unwanted text characters into the target editor.
@MainActor
public final class HotkeyManager {

    // MARK: - Properties

    private var hotKeyRefs: [EventHotKeyRef] = []
    private var eventHandler: EventHandlerRef?
    private var onTrigger: (@MainActor () -> Void)?

    // MARK: - Initialization

    public init() {}

    // MARK: - Registration

    /// Registers the default system hotkeys:
    /// 1. `Option + V` (Windows 11 Win+V equivalent)
    /// 2. `Cmd + Shift + V` (Universal macOS paste shortcut)
    ///
    /// - Parameter onTrigger: The callback executed on `@MainActor` when either hotkey is pressed.
    public func registerDefaultHotkeys(onTrigger: @escaping @MainActor () -> Void) {
        self.onTrigger = onTrigger
        installCarbonEventHandler()

        // Hotkey 1: Option + V (keyCode 9, optionKey = 2048)
        registerHotKey(
            keyCode: UInt32(kVK_ANSI_V),
            carbonModifiers: UInt32(optionKey),
            id: 1
        )

        // Hotkey 2: Cmd + Shift + V (keyCode 9, cmdKey = 256, shiftKey = 512)
        registerHotKey(
            keyCode: UInt32(kVK_ANSI_V),
            carbonModifiers: UInt32(cmdKey | shiftKey),
            id: 2
        )
    }

    /// Registers a custom hotkey combination.
    /// - Parameters:
    ///   - keyCode: Carbon virtual key code (e.g. `kVK_ANSI_V`).
    ///   - carbonModifiers: Carbon modifier bitmask (e.g. `optionKey`, `cmdKey | shiftKey`).
    ///   - id: Unique integer identifier for this hotkey.
    public func registerHotKey(keyCode: UInt32, carbonModifiers: UInt32, id: UInt32) {
        var hotKeyRef: EventHotKeyRef?
        let hotKeyID = EventHotKeyID(signature: OSType(0x434C4950), id: id) // "CLIP"

        let status = RegisterEventHotKey(
            keyCode,
            carbonModifiers,
            hotKeyID,
            GetApplicationEventTarget(),
            0,
            &hotKeyRef
        )

        if status == noErr, let ref = hotKeyRef {
            hotKeyRefs.append(ref)
        }
    }

    // MARK: - Event Handling

    private func installCarbonEventHandler() {
        guard eventHandler == nil else { return }

        var eventType = EventTypeSpec(
            eventClass: OSType(kEventClassKeyboard),
            eventKind: OSType(kEventHotKeyPressed)
        )

        let handler: EventHandlerUPP = { (_, _, userData) -> OSStatus in
            guard let userData = userData else { return noErr }
            let manager = Unmanaged<HotkeyManager>.fromOpaque(userData).takeUnretainedValue()
            Task { @MainActor in
                manager.onTrigger?()
            }
            return noErr
        }

        let selfPtr = Unmanaged.passUnretained(self).toOpaque()
        InstallEventHandler(
            GetApplicationEventTarget(),
            handler,
            1,
            &eventType,
            selfPtr,
            &eventHandler
        )
    }

    // MARK: - Unregistration & Cleanup

    /// Unregisters all registered hotkeys and removes the event handler.
    public func unregisterAll() {
        for ref in hotKeyRefs {
            UnregisterEventHotKey(ref)
        }
        hotKeyRefs.removeAll()

        if let handler = eventHandler {
            RemoveEventHandler(handler)
            eventHandler = nil
        }
    }

    #if swift(>=6.0)
    isolated deinit {
        unregisterAll()
    }
    #endif
}

