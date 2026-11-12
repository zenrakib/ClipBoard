//
//  ClipboardView.swift
//  ClipBoard for macOS
//
//  Copyright © 2026 Rakib Hasan (@zenrakib) <zenrakib@gmail.com>. All rights reserved.
//  See LICENSE file for details.
//

import AppKit
import SwiftUI
import Combine

// MARK: - Frosted Glass Visual Effect View

/// NSViewRepresentable wrapping `NSVisualEffectView` to render Windows 11-style frosted glass with dark acrylic material.
public struct FrostedGlassView: NSViewRepresentable {
    public let material: NSVisualEffectView.Material
    public let blendingMode: NSVisualEffectView.BlendingMode

    public init(
        material: NSVisualEffectView.Material = .popover,
        blendingMode: NSVisualEffectView.BlendingMode = .behindWindow
    ) {
        self.material = material
        self.blendingMode = blendingMode
    }

    public func makeNSView(context: Context) -> NSVisualEffectView {
        let effectView = NSVisualEffectView()
        effectView.material = material
        effectView.blendingMode = blendingMode
        effectView.state = .active
        effectView.appearance = NSAppearance(named: .darkAqua)
        return effectView
    }

    public func updateNSView(_ nsView: NSVisualEffectView, context: Context) {
        nsView.material = material
        nsView.blendingMode = blendingMode
        nsView.appearance = NSAppearance(named: .darkAqua)
    }
}

// MARK: - Native Window Drag Area

/// An AppKit-backed view that enables native, butter-smooth macOS window dragging upon clicking and dragging.
public struct WindowDragAreaView: NSViewRepresentable {
    public init() {}

    public func makeNSView(context: Context) -> DragHandleNSView {
        DragHandleNSView()
    }

    public func updateNSView(_ nsView: DragHandleNSView, context: Context) {}

    public final class DragHandleNSView: NSView {
        public override var mouseDownCanMoveWindow: Bool {
            return true
        }

        public override func acceptsFirstMouse(for event: NSEvent?) -> Bool {
            return true
        }

        public override func mouseDown(with event: NSEvent) {
            window?.performDrag(with: event)
        }
    }
}

// MARK: - AppKit Drag & Drop Overlay (Premiere Pro, After Effects, Finder, Browsers, etc.)

/// Transparent AppKit overlay view supporting both click-to-paste and click-and-drag (`>= 5pt`)
/// into external apps (Premiere Pro, After Effects, DaVinci Resolve, Photoshop, Finder, Chrome, Notes).
public struct DraggableItemOverlay: NSViewRepresentable {
    public let item: ClipboardItem
    public let onTap: () -> Void
    public let onHoverChange: ((Bool) -> Void)?

    public init(
        item: ClipboardItem,
        onTap: @escaping () -> Void,
        onHoverChange: ((Bool) -> Void)? = nil
    ) {
        self.item = item
        self.onTap = onTap
        self.onHoverChange = onHoverChange
    }

    public func makeNSView(context: Context) -> DragSourceNSView {
        let view = DragSourceNSView()
        view.item = item
        view.onTap = onTap
        view.onHoverChange = onHoverChange
        return view
    }

    public func updateNSView(_ nsView: DragSourceNSView, context: Context) {
        nsView.item = item
        nsView.onTap = onTap
        nsView.onHoverChange = onHoverChange
    }

    public final class DragSourceNSView: NSView, NSDraggingSource {
        public var item: ClipboardItem?
        public var onTap: (() -> Void)?
        public var onHoverChange: ((Bool) -> Void)?

        private var mouseDownEvent: NSEvent?
        private var didStartDrag: Bool = false

        public override var acceptsFirstResponder: Bool { false }

        public override func acceptsFirstMouse(for event: NSEvent?) -> Bool {
            return true
        }

        public override func updateTrackingAreas() {
            super.updateTrackingAreas()
            for area in trackingAreas {
                removeTrackingArea(area)
            }
            let options: NSTrackingArea.Options = [.mouseEnteredAndExited, .activeAlways, .inVisibleRect]
            addTrackingArea(NSTrackingArea(rect: .zero, options: options, owner: self, userInfo: nil))
        }

        public override func mouseEntered(with event: NSEvent) {
            onHoverChange?(true)
        }

        public override func mouseExited(with event: NSEvent) {
            onHoverChange?(false)
        }

        public override func mouseDown(with event: NSEvent) {
            self.mouseDownEvent = event
            self.didStartDrag = false
        }

        public override func mouseDragged(with event: NSEvent) {
            guard !didStartDrag, let startEvent = mouseDownEvent, let item = item else { return }
            let dx = event.locationInWindow.x - startEvent.locationInWindow.x
            let dy = event.locationInWindow.y - startEvent.locationInWindow.y
            if hypot(dx, dy) >= 5.0 {
                didStartDrag = true
                startDragSession(for: item, with: startEvent)
            }
        }

        public override func mouseUp(with event: NSEvent) {
            let shouldTap = !didStartDrag && mouseDownEvent != nil
            self.mouseDownEvent = nil
            self.didStartDrag = false
            if shouldTap {
                onTap?()
            }
        }

        private func startDragSession(for item: ClipboardItem, with event: NSEvent) {
            let writer = ClipboardDragHelper.makePasteboardWriter(for: item)
            let draggingItem = NSDraggingItem(pasteboardWriter: writer)
            let preview = createDragPreviewImage(for: item)

            let localPoint = convert(event.locationInWindow, from: nil)
            let dragFrame = NSRect(
                x: localPoint.x - preview.size.width / 2,
                y: localPoint.y - preview.size.height / 2,
                width: preview.size.width,
                height: preview.size.height
            )
            draggingItem.setDraggingFrame(dragFrame, contents: preview)

            (self.window as? FloatingPanel)?.isDraggingContent = true
            beginDraggingSession(with: [draggingItem], event: event, source: self)
        }

        private func createDragPreviewImage(for item: ClipboardItem) -> NSImage {
            if item.isImage, let img = item.thumbnailImage {
                let orig = img.size
                let maxDim: CGFloat = 140
                let scale = min(1.0, maxDim / max(1, max(orig.width, orig.height)))
                let previewSize = NSSize(
                    width: max(40, orig.width * scale),
                    height: max(40, orig.height * scale)
                )
                return NSImage(size: previewSize, flipped: false) { rect in
                    let path = NSBezierPath(roundedRect: rect, xRadius: 6, yRadius: 6)
                    path.addClip()
                    img.draw(in: rect)
                    NSColor.white.withAlphaComponent(0.35).setStroke()
                    path.lineWidth = 1.5
                    path.stroke()
                    return true
                }
            } else {
                let snippet = String(item.text.prefix(40)).replacingOccurrences(of: "\n", with: " ")
                let isSingleEmoji = snippet.count <= 3
                let font = NSFont.systemFont(ofSize: isSingleEmoji ? 22 : 12, weight: .medium)
                let attrs: [NSAttributedString.Key: Any] = [
                    .font: font,
                    .foregroundColor: NSColor.white
                ]
                let textSize = (snippet as NSString).size(withAttributes: attrs)
                let horizontalPad: CGFloat = isSingleEmoji ? 16 : 22
                let pillSize = NSSize(
                    width: min(220, max(38, textSize.width + horizontalPad)),
                    height: isSingleEmoji ? 38 : 30
                )
                return NSImage(size: pillSize, flipped: false) { rect in
                    let path = NSBezierPath(roundedRect: rect, xRadius: 7, yRadius: 7)
                    NSColor(calibratedWhite: 0.14, alpha: 0.94).setFill()
                    path.fill()
                    NSColor(red: 0.38, green: 0.80, blue: 1.0, alpha: 0.85).setStroke()
                    path.lineWidth = 1.5
                    path.stroke()

                    let textRect = NSRect(
                        x: (pillSize.width - textSize.width) / 2,
                        y: (pillSize.height - textSize.height) / 2,
                        width: textSize.width,
                        height: textSize.height
                    )
                    (snippet as NSString).draw(
                        with: textRect,
                        options: [.usesLineFragmentOrigin, .truncatesLastVisibleLine],
                        attributes: attrs
                    )
                    return true
                }
            }
        }

        // MARK: - NSDraggingSource

        public func draggingSession(_ session: NSDraggingSession, sourceOperationMaskFor context: NSDraggingContext) -> NSDragOperation {
            return context == .outsideApplication ? .copy : [.copy, .generic]
        }

        public func draggingSession(_ session: NSDraggingSession, willBeginAt screenPoint: NSPoint) {
            (self.window as? FloatingPanel)?.isDraggingContent = true
        }

        public func draggingSession(_ session: NSDraggingSession, endedAt screenPoint: NSPoint, operation: NSDragOperation) {
            (self.window as? FloatingPanel)?.isDraggingContent = false
            self.mouseDownEvent = nil
            self.didStartDrag = false
        }
    }
}

// MARK: - Launcher Navigation Tabs

/// Navigation tabs matching Windows 11 Win+V style.
public enum LauncherTab: String, CaseIterable, Identifiable {
    case clipboard = "Clipboard"
    case emojis = "Emojis"

    public var id: String { rawValue }

    public var icon: String {
        switch self {
        case .clipboard:
            return "doc.on.clipboard"
        case .emojis:
            return "face.smiling"
        }
    }
}

// MARK: - View State Management

/// Internal observable state object managing navigation tabs, selection, and filters.
@MainActor
final class ClipboardViewState: ObservableObject {
    @Published var selectedTab: LauncherTab = .clipboard
    @Published var selectedIndex: Int = 0
    @Published var searchText: String = ""
    @Published var emojiSearchText: String = ""
    @Published var selectedEmojiCategory: String = "smileys"
    @Published var hoveredEmoji: String? = nil
    @Published var isHoveringCategoryBar: Bool = false
    @Published var isHoveringDragHandle: Bool = false
    var keyMonitor: Any?
    var scrollMonitor: Any?

    #if swift(>=6.0)
    isolated deinit {
        if let monitor = keyMonitor {
            NSEvent.removeMonitor(monitor)
        }
        if let monitor = scrollMonitor {
            NSEvent.removeMonitor(monitor)
        }
    }
    #else
    deinit {
        if let monitor = keyMonitor {
            NSEvent.removeMonitor(monitor)
        }
        if let monitor = scrollMonitor {
            NSEvent.removeMonitor(monitor)
        }
    }
    #endif
}

// MARK: - Clipboard Live View

/// A reactive container view that observes `ClipboardMonitor` and renders `ClipboardView`.
public struct ClipboardLiveView: View {
    @ObservedObject public var monitor: ClipboardMonitor
    public let onTogglePin: ((ClipboardItem) -> Void)?
    public let onSelect: (ClipboardItem) -> Void

    public init(
        monitor: ClipboardMonitor,
        onTogglePin: ((ClipboardItem) -> Void)? = nil,
        onSelect: @escaping (ClipboardItem) -> Void
    ) {
        self.monitor = monitor
        self.onTogglePin = onTogglePin
        self.onSelect = onSelect
    }

    public var body: some View {
        ClipboardView(
            items: monitor.items,
            onClear: { [weak monitor] in
                monitor?.clear()
            },
            onTogglePin: { [weak monitor] item in
                if let onTogglePin = onTogglePin {
                    onTogglePin(item)
                } else {
                    monitor?.togglePin(item: item)
                }
            },
            onSelect: onSelect
        )
    }
}

// MARK: - Clipboard View

/// A polished, dark-aesthetic clipboard history and emoji launcher modeled after Windows 11 (`Win + V`).
///
/// Features:
/// - **Frosted Glass Acrylic**: Dark acrylic backdrop with subtle 1px border.
/// - **Top Navigation Bar**: Seamless toggle between "Clipboard History" and "Emojis".
/// - **Pinning & Favorites**: Pinned section at top; pinned items persist across app restarts and reboots.
/// - **Categorized Emoji Picker**: Grid of emojis categorized by Smileys, Gestures, Animals, Food, Objects, and Symbols.
/// - **Auto-Paste Integration**: Clicking any history item or emoji closes launcher and auto-pastes instantly.
public struct ClipboardView: View {

    // MARK: - Properties

    public let items: [ClipboardItem]
    public let onClear: (() -> Void)?
    public let onTogglePin: ((ClipboardItem) -> Void)?
    public let onSelect: (ClipboardItem) -> Void

    @StateObject private var state = ClipboardViewState()

    // Windows 11 Accent Color: Fluent Cyan / Azure
    private let fluentAccent = Color(red: 0.38, green: 0.80, blue: 1.00)

    // MARK: - Initialization

    public init(
        items: [ClipboardItem],
        onClear: (() -> Void)? = nil,
        onTogglePin: ((ClipboardItem) -> Void)? = nil,
        onSelect: @escaping (ClipboardItem) -> Void
    ) {
        self.items = items
        self.onClear = onClear
        self.onTogglePin = onTogglePin
        self.onSelect = onSelect
    }

    // MARK: - Filtered & Sectioned Items

    private var filteredItems: [ClipboardItem] {
        let trimmed = state.searchText.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            return items
        }
        return items.filter { $0.text.localizedCaseInsensitiveContains(trimmed) }
    }

    private var pinnedItems: [ClipboardItem] {
        filteredItems.filter { $0.isPinned }
    }

    private var recentItems: [ClipboardItem] {
        filteredItems.filter { !$0.isPinned }
    }

    /// Flat display array: pinned items first, then recent items.
    /// Used for keyboard navigation index tracking.
    private var displayItems: [ClipboardItem] {
        pinnedItems + recentItems
    }

    // MARK: - Body

    public var body: some View {
        ZStack {
            // 1. Frosted Glass Backing + Dark Acrylic Tint
            FrostedGlassView(material: .popover, blendingMode: .behindWindow)
            Color.black.opacity(0.40)

            VStack(spacing: 0) {
                // 1. Draggable Top Grab Handle (Windows 11 / Floating Panel style)
                topDragHandleView

                // 2. Windows 11 Navigation Tab Bar (Clipboard vs Emojis)
                topTabBarView

                Divider()
                    .background(Color.white.opacity(0.08))

                // 3. Tab Content
                if state.selectedTab == .clipboard {
                    clipboardTabContent
                } else {
                    emojiTabContent
                }

                Divider()
                    .background(Color.white.opacity(0.08))

                // 4. Footer
                footerView
            }
        }
        .frame(width: 340, height: 440)
        .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .stroke(Color.white.opacity(0.14), lineWidth: 1)
        )
        .onAppear {
            setupEventMonitors()
        }
        .onDisappear {
            teardownEventMonitors()
        }
    }

    // MARK: - Draggable Top Handle & Tab Bar

    private var topDragHandleView: some View {
        Capsule()
            .fill(Color.white.opacity(state.isHoveringDragHandle ? 0.55 : 0.24))
            .frame(width: 40, height: 4)
            .allowsHitTesting(false)
            .frame(maxWidth: .infinity)
            .frame(height: 12)
            .padding(.top, 4)
            .background(WindowDragAreaView())
            .onHover { hovering in
                state.isHoveringDragHandle = hovering
            }
            .help("Drag to move window")
    }

    private var topTabBarView: some View {
        HStack(spacing: 4) {
            // Left: Compact, single-line Tab Switcher (never wraps or shifts width)
            HStack(spacing: 2) {
                tabButton(tab: .clipboard, title: "Clipboard", icon: "doc.on.clipboard")
                tabButton(tab: .emojis, title: "Emojis", icon: "face.smiling")
            }
            .fixedSize(horizontal: true, vertical: true)
            .layoutPriority(2)

            // Middle: Draggable empty space (shrinks gracefully without compressing tabs)
            WindowDragAreaView()
                .frame(height: 22)
                .frame(minWidth: 8, maxWidth: .infinity)
                .layoutPriority(-1)

            // Right: Clear & count badge (fixed single-line; opacity-toggled to prevent bar jump)
            HStack(spacing: 6) {
                if let onClear = onClear, !recentItems.isEmpty || !items.isEmpty {
                    Button(action: onClear) {
                        Text("Clear all")
                            .font(.system(size: 10.5, weight: .medium))
                            .foregroundColor(.white.opacity(0.65))
                            .lineLimit(1)
                    }
                    .buttonStyle(.plain)
                    .noFocusRing()
                    .fixedSize(horizontal: true, vertical: true)
                    .help("Clear unpinned history")
                }

                Text("\(items.count)")
                    .font(.system(size: 10.5, weight: .semibold, design: .rounded))
                    .foregroundColor(.white.opacity(0.70))
                    .lineLimit(1)
                    .padding(.horizontal, 5)
                    .padding(.vertical, 2)
                    .background(Color.white.opacity(0.10))
                    .cornerRadius(4)
                    .fixedSize(horizontal: true, vertical: true)
            }
            .fixedSize(horizontal: true, vertical: true)
            .layoutPriority(2)
            .opacity(state.selectedTab == .clipboard ? 1 : 0)
            .allowsHitTesting(state.selectedTab == .clipboard)
        }
        .padding(.horizontal, 10)
        .padding(.top, 1)
        .padding(.bottom, 3)
        .background(WindowDragAreaView())
    }

    private func tabButton(tab: LauncherTab, title: String, icon: String) -> some View {
        let isSelected = state.selectedTab == tab
        return Button(action: {
            state.selectedTab = tab
        }) {
            VStack(spacing: 3) {
                HStack(spacing: 4) {
                    Image(systemName: isSelected ? "\(icon).fill" : icon)
                        .font(.system(size: 10.5, weight: .medium))
                        .frame(width: 12, height: 12)
                    Text(title)
                        .font(.system(size: 11, weight: .medium))
                        .lineLimit(1)
                }
                .foregroundColor(isSelected ? fluentAccent : .white.opacity(0.60))

                // Subtle indicator dot beneath the active tab (no box!)
                Circle()
                    .fill(isSelected ? fluentAccent : Color.clear)
                    .frame(width: 4, height: 4)
            }
            .padding(.horizontal, 6)
            .padding(.top, 3)
            .padding(.bottom, 2)
            .fixedSize(horizontal: true, vertical: true)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .noFocusRing()
        .fixedSize(horizontal: true, vertical: true)
    }

    // MARK: - Clipboard Tab Content

    private var clipboardTabContent: some View {
        VStack(spacing: 0) {
            // Search Bar
            if !items.isEmpty {
                searchBarView
            }

            // List of Items or Empty State
            if displayItems.isEmpty {
                emptyStateView
            } else {
                cardListView
            }
        }
    }

    private var searchBarView: some View {
        HStack(spacing: 6) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 11, weight: .medium))
                .foregroundColor(.white.opacity(0.40))

            TextField("Search history...", text: $state.searchText)
                .textFieldStyle(.plain)
                .font(.system(size: 11))
                .foregroundColor(.white)

            if !state.searchText.isEmpty {
                Button(action: { state.searchText = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.system(size: 11))
                        .foregroundColor(.white.opacity(0.50))
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(Color.white.opacity(0.06))
        .cornerRadius(6)
        .overlay(
            RoundedRectangle(cornerRadius: 6)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
    }

    private var cardListView: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 6) {
                    // 1. PINNED SECTION (if any items are pinned)
                    if !pinnedItems.isEmpty {
                        HStack(spacing: 5) {
                            Image(systemName: "pin.fill")
                                .font(.system(size: 9))
                            Text("PINNED")
                                .font(.system(size: 10, weight: .bold))
                            Spacer()
                            Text("\(pinnedItems.count)")
                                .font(.system(size: 9, weight: .semibold, design: .rounded))
                                .foregroundColor(.white.opacity(0.50))
                        }
                        .foregroundColor(fluentAccent)
                        .padding(.horizontal, 4)
                        .padding(.top, 4)

                        ForEach(Array(pinnedItems.enumerated()), id: \.element.id) { index, item in
                            let isSelected = index == state.selectedIndex
                            ClipboardCardView(
                                item: item,
                                isSelected: isSelected,
                                accentColor: fluentAccent,
                                onHover: {
                                    state.selectedIndex = index
                                },
                                onTap: {
                                    onSelect(item)
                                },
                                onTogglePin: {
                                    onTogglePin?(item)
                                }
                            )
                            .id(item.id)
                        }

                        if !recentItems.isEmpty {
                            HStack(spacing: 5) {
                                Image(systemName: "clock")
                                    .font(.system(size: 9))
                                Text("RECENT")
                                    .font(.system(size: 10, weight: .bold))
                                Spacer()
                            }
                            .foregroundColor(.white.opacity(0.50))
                            .padding(.horizontal, 4)
                            .padding(.top, 6)
                        }
                    }

                    // 2. RECENT / UNPINNED ITEMS
                    ForEach(Array(recentItems.enumerated()), id: \.element.id) { subIndex, item in
                        let overallIndex = pinnedItems.count + subIndex
                        let isSelected = overallIndex == state.selectedIndex
                        ClipboardCardView(
                            item: item,
                            isSelected: isSelected,
                            accentColor: fluentAccent,
                            onHover: {
                                state.selectedIndex = overallIndex
                            },
                            onTap: {
                                onSelect(item)
                            },
                            onTogglePin: {
                                onTogglePin?(item)
                            }
                        )
                        .id(item.id)
                    }
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
            }
            .onIndexChange(of: state.selectedIndex) { newIndex in
                if displayItems.indices.contains(newIndex) {
                    withAnimation(.easeInOut(duration: 0.08)) {
                        proxy.scrollTo(displayItems[newIndex].id, anchor: .center)
                    }
                }
            }
        }
    }

    private var emptyStateView: some View {
        VStack(spacing: 8) {
            Spacer()
            Image(systemName: "clipboard")
                .font(.system(size: 32, weight: .light))
                .foregroundColor(.white.opacity(0.30))

            Text(items.isEmpty ? "Clipboard is empty" : "No matching items")
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.70))

            Text("Copied plain text and photos will appear here.")
                .font(.system(size: 11))
                .foregroundColor(.white.opacity(0.40))
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // MARK: - Emoji Tab Content

    private var emojiTabContent: some View {
        EmojiPickerView(
            accentColor: fluentAccent,
            searchQuery: $state.emojiSearchText,
            selectedCategory: $state.selectedEmojiCategory,
            hoveredEmoji: $state.hoveredEmoji,
            isHoveringCategoryBar: $state.isHoveringCategoryBar,
            onSelectEmoji: { emoji in
                onSelect(ClipboardItem(text: emoji))
            }
        )
    }

    // MARK: - Footer

    private var footerView: some View {
        HStack(spacing: 6) {
            if state.selectedTab == .clipboard {
                Text("Click Paste")
                Text("•")
                    .opacity(0.4)
                Text("Drag to Apps")
                Text("•")
                    .opacity(0.4)
                Text("Esc Close")
            } else {
                Text("Click Paste / Drag")
                Text("•")
                    .opacity(0.4)
                Text("Esc Close")
            }
            Spacer()

            Text("© zenrakib")
                .font(.system(size: 9.5, weight: .medium))
                .foregroundColor(.white.opacity(0.32))
                .help("ClipBoard by Rakib Hasan (zenrakib@gmail.com)")
        }
        .font(.system(size: 10, weight: .regular))
        .foregroundColor(.white.opacity(0.45))
        .padding(.horizontal, 14)
        .padding(.vertical, 7)
        .background(Color.black.opacity(0.20))
    }

    // MARK: - Event Monitors (Keyboard & Category Scroll Wheel)

    private func setupEventMonitors() {
        teardownEventMonitors()

        // 1. Keyboard event monitor for clipboard list navigation
        state.keyMonitor = NSEvent.addLocalMonitorForEvents(matching: [.keyDown]) { event in
            guard state.selectedTab == .clipboard else {
                return event
            }

            switch event.keyCode {
            case 125: // Down Arrow
                let count = displayItems.count
                if count > 0 {
                    state.selectedIndex = min(count - 1, state.selectedIndex + 1)
                }
                return nil

            case 126: // Up Arrow
                let count = displayItems.count
                if count > 0 {
                    state.selectedIndex = max(0, state.selectedIndex - 1)
                }
                return nil

            case 36, 76: // Enter / Keypad Return
                if displayItems.indices.contains(state.selectedIndex) {
                    onSelect(displayItems[state.selectedIndex])
                }
                return nil

            default:
                return event
            }
        }

        // 2. Scroll wheel event monitor: translates vertical mouse wheel scrolling over category bar to horizontal category navigation
        state.scrollMonitor = NSEvent.addLocalMonitorForEvents(matching: [.scrollWheel]) { [weak state] event in
            guard let state = state,
                  state.selectedTab == .emojis,
                  state.isHoveringCategoryBar else {
                return event
            }

            // Mouse wheel vertical scrolling (deltaY without deltaX)
            if event.scrollingDeltaX == 0 && abs(event.scrollingDeltaY) > 1.2 {
                let direction = event.scrollingDeltaY < 0 ? 1 : -1
                let categories = EmojiPickerView.categories
                if let currentIndex = categories.firstIndex(where: { $0.id == state.selectedEmojiCategory }) {
                    let nextIndex = min(max(0, currentIndex + direction), categories.count - 1)
                    if nextIndex != currentIndex {
                        state.selectedEmojiCategory = categories[nextIndex].id
                        state.emojiSearchText = ""
                    }
                }
                return nil // Event handled, prevent bubbled scroll
            }
            return event
        }
    }

    private func teardownEventMonitors() {
        if let monitor = state.keyMonitor {
            NSEvent.removeMonitor(monitor)
            state.keyMonitor = nil
        }
        if let monitor = state.scrollMonitor {
            NSEvent.removeMonitor(monitor)
            state.scrollMonitor = nil
        }
    }
}

// MARK: - Minimalist Card Row with Pin Button

/// Individual minimalist card representing a clipboard item (Text or Image) with pinning support.
struct ClipboardCardView: View {
    let item: ClipboardItem
    let isSelected: Bool
    let accentColor: Color
    let onHover: () -> Void
    let onTap: () -> Void
    let onTogglePin: (() -> Void)?

    var body: some View {
        HStack(spacing: 0) {
            // Windows 11 Accent Indicator Bar
            Rectangle()
                .fill(isSelected ? accentColor : Color.clear)
                .frame(width: 3)
                .cornerRadius(1.5)
                .padding(.vertical, 5)

            if item.isImage {
                // Image Card Layout: overlay drag handler over image + metadata, keeping pinButton on top
                ZStack(alignment: .topTrailing) {
                    VStack(alignment: .leading, spacing: 6) {
                        if let nsImage = item.thumbnailImage {
                            Image(nsImage: nsImage)
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(maxWidth: .infinity, maxHeight: 110, alignment: .leading)
                                .clipShape(RoundedRectangle(cornerRadius: 4, style: .continuous))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 4, style: .continuous)
                                        .stroke(Color.white.opacity(0.12), lineWidth: 1)
                                )
                        }

                        // Metadata Pill Bar
                        HStack(spacing: 6) {
                            HStack(spacing: 3) {
                                Image(systemName: "photo")
                                    .font(.system(size: 8))
                                if let dim = item.imageDimensions {
                                    Text("\(Int(dim.width)) × \(Int(dim.height))")
                                        .font(.system(size: 9, weight: .medium, design: .monospaced))
                                } else {
                                    Text("Image")
                                        .font(.system(size: 9, weight: .medium))
                                }
                            }
                            .foregroundColor(.white.opacity(0.75))
                            .padding(.horizontal, 5)
                            .padding(.vertical, 2)
                            .background(Color.white.opacity(0.10))
                            .cornerRadius(3)

                            if let count = item.imageData?.count {
                                Text(formatByteCount(count))
                                    .font(.system(size: 9))
                                    .foregroundColor(.white.opacity(0.45))
                            }

                            Text("•")
                                .font(.system(size: 9))
                                .foregroundColor(.white.opacity(0.25))

                            Text(item.timestamp, style: .time)
                                .font(.system(size: 9, weight: .medium))
                                .foregroundColor(.white.opacity(0.45))

                            Spacer()
                        }
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 8)
                    .contentShape(Rectangle())
                    .overlay(
                        DraggableItemOverlay(
                            item: item,
                            onTap: onTap,
                            onHoverChange: { hovering in
                                if hovering { onHover() }
                            }
                        )
                    )

                    // Pin Icon Button (Top-Right on Image - uncovered by drag overlay)
                    pinButton
                        .padding(4)
                        .background(
                            Circle()
                                .fill(Color.black.opacity(0.65))
                        )
                        .padding(12)
                }
            } else {
                // Text Card Layout
                HStack(alignment: .top, spacing: 6) {
                    VStack(alignment: .leading, spacing: 5) {
                        // Plain-text preview, line-clamped to 2 lines
                        Text(item.text)
                            .font(.system(size: 12, weight: .regular))
                            .foregroundColor(.white.opacity(isSelected ? 1.0 : 0.85))
                            .lineLimit(2)
                            .truncationMode(.tail)
                            .multilineTextAlignment(.leading)
                            .frame(maxWidth: .infinity, alignment: .leading)

                        // Timestamp & Character Count
                        HStack(spacing: 6) {
                            Text(item.timestamp, style: .time)
                                .font(.system(size: 10, weight: .medium))
                                .foregroundColor(.white.opacity(0.40))

                            Text("•")
                                .font(.system(size: 9))
                                .foregroundColor(.white.opacity(0.25))

                            Text("\(item.text.count) chars")
                                .font(.system(size: 10))
                                .foregroundColor(.white.opacity(0.40))

                            Spacer()
                        }
                    }
                    .contentShape(Rectangle())
                    .overlay(
                        DraggableItemOverlay(
                            item: item,
                            onTap: onTap,
                            onHoverChange: { hovering in
                                if hovering { onHover() }
                            }
                        )
                    )

                    // Pin Icon Button (Top-Right on Text - uncovered by drag overlay)
                    pinButton
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 8)
            }
        }
        .background(
            RoundedRectangle(cornerRadius: 6, style: .continuous)
                .fill(isSelected ? Color.white.opacity(0.12) : Color.white.opacity(0.04))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 6, style: .continuous)
                .stroke(isSelected ? Color.white.opacity(0.20) : Color.white.opacity(0.06), lineWidth: 1)
        )
        .contentShape(Rectangle())
        .onHover { isHovering in
            if isHovering {
                onHover()
            }
        }
    }

    private var pinButton: some View {
        Button(action: {
            onTogglePin?()
        }) {
            Image(systemName: item.isPinned ? "pin.fill" : "pin")
                .font(.system(size: 10, weight: .semibold))
                .foregroundColor(item.isPinned ? accentColor : .white.opacity(isSelected ? 0.70 : 0.25))
                .padding(5)
                .background(
                    Circle()
                        .fill(item.isPinned ? accentColor.opacity(0.18) : (isSelected ? Color.white.opacity(0.08) : Color.clear))
                )
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .noFocusRing()
        .help(item.isPinned ? "Unpin item" : "Pin item to favorites")
    }

    private func formatByteCount(_ bytes: Int) -> String {
        let formatter = ByteCountFormatter()
        formatter.allowedUnits = [.useKB, .useMB]
        formatter.countStyle = .file
        return formatter.string(fromByteCount: Int64(bytes))
    }
}

// MARK: - Windows 11 Emoji Picker View

/// Categorized, searchable Emoji grid matching the Windows 11 Win+V experience.
struct EmojiPickerView: View {
    let accentColor: Color
    @Binding var searchQuery: String
    @Binding var selectedCategory: String
    @Binding var hoveredEmoji: String?
    @Binding var isHoveringCategoryBar: Bool
    let onSelectEmoji: (String) -> Void

    // Emoji Category Model
    struct EmojiCategory: Identifiable {
        let id: String
        let name: String
        let icon: String
        let emojis: [String]
    }

    // Categorized Emoji Catalog
    static let categories: [EmojiCategory] = [
        EmojiCategory(
            id: "smileys",
            name: "Smileys",
            icon: "face.smiling",
            emojis: [
                "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃",
                "😉", "😊", "😇", "🥰", "😍", "🤩", "😘", "😗", "😚", "😙",
                "😋", "😛", "😜", "🤪", "😝", "🤑", "🤗", "🤭", "🤫", "🤔",
                "🤐", "🤨", "😐", "😑", "😶", "😏", "😒", "🙄", "😬", "🤥",
                "😌", "😔", "😪", "🤤", "😴", "😷", "🤒", "🤕", "🤢", "🤮",
                "🤧", "🥵", "🥶", "🥴", "😵", "🤯", "🤠", "🥳", "🥸", "😎",
                "🤓", "🧐", "😕", "😟", "🙁", "😮", "😯", "😲", "😳", "🥺",
                "😦", "😧", "😨", "😰", "😥", "😢", "😭", "😱", "😖", "😣",
                "😞", "😓", "😩", "😫", "🥱", "😤", "😡", "😠", "🤬", "😈",
                "👿", "💀", "☠️", "💩", "🤡", "👹", "👺", "👻", "👽", "🤖"
            ]
        ),
        EmojiCategory(
            id: "gestures",
            name: "Gestures",
            icon: "hand.raised",
            emojis: [
                "👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤌", "🤏", "✌️", "🤞",
                "🫰", "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️",
                "👍", "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌", "👐", "🤲",
                "🤝", "🙏", "✍️", "💅", "🤳", "💪", "🦾", "🦿", "🦵", "🦶",
                "👂", "🦻", "👃", "🫀", "🫁", "🧠", "🦷", "🦴", "👀", "👁️",
                "👅", "👄", "🫦", "👤", "👥", "🫂"
            ]
        ),
        EmojiCategory(
            id: "animals",
            name: "Animals",
            icon: "leaf",
            emojis: [
                "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐻‍❄️", "🐨",
                "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🐒", "🐔", "🐧", "🐦",
                "🐤", "🦆", "🦅", "🦉", "🦇", "🐺", "🐗", "🐴", "🦄", "🐝",
                "🐛", "🦋", "🐌", "🐞", "🐜", "🪰", "🪲", "🦟", "🦗", "🕷️",
                "🐢", "🐍", "🦎", "🐙", "🦑", "🦐", "🦞", "🦀", "🐠", "🐟",
                "🐬", "🐳", "🦈", "🐊", "🐅", "🐆", "🦓", "🦍", "🐘", "🦛",
                "🌲", "🌳", "🌴", "🌱", "🌿", "☘️", "🍀", "🍃", "🍂", "🍁",
                "🍄", "🌾", "💐", "🌷", "🌹", "🌺", "🌸", "🌼", "🌻", "☀️",
                "🌤️", "⛅️", "☁️", "🌧️", "⛈️", "🌩️", "❄️", "☃️", "🔥", "🌈"
            ]
        ),
        EmojiCategory(
            id: "food",
            name: "Food",
            icon: "cup.and.saucer",
            emojis: [
                "🍏", "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐",
                "🍒", "🍑", "🥭", "🍍", "🥥", "🥝", "🍅", "🥑", "🥦", "🥬",
                "🥒", "🌶️", "🌽", "🥕", "🥔", "🍠", "🥐", "🥯", "🍞", "🥖",
                "🥨", "🧀", "🥚", "🍳", "🧈", "🥞", "🧇", "🥓", "🥩", "🍗",
                "🌭", "🍔", "🍟", "🍕", "🥪", "🌮", "🌯", "🥗", "🥘", "🍝",
                "🍜", "🍲", "🍛", "🍣", "🍱", "🥟", "🍤", "🍙", "🍚", "🍦",
                "🍩", "🍪", "🎂", "🍰", "🧁", "🍫", "🍬", "🍭", "🍿", "☕️",
                "🍵", "🧃", "🥤", "🧋", "🍶", "🍺", "🍻", "🥂", "🍷", "🥃"
            ]
        ),
        EmojiCategory(
            id: "objects",
            name: "Objects",
            icon: "gamecontroller",
            emojis: [
                "⚽️", "🏀", "🏈", "⚾️", "🥎", "🎾", "🏐", "🏉", "🥏", "🎱",
                "🏓", "🏸", "🏒", "🥊", "🥋", "🎯", "🎳", "🎮", "🎲", "🧩",
                "🚗", "🚕", "🚙", "🚌", "🏎️", "🚓", "🚑", "🚒", "🚲", "🛵",
                "🏍️", "✈️", "🚀", "🛸", "⛵️", "🚢", "📱", "💻", "⌨️", "🖥️",
                "📷", "📹", "🎥", "📺", "📻", "🎙️", "⏰", "⏱️", "⏳", "💡",
                "🔦", "🕯️", "💵", "💰", "💳", "💎", "⚖️", "🔧", "🔨", "⚒️",
                "🛠️", "⚙️", "🧲", "💣", "🔪", "🛡️", "🔮", "🩺", "💊", "🩹"
            ]
        ),
        EmojiCategory(
            id: "symbols",
            name: "Symbols",
            icon: "heart",
            emojis: [
                "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
                "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "☮️",
                "✝️", "☯️", "🕉️", "✡️", "☸️", "♈️", "♉️", "♊️", "♋️", "♌️",
                "♍️", "♎️", "♏️", "♐️", "♑️", "♒️", "♓️", "⚠️", "⛔️", "🚫",
                "✅", "❌", "⭕️", "🛑", "💯", "💢", "♨️", "❗️", "❓", "‼️",
                "⁉️", "♻️", "🌐", "💤", "🆗", "🆙", "🆒", "🆕", "0️⃣", "1️⃣",
                "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "▶️",
                "⏸️", "⏹️", "⏺️", "⏩", "⏪", "🔼", "🔽", "➡️", "⬅️", "⬆️",
                "⬇️", "🎵", "🎶", "➕", "➖", "✖️", "➗", "🟰", "♾️", "💲"
            ]
        )
    ]

    private var currentIndex: Int {
        Self.categories.firstIndex(where: { $0.id == selectedCategory }) ?? 0
    }

    private func navigateCategory(direction: Int, proxy: ScrollViewProxy) {
        let count = Self.categories.count
        let nextIndex = min(max(0, currentIndex + direction), count - 1)
        guard nextIndex != currentIndex else { return }
        let nextCat = Self.categories[nextIndex]
        selectedCategory = nextCat.id
        searchQuery = ""
        withAnimation(.easeInOut(duration: 0.15)) {
            proxy.scrollTo(nextCat.id, anchor: .center)
        }
    }

    /// Common conversational aliases mapped to emojis so natural keywords
    /// (e.g., "happy", "love", "lol", "sad", "yes", "money", "party", "fire") match seamlessly.
    private static let emojiAliases: [String: String] = [
        // Smileys & Emotions
        "😀": "happy smile grin joy cheerful glad",
        "😃": "happy smile grin joy excited",
        "😄": "happy smile laugh grin joy glad haha",
        "😁": "happy grin smile teeth excited haha",
        "😆": "laugh haha lol hilarious happy",
        "😅": "sweat relief whew nervous laugh haha",
        "🤣": "rofl lmao lol haha laugh funny tears",
        "😂": "lol laugh funny haha tears cry joy lmao",
        "🙂": "smile happy polite ok",
        "🙃": "upside down sarcasm silly",
        "😉": "wink flirt playful joke",
        "😊": "happy smile blush warm cute",
        "😇": "angel halo innocent bless good",
        "🥰": "love adore crush hearts cute romantic",
        "😍": "love heart eyes crush adore romantic wow",
        "🤩": "star excited wow amazing famous",
        "😘": "kiss love romantic hug flirt muah",
        "😗": "kiss",
        "😚": "kiss blush",
        "😙": "kiss smile",
        "😋": "yum delicious food tasty hungry",
        "😛": "tongue silly playful",
        "😜": "wink tongue crazy silly playful",
        "🤪": "crazy silly goofy wild",
        "😝": "tongue silly laugh",
        "🤑": "money rich dollar cash wealth",
        "🤗": "hug warm open care welcome",
        "🤭": "oops giggles shy secret surprise",
        "🤫": "quiet shh secret silence whisper",
        "🤔": "think hmm wonder question idea doubt",
        "🤐": "zipped quiet secret silent lips",
        "🤨": "suspicious doubt eyebrow wait",
        "😐": "neutral meh blank ok",
        "😑": "expressionless blank annoyed meh",
        "😶": "silent speechless quiet blank",
        "😏": "smirk smug flirt sly",
        "😒": "unamused annoyed meh bored",
        "🙄": "eyeroll annoyed whatever sarcastic",
        "😬": "grimace cringe awkward nervous oops",
        "🤥": "lie liar pinocchio",
        "😌": "relieved calm peaceful zen",
        "😔": "sad sorry pensive disappointed down",
        "😪": "sleepy tired sad",
        "🤤": "drool hungry yum want",
        "😴": "sleep tired zzz nap night",
        "😷": "sick mask doctor ill flu",
        "🤒": "sick fever ill thermometer",
        "🤕": "hurt bandage injured pain",
        "🤢": "sick gross vomit disgusted",
        "🤮": "vomit puke sick gross",
        "🤧": "sneeze cold sick allergies",
        "🥵": "hot sweat heat spicy",
        "🥶": "cold freeze ice chill winter",
        "🥴": "drunk dizzy woozy",
        "😵": "dizzy knocked out shock",
        "🤯": "mind blown shocked omg amazed explode",
        "🤠": "cowboy hat yeehaw",
        "🥳": "party celebrate birthday congrats hooray",
        "🥸": "disguise glasses mustache funny",
        "😎": "cool sunglasses awesome chill swag",
        "🤓": "nerd smart glasses geek study",
        "🧐": "monocle inspect classy think",
        "😕": "confused unsure sad",
        "😟": "worried anxious concerned",
        "🙁": "sad frown unhappy",
        "😮": "wow surprise shocked open mouth",
        "😯": "hushed surprise quiet wow",
        "😲": "astonished shocked amazed wow omg",
        "😳": "flushed embarrassed blush shy",
        "🥺": "pleading puppy eyes please sad cute",
        "😦": "frown surprise",
        "😧": "anguish scared worry",
        "😨": "fearful scared afraid omg",
        "😰": "anxious nervous sweat fear",
        "😥": "sad relief sweat disappointed",
        "😢": "cry sad tear unhappy",
        "😭": "cry sob tears sad heartbroken",
        "😱": "scream shock omg terrified fear horror",
        "😖": "confounded frustrated",
        "😣": "persevere struggle",
        "😞": "disappointed sad sorry down",
        "😓": "sweat sad tired hard work",
        "😩": "weary tired frustrated",
        "😫": "tired exhausted frustrated",
        "🥱": "yawn tired sleepy bored",
        "😤": "triumph frustrated angry huff",
        "😡": "angry mad furious rage red",
        "😠": "angry mad upset",
        "🤬": "angry curse swear mad rage",
        "😈": "devil evil naughty purple",
        "👿": "devil angry evil imp",
        "💀": "skull dead death lol skeleton",
        "☠️": "skull crossbones death danger pirate",
        "💩": "poop shit crap funny",
        "🤡": "clown funny circus joker",
        "👹": "ogre monster mask",
        "👺": "goblin monster",
        "👻": "ghost boo halloween spooky",
        "👽": "alien ufo space",
        "👾": "alien game arcade retro",
        "🤖": "robot ai bot tech cyborg",

        // Gestures & People
        "👋": "wave hi hello bye goodbye hey",
        "🤚": "hand stop raise",
        "🖐️": "hand five high five stop",
        "✋": "hand stop high five",
        "🖖": "vulcan spock star trek",
        "👌": "ok okay nice good perfect zero",
        "🤌": "pinched fingers italian chef kiss",
        "🤏": "small tiny little pinch bit",
        "✌️": "peace victory two chill",
        "🤞": "luck fingers crossed hope wish",
        "🫰": "heart snap love money",
        "🤟": "love you rock",
        "🤘": "rock metal horns cool",
        "🤙": "call me shaka chill phone",
        "👈": "left point finger",
        "👉": "right point finger",
        "👆": "up point above",
        "🖕": "middle finger angry",
        "👇": "down point below",
        "☝️": "one up point idea wait",
        "👍": "thumbs up like yes ok good approve agree great",
        "👎": "thumbs down dislike no bad reject",
        "✊": "fist power solidarity punch",
        "👊": "punch fist bump bro",
        "🤛": "fist bump left",
        "🤜": "fist bump right",
        "👏": "clap applause bravo congrats well done",
        "🙌": "hands up celebrate hooray praise yay",
        "👐": "open hands hug",
        "🤲": "palms pray dua",
        "🤝": "handshake deal agree partner welcome",
        "🙏": "pray please thank you thanks namaste hope sorry",
        "✍️": "write pen draw sign note",
        "💅": "nails polish slay sass beauty",
        "🤳": "selfie camera phone",
        "💪": "muscle strong power gym flex bicep workout",
        "👀": "eyes look see watch stare",
        "👁️": "eye see watch",
        "🧠": "brain smart mind think iq",

        // Animals & Nature
        "🐶": "dog puppy pet woof",
        "🐱": "cat kitty pet meow",
        "🐭": "mouse rat",
        "🐹": "hamster pet",
        "🐰": "rabbit bunny easter",
        "🦊": "fox",
        "🐻": "bear",
        "🐼": "panda cute",
        "🐨": "koala",
        "🐯": "tiger",
        "🦁": "lion king",
        "🐮": "cow moo",
        "🐷": "pig oink",
        "🐸": "frog",
        "🐵": "monkey",
        "🐒": "monkey",
        "🐔": "chicken bird",
        "🐧": "penguin cold",
        "🐦": "bird tweet",
        "🐤": "chick bird baby",
        "🦆": "duck",
        "🦅": "eagle",
        "🦉": "owl wise night",
        "🦇": "bat halloween",
        "🐺": "wolf",
        "🐗": "boar",
        "🐴": "horse",
        "🦄": "unicorn magic",
        "🐝": "bee honey buzz",
        "🐛": "bug worm",
        "🦋": "butterfly pretty",
        "🐌": "snail slow",
        "🐞": "ladybug bug",
        "🐜": "ant bug",
        "🐢": "turtle slow",
        "🐍": "snake",
        "🦎": "lizard",
        "🐙": "octopus sea",
        "🐬": "dolphin sea ocean",
        "🐳": "whale ocean",
        "🦈": "shark ocean jaws",
        "🌲": "tree pine forest nature",
        "🌳": "tree forest nature",
        "🌴": "palm tree beach tropical vacation",
        "🌱": "seedling sprout grow plant",
        "🌿": "herb leaf plant",
        "🍀": "clover lucky four leaf",
        "🍁": "maple leaf autumn fall canada",
        "💐": "bouquet flowers gift",
        "🌷": "tulip flower",
        "🌹": "rose flower love red",
        "🌺": "hibiscus flower",
        "🌸": "cherry blossom flower pink spring",
        "🌼": "flower blossom",
        "🌻": "sunflower yellow flower",
        "☀️": "sun sunny hot bright morning weather",
        "☁️": "cloud weather sky",
        "🌧️": "rain weather cloud",
        "⛈️": "storm thunder lightning rain",
        "❄️": "snow winter cold ice",
        "🔥": "fire hot lit flame burn trending",
        "🌈": "rainbow colorful pride sky",

        // Food & Drink
        "🍎": "apple fruit red healthy",
        "🍏": "apple green fruit",
        "🍐": "pear fruit",
        "🍊": "orange fruit citrus",
        "🍋": "lemon yellow sour fruit",
        "🍌": "banana fruit yellow",
        "🍉": "watermelon fruit summer",
        "🍇": "grapes fruit wine",
        "🍓": "strawberry fruit berry red",
        "🫐": "blueberry fruit",
        "🍒": "cherry fruit red",
        "🍑": "peach fruit",
        "🥭": "mango fruit",
        "🍍": "pineapple fruit",
        "🥥": "coconut",
        "🥝": "kiwi fruit",
        "🍅": "tomato vegetable",
        "🥑": "avocado healthy",
        "🥦": "broccoli vegetable green",
        "🌽": "corn",
        "🥕": "carrot",
        "🥔": "potato",
        "🍞": "bread toast",
        "🥐": "croissant bread bakery",
        "🧀": "cheese",
        "🥚": "egg breakfast",
        "🍳": "egg fry breakfast cooking",
        "🥞": "pancake breakfast",
        "🥓": "bacon meat breakfast",
        "🍔": "burger hamburger fast food lunch",
        "🍟": "fries french fries fast food",
        "🍕": "pizza slice food party",
        "🌭": "hotdog food",
        "🥪": "sandwich lunch",
        "🌮": "taco mexican food",
        "🌯": "burrito mexican food",
        "🥗": "salad healthy food",
        "🍝": "pasta spaghetti dinner",
        "🍜": "noodles ramen soup hot",
        "🍛": "curry rice food",
        "🍣": "sushi japanese food",
        "🍱": "bento box lunch",
        "🍦": "ice cream cone sweet dessert",
        "🍩": "donut doughnut sweet dessert",
        "🍪": "cookie sweet snack",
        "🎂": "cake birthday party celebrate",
        "🍰": "cake slice dessert sweet",
        "🧁": "cupcake sweet dessert",
        "🍫": "chocolate sweet candy",
        "🍬": "candy sweet",
        "🍭": "lollipop candy",
        "🍿": "popcorn movie snack",
        "☕️": "coffee tea espresso morning cup hot cafe",
        "🍵": "tea green tea cup hot",
        "🧃": "juice drink box",
        "🥤": "soda drink cup straw",
        "🧋": "boba bubble tea milk tea drink",
        "🍺": "beer drink bar party",
        "🍻": "beers cheers party drinks",
        "🥂": "champagne cheers toast celebrate",
        "🍷": "wine drink glass",

        // Objects & Activities
        "⚽️": "soccer football sport ball goal",
        "🏀": "basketball sport ball",
        "🏈": "football sport ball",
        "⚾️": "baseball sport ball",
        "🎾": "tennis sport ball",
        "🎯": "target bullseye goal aim",
        "🎮": "game gaming controller play video game",
        "🎲": "dice game luck",
        "🚗": "car drive auto vehicle",
        "🚕": "taxi cab car",
        "🚌": "bus transit",
        "🏎️": "race car fast speed f1",
        "🚓": "police car siren",
        "🚑": "ambulance emergency hospital",
        "🚒": "fire truck",
        "🚲": "bike bicycle cycle",
        "🏍️": "motorcycle bike",
        "✈️": "plane airplane flight travel airport",
        "🚀": "rocket launch space fast moon",
        "🛸": "ufo alien space",
        "🚢": "ship boat cruise",
        "📱": "phone mobile iphone cell smartphone",
        "💻": "laptop computer macbook code work",
        "⌨️": "keyboard type",
        "🖥️": "desktop computer monitor mac screen",
        "📷": "camera photo picture",
        "📹": "video camera record",
        "🎥": "movie film camera",
        "📺": "tv television watch",
        "📻": "radio",
        "🎙️": "mic microphone podcast voice",
        "⏰": "alarm clock time wake up",
        "⏱️": "stopwatch timer time",
        "⏳": "hourglass time wait",
        "💡": "idea light bulb bright smart",
        "🔦": "flashlight torch light",
        "💵": "money dollar cash bill bank",
        "💰": "money bag rich cash wealth",
        "💳": "credit card pay bank shop",
        "💎": "diamond gem ring rich",
        "🔧": "wrench tool fix repair",
        "🔨": "hammer tool build",
        "🛠️": "tools fix repair build",
        "⚙️": "gear settings config",
        "💣": "bomb boom explode",
        "🛡️": "shield protect security safe",
        "🩺": "doctor medical health",
        "💊": "pill medicine drug health",

        // Symbols & Hearts
        "❤️": "heart love red like romance",
        "🧡": "orange heart love",
        "💛": "yellow heart love gold",
        "💚": "green heart love",
        "💙": "blue heart love",
        "💜": "purple heart love",
        "🖤": "black heart dark",
        "🤍": "white heart pure",
        "🤎": "brown heart",
        "💔": "broken heart sad breakup",
        "❣️": "heart exclamation love",
        "💕": "two hearts love pink",
        "💞": "revolving hearts love",
        "💓": "beating heart love",
        "💗": "growing heart love",
        "💖": "sparkling heart love cute",
        "💘": "cupid arrow heart love",
        "💝": "gift heart ribbon love",
        "⚠️": "warning alert caution danger",
        "⛔️": "no entry stop ban",
        "🚫": "prohibited no ban forbidden",
        "✅": "check checkmark tick yes done green verified ok",
        "❌": "cross x wrong no cancel delete close",
        "⭕️": "circle ring o",
        "🛑": "stop sign red",
        "💯": "100 hundred perfect keep it real score",
        "💢": "anger mad symbol",
        "❗️": "exclamation important alert",
        "❓": "question what help",
        "‼️": "exclamation double urgent",
        "⁉️": "exclamation question",
        "♻️": "recycle green eco environment",
        "🌐": "globe world earth internet web",
        "💤": "zzz sleep tired snore",
        "🆗": "ok okay",
        "🆙": "up",
        "🆒": "cool",
        "🆕": "new",
        "0️⃣": "0 zero number",
        "1️⃣": "1 one number",
        "2️⃣": "2 two number",
        "3️⃣": "3 three number",
        "4️⃣": "4 four number",
        "5️⃣": "5 five number",
        "6️⃣": "6 six number",
        "7️⃣": "7 seven number",
        "8️⃣": "8 eight number",
        "9️⃣": "9 nine number",
        "🔟": "10 ten number",
        "▶️": "play start video arrow",
        "⏸️": "pause",
        "⏹️": "stop",
        "⏺️": "record",
        "⏩": "fast forward",
        "⏪": "rewind back",
        "➡️": "right arrow next",
        "⬅️": "left arrow back",
        "⬆️": "up arrow",
        "⬇️": "down arrow",
        "🎵": "music note song audio",
        "🎶": "music notes song audio",
        "➕": "plus add math",
        "➖": "minus subtract math",
        "✖️": "multiply math",
        "➗": "divide math",
        "♾️": "infinity forever endless",
        "💲": "dollar money price"
    ]

    /// Precomputed search index pairing each emoji with its automatic Unicode name,
    /// category label, and curated conversational aliases.
    private static let searchIndex: [(emoji: String, keywords: String)] = {
        var result: [(String, String)] = []
        var seen = Set<String>()
        for cat in categories {
            let catName = cat.name.lowercased()
            for emoji in cat.emojis {
                if seen.contains(emoji) { continue }
                seen.insert(emoji)

                let unicodeRaw = emoji.applyingTransform(.toUnicodeName, reverse: false) ?? ""
                let unicodeName = unicodeRaw
                    .replacingOccurrences(of: "\\N{", with: " ")
                    .replacingOccurrences(of: "}", with: " ")
                    .replacingOccurrences(of: "variation selector-16", with: "")
                    .lowercased()

                let alias = emojiAliases[emoji] ?? ""
                let combined = "\(emoji) \(unicodeName) \(catName) \(alias)"
                result.append((emoji, combined))
            }
        }
        return result
    }()

    private var activeEmojis: [String] {
        let trimmed = searchQuery.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if !trimmed.isEmpty {
            let terms = trimmed.split(whereSeparator: { $0.isWhitespace }).map(String.init)
            return Self.searchIndex
                .filter { entry in
                    terms.allSatisfy { term in entry.keywords.contains(term) }
                }
                .map(\.emoji)
        }

        // Otherwise display the selected category
        let category = Self.categories.first(where: { $0.id == selectedCategory }) ?? Self.categories[0]
        return category.emojis
    }

    private let columns = Array(repeating: GridItem(.flexible(), spacing: 4), count: 7)

    var body: some View {
        VStack(spacing: 0) {
            // 1. Category Chips Bar with Left/Right Chevrons & ScrollViewReader
            ScrollViewReader { scrollProxy in
                HStack(spacing: 3) {
                    // Left Chevron Scroll Button
                    Button(action: {
                        navigateCategory(direction: -1, proxy: scrollProxy)
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 8, weight: .bold))
                            .foregroundColor(currentIndex > 0 ? .white.opacity(0.80) : .white.opacity(0.18))
                            .frame(width: 18, height: 26)
                            .background(currentIndex > 0 ? Color.white.opacity(0.08) : Color.white.opacity(0.02))
                            .cornerRadius(4)
                    }
                    .buttonStyle(.plain)
                    .noFocusRing()
                    .disabled(currentIndex == 0)
                    .help("Scroll left to previous categories")

                    // Horizontal Scrollable Chips
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 4) {
                            ForEach(Self.categories) { cat in
                                let isCatSelected = selectedCategory == cat.id
                                Button(action: {
                                    selectedCategory = cat.id
                                    searchQuery = ""
                                    withAnimation(.easeInOut(duration: 0.15)) {
                                        scrollProxy.scrollTo(cat.id, anchor: .center)
                                    }
                                }) {
                                    HStack(spacing: 3) {
                                        Image(systemName: cat.icon)
                                            .font(.system(size: 9.5, weight: .medium))
                                            .frame(width: 11, height: 11)
                                        Text(cat.name)
                                            .font(.system(size: 10, weight: .medium))
                                            .lineLimit(1)
                                    }
                                    .foregroundColor(isCatSelected ? accentColor : .white.opacity(0.65))
                                    .padding(.horizontal, 7)
                                    .padding(.vertical, 4)
                                    .background(
                                        RoundedRectangle(cornerRadius: 5, style: .continuous)
                                            .fill(isCatSelected ? Color.white.opacity(0.14) : Color.white.opacity(0.04))
                                    )
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 5, style: .continuous)
                                            .stroke(isCatSelected ? accentColor.opacity(0.40) : Color.clear, lineWidth: 1)
                                    )
                                    .fixedSize(horizontal: true, vertical: true)
                                }
                                .buttonStyle(.plain)
                                .noFocusRing()
                                .fixedSize(horizontal: true, vertical: true)
                                .id(cat.id)
                            }
                        }
                        .padding(.horizontal, 2)
                        .padding(.vertical, 3)
                    }
                    .onHover { hovering in
                        isHoveringCategoryBar = hovering
                    }

                    // Right Chevron Scroll Button
                    Button(action: {
                        navigateCategory(direction: 1, proxy: scrollProxy)
                    }) {
                        Image(systemName: "chevron.right")
                            .font(.system(size: 8, weight: .bold))
                            .foregroundColor(currentIndex < Self.categories.count - 1 ? .white.opacity(0.80) : .white.opacity(0.18))
                            .frame(width: 18, height: 26)
                            .background(currentIndex < Self.categories.count - 1 ? Color.white.opacity(0.08) : Color.white.opacity(0.02))
                            .cornerRadius(4)
                    }
                    .buttonStyle(.plain)
                    .noFocusRing()
                    .disabled(currentIndex == Self.categories.count - 1)
                    .help("Scroll right to more categories")
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .onCategoryChange(of: selectedCategory) { newCat in
                    withAnimation(.easeInOut(duration: 0.15)) {
                        scrollProxy.scrollTo(newCat, anchor: .center)
                    }
                }
            }

            // 2. Emoji Search Bar
            HStack(spacing: 6) {
                Image(systemName: "magnifyingglass")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.white.opacity(0.40))

                TextField("Search emoji...", text: $searchQuery)
                    .textFieldStyle(.plain)
                    .font(.system(size: 11))
                    .foregroundColor(.white)

                if !searchQuery.isEmpty {
                    Button(action: { searchQuery = "" }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 11))
                            .foregroundColor(.white.opacity(0.50))
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 5)
            .background(Color.white.opacity(0.06))
            .cornerRadius(6)
            .overlay(
                RoundedRectangle(cornerRadius: 6)
                    .stroke(Color.white.opacity(0.08), lineWidth: 1)
            )
            .padding(.horizontal, 10)
            .padding(.bottom, 6)

            // 3. Grid of Emojis or Empty Search State
            if activeEmojis.isEmpty {
                VStack(spacing: 6) {
                    Spacer()
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 24, weight: .light))
                        .foregroundColor(.white.opacity(0.30))
                    Text("No matching emojis")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.white.opacity(0.60))
                    Spacer()
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                ScrollView {
                    LazyVGrid(columns: columns, spacing: 4) {
                        ForEach(activeEmojis, id: \.self) { emoji in
                            EmojiButton(
                                emoji: emoji,
                                isHovered: hoveredEmoji == emoji,
                                onHover: { hovering in
                                    hoveredEmoji = hovering ? emoji : nil
                                },
                                onSelect: {
                                    onSelectEmoji(emoji)
                                }
                            )
                        }
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                }
            }
        }
    }
}

/// Single interactive emoji button supporting both click-to-paste and drag-and-drop.
struct EmojiButton: View {
    let emoji: String
    let isHovered: Bool
    let onHover: (Bool) -> Void
    let onSelect: () -> Void

    var body: some View {
        Text(emoji)
            .font(.system(size: 20))
            .frame(width: 38, height: 38)
            .background(
                RoundedRectangle(cornerRadius: 6, style: .continuous)
                    .fill(isHovered ? Color.white.opacity(0.16) : Color.clear)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 6, style: .continuous)
                    .stroke(isHovered ? Color.white.opacity(0.20) : Color.clear, lineWidth: 1)
            )
            .overlay(
                DraggableItemOverlay(
                    item: ClipboardItem(text: emoji),
                    onTap: onSelect,
                    onHoverChange: onHover
                )
            )
    }
}

// MARK: - Compatibility Extensions

private extension View {
    @ViewBuilder
    func onIndexChange(of index: Int, perform action: @escaping (Int) -> Void) -> some View {
        if #available(macOS 14.0, *) {
            self.onChange(of: index) { _, newIndex in
                action(newIndex)
            }
        } else {
            self.onChange(of: index) { newIndex in
                action(newIndex)
            }
        }
    }

    @ViewBuilder
    func onCategoryChange(of category: String, perform action: @escaping (String) -> Void) -> some View {
        if #available(macOS 14.0, *) {
            self.onChange(of: category) { _, newCat in
                action(newCat)
            }
        } else {
            self.onChange(of: category) { newCat in
                action(newCat)
            }
        }
    }

    @ViewBuilder
    func noFocusRing() -> some View {
        if #available(macOS 14.0, *) {
            self.focusEffectDisabled(true)
        } else {
            self
        }
    }
}
