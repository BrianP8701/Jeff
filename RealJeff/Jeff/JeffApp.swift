import SwiftUI
import HotKey

@main
struct JeffApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        Settings {
            EmptyView()
        }
    }
}

// Remove the SpotlightApp struct as it's not needed

class AppDelegate: NSObject, NSApplicationDelegate {
    var hotKey: HotKey?
    var searchWindow: NSPanel?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        setupHotKey()
        setupSearchWindow()
    }
    
    func setupHotKey() {
        hotKey = HotKey(key: .j, modifiers: [.command])
        hotKey?.keyDownHandler = { [weak self] in
            self?.toggleSearchWindow()
        }
    }
    
    func setupSearchWindow() {
        let contentView = ContentView()
        searchWindow = NSPanel(
            contentRect: NSRect(x: 0, y: 0, width: 800, height: 120),
            styleMask: [.borderless, .nonactivatingPanel, .titled, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        searchWindow?.center()
        searchWindow?.setFrameAutosaveName("Search Window")
        searchWindow?.contentView = NSHostingView(rootView: contentView)
        searchWindow?.level = .floating
        searchWindow?.backgroundColor = .clear
        searchWindow?.isOpaque = false
        searchWindow?.hasShadow = true
        searchWindow?.isMovableByWindowBackground = true
        searchWindow?.titlebarAppearsTransparent = true
        searchWindow?.titleVisibility = .hidden
        
        // Observe changes in the ContentView's searchResults
        NotificationCenter.default.addObserver(self, selector: #selector(adjustWindowSize), name: NSNotification.Name("SearchResultsChanged"), object: nil)
        
        if let searchWindow = searchWindow {
            NSApp.activate(ignoringOtherApps: true)
            searchWindow.makeKeyAndOrderFront(nil)
        }
    }
    
    @objc func adjustWindowSize() {
        guard let window = searchWindow,
              let contentView = window.contentView as? NSHostingView<ContentView> else {
            return
        }
        
        let hasResults = !contentView.rootView.searchResults.isEmpty
        let hasAnswerSummary = contentView.rootView.answerSummary != nil
        
        var newHeight: CGFloat = 60 // Base height for search bar
        if hasAnswerSummary {
            newHeight += 100 // Estimated height for answer summary
        }
        if hasResults {
            newHeight += min(CGFloat(contentView.rootView.searchResults.count) * 60, 400)
        }
        
        window.setFrame(NSRect(x: window.frame.origin.x,
                               y: window.frame.origin.y + (window.frame.height - newHeight),
                               width: 800,
                               height: newHeight),
                        display: true,
                        animate: true)
    }
    
    func toggleSearchWindow() {
        if let window = searchWindow {
            if window.isVisible {
                window.orderOut(nil)
                NSApp.hide(nil)
            } else {
                NSApp.activate(ignoringOtherApps: true)
                window.makeKeyAndOrderFront(nil)
            }
        }
    }
}
