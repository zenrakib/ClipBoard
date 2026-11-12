// swift-tools-version: 5.9
//
//  Package.swift — ClipBoard for macOS
//  Copyright © 2026 Rakib Hasan (@zenrakib) <zenrakib@gmail.com>. All rights reserved.
//
import PackageDescription

let package = Package(
    name: "ClipBoard",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(name: "ClipBoard", targets: ["ClipBoard"])
    ],
    targets: [
        .executableTarget(
            name: "ClipBoard",
            path: "Sources/ClipBoard"
        )
    ]
)
