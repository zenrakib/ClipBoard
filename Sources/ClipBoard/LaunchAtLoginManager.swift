//
//  LaunchAtLoginManager.swift
//  ClipBoard for macOS
//
//  Copyright © 2026 Rakib Hasan (@zenrakib) <zenrakib@gmail.com>. All rights reserved.
//  See LICENSE file for details.
//

import Foundation
import ServiceManagement
import AppKit

/// Manages automatic application startup on macOS login / boot.
@MainActor
public final class LaunchAtLoginManager: ObservableObject {

    public static let shared = LaunchAtLoginManager()

    @Published public private(set) var isEnabled: Bool = false

    private let launchAgentURL: URL = {
        let home = FileManager.default.homeDirectoryForCurrentUser
        return home.appendingPathComponent("Library/LaunchAgents/com.zenrakib.clipboard.plist")
    }()

    private init() {
        self.isEnabled = checkIsEnabled()
    }

    /// Evaluates if autostart on login is currently enabled.
    public func checkIsEnabled() -> Bool {
        if #available(macOS 13.0, *) {
            if SMAppService.mainApp.status == .enabled {
                return true
            }
        }
        return FileManager.default.fileExists(atPath: launchAgentURL.path)
    }

    /// Toggles the launch at login state.
    public func toggle() {
        setEnabled(!isEnabled)
    }

    /// Enables or disables automatic startup at login.
    public func setEnabled(_ enable: Bool) {
        if enable {
            enableLaunchAtLogin()
        } else {
            disableLaunchAtLogin()
        }
        self.isEnabled = checkIsEnabled()
    }

    /// Enables launch at login via SMAppService and User LaunchAgent.
    public func enableLaunchAtLogin() {
        // Method 1: Modern macOS 13+ ServiceManagement API
        if #available(macOS 13.0, *) {
            do {
                if SMAppService.mainApp.status != .enabled {
                    try SMAppService.mainApp.register()
                }
            } catch {
                print("⚠️ [LaunchAtLoginManager] SMAppService register note: \(error)")
            }
        }

        // Method 2: Resilient User LaunchAgent
        createLaunchAgentPlist()
        self.isEnabled = true
    }

    /// Disables launch at login.
    public func disableLaunchAtLogin() {
        if #available(macOS 13.0, *) {
            do {
                try SMAppService.mainApp.unregister()
            } catch {
                print("⚠️ [LaunchAtLoginManager] SMAppService unregister note: \(error)")
            }
        }

        try? FileManager.default.removeItem(at: launchAgentURL)
        self.isEnabled = false
    }

    private func createLaunchAgentPlist() {
        let launchAgentsDir = launchAgentURL.deletingLastPathComponent()
        try? FileManager.default.createDirectory(at: launchAgentsDir, withIntermediateDirectories: true)

        let executablePath = Bundle.main.executablePath ?? "/Applications/ClipBoard.app/Contents/MacOS/ClipBoard"
        let plistContent = """
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.zenrakib.clipboard</string>
            <key>ProgramArguments</key>
            <array>
                <string>\(executablePath)</string>
            </array>
            <key>RunAtLoad</key>
            <true/>
            <key>ProcessType</key>
            <string>Interactive</string>
        </dict>
        </plist>
        """

        if let data = plistContent.data(using: .utf8) {
            try? data.write(to: launchAgentURL, options: .atomic)
        }
    }
}

