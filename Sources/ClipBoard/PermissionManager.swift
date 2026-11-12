//
//  PermissionManager.swift
//  ClipBoard for macOS
//
//  Copyright © 2026 Rakib Hasan (@zenrakib) <zenrakib@gmail.com>. All rights reserved.
//  See LICENSE file for details.
//

import ApplicationServices
import AppKit

/// Manages macOS Accessibility permissions required for synthetic keystroke injection (auto-paste).
@MainActor
public final class PermissionManager {

    // MARK: - Shared Instance

    public static let shared = PermissionManager()

    private init() {}

    // MARK: - Permission Queries

    /// Checks whether the application currently holds macOS Accessibility permissions.
    ///
    /// This query does not trigger any system dialogues.
    public func isAccessibilityGranted() -> Bool {
        return AXIsProcessTrusted()
    }

    /// Checks whether Accessibility permissions are granted.
    /// If not, it requests macOS to prompt the user once with a system dialog directing them
    /// to System Settings > Privacy & Security > Accessibility.
    /// - Returns: `true` if permission is already granted, `false` otherwise.
    @discardableResult
    public func requestAccessibilityPermission() -> Bool {
        let promptKey = "AXTrustedCheckOptionPrompt" as CFString
        let options = [promptKey: true] as CFDictionary
        return AXIsProcessTrustedWithOptions(options)
    }

    /// Directly opens the macOS System Settings page for Accessibility permissions.
    public func openAccessibilitySettings() {
        let urlString = "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
        if let url = URL(string: urlString) {
            NSWorkspace.shared.open(url)
        }
    }
}

