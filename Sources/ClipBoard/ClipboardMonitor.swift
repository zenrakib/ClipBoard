//
//  ClipboardMonitor.swift
//  ClipBoard for macOS
//
//  Copyright © 2026 Rakib Hasan (@zenrakib) <zenrakib@gmail.com>. All rights reserved.
//  See LICENSE file for details.
//

import AppKit
import SwiftUI
import Combine
import ImageIO

// MARK: - Clipboard Item Model

/// Represents an immutable entry within the clipboard history stack (Text or Image).
public struct ClipboardItem: Identifiable, Equatable, Hashable, Sendable, Codable {
    /// Unique identifier for each clipboard entry.
    public let id: UUID
    /// The sanitized plain text content or image descriptor.
    public let text: String
    /// The full-resolution image data (PNG format) if this entry is an image.
    public let imageData: Data?
    /// Downscaled, lightweight thumbnail data for optimal UI performance.
    public let thumbnailData: Data?
    /// Native image dimensions in pixels, if applicable.
    public let imageDimensions: CGSize?
    /// The timestamp when the item was copied to the clipboard.
    public let timestamp: Date
    /// Whether this entry is pinned (favorited) and protected from eviction/clearing.
    public var isPinned: Bool

    /// Initializes a text-based clipboard entry.
    public init(
        id: UUID = UUID(),
        text: String,
        timestamp: Date = Date(),
        isPinned: Bool = false
    ) {
        self.id = id
        self.text = text
        self.imageData = nil
        self.thumbnailData = nil
        self.imageDimensions = nil
        self.timestamp = timestamp
        self.isPinned = isPinned
    }

    /// Initializes an image-based clipboard entry.
    public init(
        id: UUID = UUID(),
        imageData: Data,
        thumbnailData: Data,
        dimensions: CGSize,
        timestamp: Date = Date(),
        isPinned: Bool = false
    ) {
        self.id = id
        let w = Int(dimensions.width)
        let h = Int(dimensions.height)
        self.text = "Image (\(w) × \(h))"
        self.imageData = imageData
        self.thumbnailData = thumbnailData
        self.imageDimensions = dimensions
        self.timestamp = timestamp
        self.isPinned = isPinned
    }

    /// Whether this entry contains an image payload.
    public var isImage: Bool {
        imageData != nil
    }

    /// Returns an NSImage constructed from the downscaled thumbnail data or original image data.
    public var thumbnailImage: NSImage? {
        if let thumbData = thumbnailData {
            return NSImage(data: thumbData)
        }
        if let data = imageData {
            return NSImage(data: data)
        }
        return nil
    }
}

// MARK: - Clipboard Monitor

/// High-performance, zero-CPU-overhead clipboard monitor for macOS using `NSPasteboard`.
///
/// Key design characteristics:
/// - **Zero CPU Overhead**: Employs integer-based `changeCount` polling with timer coalescing tolerance,
///   exiting in nanoseconds whenever no pasteboard change has occurred.
/// - **Strict Credential Suppression**: Filters out copies tagged with `org.nspasteboard.ConcealedType`,
///   `com.agilebits.onepassword`, transient types, and custom credential signatures from password managers.
/// - **Multimodal Support**: Automatically detects and extracts both text and screenshots / images (PNG/TIFF).
/// - **Thumbnailing & Memory Safety**: Downscales large images to lightweight thumbnails via ImageIO.
/// - **Sanitization & Deduplication**: Deduplicates existing entries by bumping them to the top of the stack,
///   and caps in-memory storage to the last 50 items.
/// - **SwiftUI Reactivity & Thread Safety**: Bound to `@MainActor` with `@Published` properties, ensuring
///   safe, seamless main-thread updates to SwiftUI views without race conditions.
@MainActor
public final class ClipboardMonitor: ObservableObject {

    // MARK: - Published Properties

    /// In-memory stack containing the latest clipboard items (most recent at index 0).
    @Published public private(set) var items: [ClipboardItem] = []

    /// Current monitoring state.
    @Published public private(set) var isMonitoring: Bool = false

    // MARK: - Configuration

    /// Maximum capacity of the in-memory clipboard history stack (default: 50).
    public let maxCapacity: Int

    /// Polling interval for checking pasteboard change counts (default: 0.25s).
    public let pollInterval: TimeInterval

    /// Most recently copied item, if any.
    public var latestItem: ClipboardItem? {
        items.first
    }

    // MARK: - Password Manager & Concealed Types

    /// Standard UTI signatures used by password managers and system utilities to mark concealed or transient data.
    public static let suppressedPasteboardTypes: Set<NSPasteboard.PasteboardType> = [
        // Universal standard for concealed / confidential data (1Password, Bitwarden, KeePassXC, etc.)
        NSPasteboard.PasteboardType("org.nspasteboard.ConcealedType"),
        // 1Password specific UTI identifiers
        NSPasteboard.PasteboardType("com.agilebits.onepassword"),
        NSPasteboard.PasteboardType("com.agilebits.onepassword4"),
        // Password generators and system autogenerated content
        NSPasteboard.PasteboardType("org.nspasteboard.AutoGeneratedType"),
        // Universal transient pasteboard type (indicates clipboard history should not record this)
        NSPasteboard.PasteboardType("org.nspasteboard.TransientType"),
        // Legacy TextExpander & Butler transient type
        NSPasteboard.PasteboardType("de.petermaurer.TransientPasteboardType"),
        // TypeIt4Me transient marker
        NSPasteboard.PasteboardType("com.typeit4me.clipping"),
        // macOS text generator type
        NSPasteboard.PasteboardType("Pasteboard generator type")
    ]

    // MARK: - Private State

    private let pasteboard: NSPasteboard
    private var lastChangeCount: Int
    private var timer: Timer?
    private let persistenceURL: URL?
    private let isPersistenceEnabled: Bool

    // MARK: - Persistence Path & Storage

    /// Resolves the filesystem URL for persistent pinned items JSON.
    /// Default: `~/Library/Application Support/ClipBoard/pinned.json`
    public var resolvedPersistenceURL: URL {
        if let custom = persistenceURL {
            return custom
        }
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        let dir = appSupport.appendingPathComponent("ClipBoard", isDirectory: true)
        return dir.appendingPathComponent("pinned.json")
    }

    /// Saves all currently pinned items to local disk storage in JSON format.
    public func savePinnedItems() {
        guard isPersistenceEnabled else { return }
        let pinned = items.filter { $0.isPinned }
        let targetURL = resolvedPersistenceURL
        let parentDir = targetURL.deletingLastPathComponent()

        do {
            try FileManager.default.createDirectory(at: parentDir, withIntermediateDirectories: true)
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            encoder.outputFormatting = .prettyPrinted
            let data = try encoder.encode(pinned)
            try data.write(to: targetURL, options: .atomic)
        } catch {
            print("Failed to persist pinned items to \(targetURL.path): \(error)")
        }
    }

    /// Loads persisted pinned items from disk storage.
    public func loadPinnedItems() -> [ClipboardItem] {
        guard isPersistenceEnabled else { return [] }
        let targetURL = resolvedPersistenceURL
        guard FileManager.default.fileExists(atPath: targetURL.path) else { return [] }

        do {
            let data = try Data(contentsOf: targetURL)
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode([ClipboardItem].self, from: data)
        } catch {
            print("Failed to decode pinned items from \(targetURL.path): \(error)")
            return []
        }
    }

    // MARK: - Initialization

    /// Initializes a new `ClipboardMonitor`.
    /// - Parameters:
    ///   - pasteboard: The pasteboard to monitor (defaults to `NSPasteboard.general`).
    ///   - pollInterval: Polling cadence in seconds (defaults to `0.25`).
    ///   - maxCapacity: Maximum items retained in the stack (defaults to `50`).
    ///   - autoStart: Whether to start monitoring immediately upon initialization (defaults to `true`).
    ///   - captureCurrentOnStart: If true, checks and records the current clipboard item on startup.
    ///   - enablePersistence: Enables JSON storage for pinned items (defaults to true for .general or custom persistenceURL).
    ///   - persistenceURL: Optional custom storage URL (defaults to `~/Library/Application Support/ClipBoard/pinned.json`).
    public init(
        pasteboard: NSPasteboard = .general,
        pollInterval: TimeInterval = 0.25,
        maxCapacity: Int = 50,
        autoStart: Bool = true,
        captureCurrentOnStart: Bool = true,
        enablePersistence: Bool? = nil,
        persistenceURL: URL? = nil
    ) {
        self.pasteboard = pasteboard
        self.pollInterval = pollInterval
        self.maxCapacity = maxCapacity
        self.persistenceURL = persistenceURL
        self.isPersistenceEnabled = enablePersistence ?? (pasteboard == .general || persistenceURL != nil)
        self.lastChangeCount = captureCurrentOnStart ? -1 : pasteboard.changeCount

        // 1. Populate stack with persisted pinned items
        if self.isPersistenceEnabled {
            self.items = loadPinnedItems()
        }

        // 2. Start monitoring and capture current pasteboard if requested
        if autoStart {
            startMonitoring()
            if captureCurrentOnStart {
                checkPasteboard()
            }
        }
    }

    #if swift(>=6.0)
    isolated deinit {
        timer?.invalidate()
    }
    #else
    deinit {
        timer?.invalidate()
    }
    #endif

    // MARK: - Monitoring Lifecycle

    /// Begins polling the pasteboard for changes.
    public func startMonitoring() {
        guard !isMonitoring else { return }
        isMonitoring = true
        lastChangeCount = pasteboard.changeCount

        let timer = Timer(timeInterval: pollInterval, repeats: true) { [weak self] _ in
            MainActor.assumeIsolated {
                self?.checkPasteboard()
            }
        }

        timer.tolerance = min(0.05, pollInterval * 0.2)
        RunLoop.main.add(timer, forMode: .common)
        self.timer = timer
    }

    /// Stops monitoring the pasteboard and releases the timer.
    public func stopMonitoring() {
        guard isMonitoring else { return }
        isMonitoring = false
        timer?.invalidate()
        timer = nil
    }

    // MARK: - Core Pasteboard Processing

    /// Inspects the pasteboard and records plain text or image content if changed and not suppressed.
    ///
    /// Exits in nanoseconds when `pasteboard.changeCount == lastChangeCount` (Zero CPU Overhead).
    public func checkPasteboard() {
        let currentChangeCount = pasteboard.changeCount

        // 1. Zero CPU Overhead Fast-Path: single integer comparison guard
        guard currentChangeCount != lastChangeCount else {
            return
        }
        lastChangeCount = currentChangeCount

        // 2. Strict Password Manager Suppression
        guard !isSuppressedByPasswordManager() else {
            return
        }

        // 3. Inspect Image Data (Screenshots & Copied Images)
        if let imagePayload = extractImage() {
            recordImageItem(
                data: imagePayload.data,
                thumbnailData: imagePayload.thumbnailData,
                dimensions: imagePayload.dimensions
            )
            return
        }

        // 4. Extract Plain Text
        guard let rawText = extractPlainText() else {
            return
        }

        // 5. Trim Whitespace & Reject Empty Strings
        let trimmedText = rawText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedText.isEmpty else {
            return
        }

        // 6. Record into stack
        recordTextItem(trimmedText)
    }

    // MARK: - Suppression Logic

    /// Evaluates if the current pasteboard contents originate from a password manager or are marked concealed.
    private func isSuppressedByPasswordManager() -> Bool {
        if let types = pasteboard.types, types.contains(where: Self.isSuppressedType) {
            return true
        }

        if let pbItems = pasteboard.pasteboardItems {
            for item in pbItems {
                if item.types.contains(where: Self.isSuppressedType) {
                    return true
                }
            }
        }

        return false
    }

    /// Determines if a specific `NSPasteboard.PasteboardType` indicates concealed or sensitive data.
    public static func isSuppressedType(_ type: NSPasteboard.PasteboardType) -> Bool {
        if suppressedPasteboardTypes.contains(type) {
            return true
        }

        let raw = type.rawValue.lowercased()
        return raw.contains("concealed") ||
               raw.contains("onepassword") ||
               raw.contains("transient") ||
               raw.contains("autogenerated") ||
               raw.contains("credential") ||
               raw.contains("password")
    }

    // MARK: - Plain Text Extraction

    /// Safely extracts plain text representation from the pasteboard.
    private func extractPlainText() -> String? {
        if let string = pasteboard.string(forType: .string) {
            return string
        }

        if let item = pasteboard.pasteboardItems?.first {
            if let string = item.string(forType: .string) {
                return string
            }
            if let string = item.string(forType: NSPasteboard.PasteboardType("public.utf8-plain-text")) {
                return string
            }
        }

        return nil
    }

    // MARK: - Image Extraction & Thumbnailing

    /// Inspects the pasteboard for image/screenshot data and extracts PNG bytes,
    /// dimensions, and a downscaled thumbnail across all macOS image sources
    /// (Direct PNG, TIFF screenshots, JPEG, WebP, Cocoa NSImage, and Finder file copies).
    ///
    /// Preserves exact original PNG bytes and applies strict sRGB color calibration to screenshots
    /// and uncalibrated formats to prevent color distortion or washing out on custom/Display P3 monitors.
    private func extractImage() -> (data: Data, thumbnailData: Data, dimensions: CGSize)? {
        // Strategy 1: Direct PNG data (Chromium/Brave, Safari, Figma, etc.)
        // Preserves 100% untouched original byte stream with embedded ICC/gamma chunks
        if let pngData = pasteboard.data(forType: .png) {
            if let source = CGImageSourceCreateWithData(pngData as CFData, nil),
               let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
               let width = properties[kCGImagePropertyPixelWidth] as? CGFloat,
               let height = properties[kCGImagePropertyPixelHeight] as? CGFloat {
                let dims = CGSize(width: width, height: height)
                let thumb = generateThumbnailData(from: pngData, maxDimension: 320) ?? pngData
                return (data: pngData, thumbnailData: thumb, dimensions: dims)
            }
        }

        // Strategy 2: Direct TIFF data (macOS default screenshot Cmd+Shift+Control+4)
        // Strictly calibrated to universal standard sRGB from the monitor's native color space
        if let tiffData = pasteboard.data(forType: .tiff),
           let rep = NSBitmapImageRep(data: tiffData) {
            let dims = CGSize(width: rep.pixelsWide, height: rep.pixelsHigh)
            let srgbRep = rep.converting(to: .sRGB, renderingIntent: .default) ?? rep
            var props: [NSBitmapImageRep.PropertyKey: Any] = [:]
            if let icc = NSColorSpace.sRGB.iccProfileData {
                props[.colorSyncProfileData] = icc
            }
            if let pngBytes = srgbRep.representation(using: .png, properties: props) {
                let thumb = generateThumbnailData(from: pngBytes, maxDimension: 320) ?? pngBytes
                return (data: pngBytes, thumbnailData: thumb, dimensions: dims)
            }
        }

        // Strategy 3: Direct JPEG data
        let jpegType = NSPasteboard.PasteboardType("public.jpeg")
        if let jpegData = pasteboard.data(forType: jpegType),
           let rep = NSBitmapImageRep(data: jpegData) {
            let dims = CGSize(width: rep.pixelsWide, height: rep.pixelsHigh)
            let srgbRep = rep.converting(to: .sRGB, renderingIntent: .default) ?? rep
            var props: [NSBitmapImageRep.PropertyKey: Any] = [:]
            if let icc = NSColorSpace.sRGB.iccProfileData {
                props[.colorSyncProfileData] = icc
            }
            if let pngBytes = srgbRep.representation(using: .png, properties: props) {
                let thumb = generateThumbnailData(from: pngBytes, maxDimension: 320) ?? pngBytes
                return (data: pngBytes, thumbnailData: thumb, dimensions: dims)
            }
        }

        // Strategy 4: Universal Cocoa NSImage(pasteboard:)
        if NSImage.canInit(with: pasteboard),
           let pbImage = NSImage(pasteboard: pasteboard),
           let tiffData = pbImage.tiffRepresentation,
           let rep = NSBitmapImageRep(data: tiffData) {
            let dims = CGSize(width: rep.pixelsWide, height: rep.pixelsHigh)
            let srgbRep = rep.converting(to: .sRGB, renderingIntent: .default) ?? rep
            var props: [NSBitmapImageRep.PropertyKey: Any] = [:]
            if let icc = NSColorSpace.sRGB.iccProfileData {
                props[.colorSyncProfileData] = icc
            }
            if let pngBytes = srgbRep.representation(using: .png, properties: props) {
                let thumb = generateThumbnailData(from: pngBytes, maxDimension: 320) ?? pngBytes
                return (data: pngBytes, thumbnailData: thumb, dimensions: dims)
            }
        }

        // Strategy 5: File URLs on pasteboard (e.g. user selected and copied an image file in Finder/Desktop)
        if let fileUrls = pasteboard.readObjects(forClasses: [NSURL.self], options: nil) as? [URL] {
            let supportedExtensions = Set(["png", "jpg", "jpeg", "gif", "webp", "heic", "tiff", "bmp"])
            for url in fileUrls {
                if supportedExtensions.contains(url.pathExtension.lowercased()) {
                    if url.pathExtension.lowercased() == "png", let fileData = try? Data(contentsOf: url) {
                        if let source = CGImageSourceCreateWithData(fileData as CFData, nil),
                           let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
                           let width = properties[kCGImagePropertyPixelWidth] as? CGFloat,
                           let height = properties[kCGImagePropertyPixelHeight] as? CGFloat {
                            let dims = CGSize(width: width, height: height)
                            let thumb = generateThumbnailData(from: fileData, maxDimension: 320) ?? fileData
                            return (data: fileData, thumbnailData: thumb, dimensions: dims)
                        }
                    } else if let img = NSImage(contentsOf: url),
                              let tiffData = img.tiffRepresentation,
                              let rep = NSBitmapImageRep(data: tiffData) {
                        let dims = CGSize(width: rep.pixelsWide, height: rep.pixelsHigh)
                        let srgbRep = rep.converting(to: .sRGB, renderingIntent: .default) ?? rep
                        var props: [NSBitmapImageRep.PropertyKey: Any] = [:]
                        if let icc = NSColorSpace.sRGB.iccProfileData {
                            props[.colorSyncProfileData] = icc
                        }
                        if let pngBytes = srgbRep.representation(using: .png, properties: props) {
                            let thumb = generateThumbnailData(from: pngBytes, maxDimension: 320) ?? pngBytes
                            return (data: pngBytes, thumbnailData: thumb, dimensions: dims)
                        }
                    }
                }
            }
        }

        return nil
    }

    /// Downscales image data to a maximum dimension using ImageIO to minimize RAM footprint.
    private func generateThumbnailData(from originalData: Data, maxDimension: CGFloat = 320) -> Data? {
        guard let source = CGImageSourceCreateWithData(originalData as CFData, nil) else {
            return nil
        }
        let options: [CFString: Any] = [
            kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceShouldCacheImmediately: true,
            kCGImageSourceCreateThumbnailWithTransform: true,
            kCGImageSourceThumbnailMaxPixelSize: maxDimension
        ]
        guard let cgThumb = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary) else {
            return nil
        }
        let rep = NSBitmapImageRep(cgImage: cgThumb)
        return rep.representation(using: .jpeg, properties: [.compressionFactor: 0.8]) ??
               rep.representation(using: .png, properties: [:])
    }

    // MARK: - Stack Management, Capacity & Deduplication

    /// Deduplicates text entries and inserts the new item at index 0.
    /// Preserves existing `isPinned` status if the item was already pinned.
    private func recordTextItem(_ text: String) {
        let existingIndex = items.firstIndex(where: { !$0.isImage && $0.text == text })
        let wasPinned = existingIndex.map { items[$0].isPinned } ?? false
        if let existingIndex = existingIndex {
            items.remove(at: existingIndex)
        }
        let newItem = ClipboardItem(text: text, isPinned: wasPinned)
        items.insert(newItem, at: 0)
        trimToCapacity()
    }

    /// Deduplicates image entries based on data content and inserts at index 0.
    /// Preserves existing `isPinned` status if the image was already pinned.
    private func recordImageItem(data: Data, thumbnailData: Data, dimensions: CGSize) {
        let existingIndex = items.firstIndex(where: { $0.isImage && $0.imageData == data })
        let wasPinned = existingIndex.map { items[$0].isPinned } ?? false
        if let existingIndex = existingIndex {
            items.remove(at: existingIndex)
        }
        let newItem = ClipboardItem(
            imageData: data,
            thumbnailData: thumbnailData,
            dimensions: dimensions,
            isPinned: wasPinned
        )
        items.insert(newItem, at: 0)
        trimToCapacity()
    }

    /// Promotes an existing item or inserts an item at the top of the stack.
    /// Preserves existing `isPinned` status.
    private func recordItem(_ item: ClipboardItem) {
        let existingIndex: Int?
        if item.isImage, let data = item.imageData {
            existingIndex = items.firstIndex(where: { $0.isImage && $0.imageData == data })
        } else {
            existingIndex = items.firstIndex(where: { !$0.isImage && $0.text == item.text })
        }
        let wasPinned = existingIndex.map { items[$0].isPinned } ?? item.isPinned
        if let existingIndex = existingIndex {
            items.remove(at: existingIndex)
        }
        var updated = item
        updated.isPinned = wasPinned
        items.insert(updated, at: 0)
        trimToCapacity()
    }

    /// Trims the history stack down to `maxCapacity`.
    /// Pinned items are strictly protected and NEVER evicted.
    private func trimToCapacity() {
        while items.count > maxCapacity {
            // Find the oldest unpinned item to evict
            if let lastUnpinnedIndex = items.lastIndex(where: { !$0.isPinned }) {
                items.remove(at: lastUnpinnedIndex)
            } else {
                // All items currently in the stack are pinned favorites; preserve them all
                break
            }
        }
    }

    // MARK: - Pinning & Favorites

    /// Toggles the pinned status of a clipboard item and saves changes to persistent storage.
    public func togglePin(item: ClipboardItem) {
        togglePin(id: item.id)
    }

    /// Toggles the pinned status of a clipboard item by its UUID and saves changes.
    public func togglePin(id: UUID) {
        guard let index = items.firstIndex(where: { $0.id == id }) else { return }
        items[index].isPinned.toggle()
        savePinnedItems()
    }

    /// Explicitly pins an item by UUID and saves changes.
    public func pin(id: UUID) {
        guard let index = items.firstIndex(where: { $0.id == id }) else { return }
        if !items[index].isPinned {
            items[index].isPinned = true
            savePinnedItems()
        }
    }

    /// Explicitly unpins an item by UUID and saves changes.
    public func unpin(id: UUID) {
        guard let index = items.firstIndex(where: { $0.id == id }) else { return }
        if items[index].isPinned {
            items[index].isPinned = false
            savePinnedItems()
        }
    }

    // MARK: - Convenience Helpers

    /// Clears unpinned history items from memory.
    /// Pinned favorites are NEVER removed.
    public func clear() {
        items.removeAll(where: { !$0.isPinned })
    }

    /// Removes a specific clipboard item by its identifier. If pinned, updates persistent storage.
    public func remove(item: ClipboardItem) {
        let wasPinned = item.isPinned
        items.removeAll(where: { $0.id == item.id })
        if wasPinned {
            savePinnedItems()
        }
    }

    /// Removes the clipboard item at the specified index. If pinned, updates persistent storage.
    public func remove(at index: Int) {
        guard items.indices.contains(index) else { return }
        let item = items.remove(at: index)
        if item.isPinned {
            savePinnedItems()
        }
    }

    /// Copies a history item back to the system clipboard, bumping it to the top
    /// of the stack while preventing redundant duplicate processing.
    public func copyToPasteboard(_ item: ClipboardItem) {
        pasteboard.clearContents()
        if item.isImage, let data = item.imageData {
            pasteboard.setData(data, forType: .png)
            if let rep = NSBitmapImageRep(data: data)?.converting(to: .sRGB, renderingIntent: .default),
               let tiff = rep.representation(using: .tiff, properties: [:]) {
                pasteboard.setData(tiff, forType: .tiff)
            }
        } else {
            pasteboard.setString(item.text, forType: .string)
        }

        // Synchronize changeCount so our own write is not re-processed
        lastChangeCount = pasteboard.changeCount

        // Promote the item to the top of the stack
        recordItem(item)
    }
}

// MARK: - Drag & Drop Asset Export & Pasteboard Writer

/// Manages persistent PNG export for dragged image items so external NLEs
/// (Premiere Pro, After Effects, DaVinci Resolve, Finder) never encounter "Media Offline".
@MainActor
public enum ClipboardDragHelper {

    /// Directory where dragged image files are persisted (`~/Library/Application Support/ClipBoard/Assets`).
    public static func defaultAssetsDirectory() -> URL {
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        return appSupport
            .appendingPathComponent("ClipBoard", isDirectory: true)
            .appendingPathComponent("Assets", isDirectory: true)
    }

    /// Exports an image `ClipboardItem` as a `.png` file on disk (or reuses an existing export)
    /// and returns its file `URL`. Returns `nil` for non-image items.
    public static func exportImageFile(
        for item: ClipboardItem,
        directory: URL? = nil
    ) -> URL? {
        guard item.isImage, let pngData = item.imageData else { return nil }
        let targetDir = directory ?? defaultAssetsDirectory()

        do {
            try FileManager.default.createDirectory(at: targetDir, withIntermediateDirectories: true)
            let shortId = String(item.id.uuidString.prefix(8))
            let fileURL = targetDir.appendingPathComponent("ClipBoard_\(shortId).png")

            // Reuse existing file if same size already exported
            if let existingAttrs = try? FileManager.default.attributesOfItem(atPath: fileURL.path),
               let existingSize = existingAttrs[.size] as? Int,
               existingSize == pngData.count {
                return fileURL
            }

            try pngData.write(to: fileURL, options: .atomic)
            return fileURL
        } catch {
            print("Failed to export dragged image asset: \(error)")
            return nil
        }
    }

    /// Builds a synchronous `NSPasteboardWriting` payload compatible with Finder, Premiere Pro,
    /// After Effects, DaVinci Resolve, Photoshop, Figma, browsers, and text editors.
    public static func makePasteboardWriter(
        for item: ClipboardItem,
        assetsDirectory: URL? = nil
    ) -> NSPasteboardWriting {
        if item.isImage,
           let pngData = item.imageData,
           let fileURL = exportImageFile(for: item, directory: assetsDirectory) {
            return DraggableClipboardWriter(fileURL: fileURL, pngData: pngData, text: item.text)
        }
        return item.text as NSString
    }
}

/// Custom `NSPasteboardWriting` providing BOTH `NSURL` file flavors (`public.file-url`,
/// `NSFilenamesPboardType`, `'furl'`) for video/image editors & Finder AND raw `.png` data for browsers/design tools.
public final class DraggableClipboardWriter: NSObject, NSPasteboardWriting {
    public let fileURL: URL
    public let pngData: Data
    public let text: String

    public init(fileURL: URL, pngData: Data, text: String) {
        self.fileURL = fileURL
        self.pngData = pngData
        self.text = text
    }

    public func writableTypes(for pasteboard: NSPasteboard) -> [NSPasteboard.PasteboardType] {
        var types = (fileURL as NSURL).writableTypes(for: pasteboard)
        if !types.contains(.png) {
            types.append(.png)
        }
        return types
    }

    public func pasteboardPropertyList(forType type: NSPasteboard.PasteboardType) -> Any? {
        if type == .png {
            return pngData
        }
        return (fileURL as NSURL).pasteboardPropertyList(forType: type)
    }
}
