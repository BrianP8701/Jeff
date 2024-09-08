//
//  ContentView.swift
//  Jeff
//
//  Created by Ayush Goel on 9/7/24.
//
import SwiftUI
import Network
import AppKit

struct SearchItem: Codable, Identifiable, Equatable {
    let type: String
    let source: String
    let title: String
    let distance: Float
    var id: String { source }
    
    static func == (lhs: SearchItem, rhs: SearchItem) -> Bool {
        return lhs.type == rhs.type && lhs.source == rhs.source && lhs.title == rhs.title && lhs.distance == rhs.distance
    }
}

struct SearchResponse: Codable {
    let results: [SearchItem]
    let answer_summary: String?
}

struct SearchRequest: Codable {
    let query: String
    let limit: Int
}

struct CustomTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .background(Color(NSColor.windowBackgroundColor))
            .cornerRadius(15)
            .overlay(
                RoundedRectangle(cornerRadius: 15)
                    .stroke(Color.clear, lineWidth: 0)
            )
    }
}

struct CustomTextField: NSViewRepresentable {
    @Binding var text: String
    var onCommit: () -> Void

    func makeNSView(context: Context) -> NSTextField {
        let textField = NSTextField()
        textField.isEditable = true
        textField.isBordered = false
        textField.isBezeled = false
        textField.drawsBackground = false
        textField.focusRingType = .none
        textField.font = .systemFont(ofSize: 24, weight: .regular)
        textField.textColor = .white
        textField.placeholderString = "Search with Jeff"
        textField.placeholderAttributedString = NSAttributedString(
            string: "Search with Jeff",
            attributes: [
                .foregroundColor: NSColor.placeholderTextColor,
                .font: NSFont.systemFont(ofSize: 24, weight: .regular)
            ]
        )
        textField.cell?.wraps = false
        textField.cell?.isScrollable = true
        textField.delegate = context.coordinator
        return textField
    }

    func updateNSView(_ nsView: NSTextField, context: Context) {
        nsView.stringValue = text
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, NSTextFieldDelegate {
        var parent: CustomTextField

        init(_ parent: CustomTextField) {
            self.parent = parent
        }

        func controlTextDidChange(_ obj: Notification) {
            guard let textField = obj.object as? NSTextField else { return }
            parent.text = textField.stringValue
        }

        func control(_ control: NSControl, textView: NSTextView, doCommandBy commandSelector: Selector) -> Bool {
            if commandSelector == #selector(NSResponder.insertNewline(_:)) {
                parent.onCommit()
                return true
            }
            return false
        }
    }
}

struct ContentView: View {
    @State private var searchText = ""
    @State var searchResults: [SearchItem] = []
    @State var answerSummary: String? = nil // Change this line
    @State private var isSearching = false
    @State private var isServerReachable = false
    @State private var searchTask: DispatchWorkItem?
    
    var body: some View {
        VStack(spacing: 0) {
            CustomTextField(text: $searchText, onCommit: performSearch)
                .frame(height: 60)
                .padding(.horizontal, 15)
                .onChange(of: searchText) { _ in
                    debouncedSearch()
                }
            
            if let summary = answerSummary {
                Text(summary)
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(10)
                    .padding(.horizontal)
                    .padding(.top, 10)
            }
            
            if !searchResults.isEmpty {
                List(searchResults) { item in
                    HStack {
                        Image(systemName: item.type == "FILE" ? "doc" : "link")
                            .font(.system(size: 20))
                        VStack(alignment: .leading) {
                            Text(item.title)
                                .font(.system(size: 18))
                            Text(item.source)
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                            Text(String(format: "Distance: %.2f", item.distance))
                                .font(.system(size: 12))
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 5)
                    .onTapGesture {
                        handleItemSelection(item)
                    }
                }
                .frame(height: min(CGFloat(searchResults.count) * 60, 400))
            }
        }
        .frame(width: 800)
        .background(Color(NSColor.windowBackgroundColor))
        .cornerRadius(15)
        .shadow(radius: 15)
        .edgesIgnoringSafeArea(.all)
        .onAppear {
            checkServerReachability()
        }
    }
    
    func debouncedSearch() {
        searchTask?.cancel()
        
        let task = DispatchWorkItem {
            self.performSearch()
        }
        
        searchTask = task
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3, execute: task)
    }
    
    func checkServerReachability() {
        let monitor = NWPathMonitor(requiredInterfaceType: .loopback)
        monitor.pathUpdateHandler = { path in
            DispatchQueue.main.async {
                self.isServerReachable = path.status == .satisfied
                print("Server reachable: \(self.isServerReachable)")
            }
        }
        let queue = DispatchQueue(label: "ServerReachability")
        monitor.start(queue: queue)
    }
    
    func performSearch() {
        guard !searchText.isEmpty else {
            searchResults = []
            return
        }
        
        isSearching = true
        
        guard let url = URL(string: "http://localhost:8000/search") else {
            print("Invalid URL")
            return
        }
        
        let searchRequest = SearchRequest(query: searchText, limit: 5)
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            let jsonData = try JSONEncoder().encode(searchRequest)
            request.httpBody = jsonData
        } catch {
            print("Error encoding search request: \(error)")
            return
        }
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            defer {
                isSearching = false
                print("Search completed")
            }

            if let error = error {
                print("Network Error: \(error.localizedDescription)")
                return
            }

            if let httpResponse = response as? HTTPURLResponse {
                print("HTTP Status Code: \(httpResponse.statusCode)")
                
                // Handle non-200 status codes
                guard (200...299).contains(httpResponse.statusCode) else {
                    print("Server Error: Status code \(httpResponse.statusCode)")
                    if let data = data, let errorMessage = String(data: data, encoding: .utf8) {
                        print("Error message: \(errorMessage)")
                    }
                    return
                }
            }
            
            guard let data = data else {
                print("No data received")
                return
            }
            
            print("Received data: \(String(data: data, encoding: .utf8) ?? "Unable to decode")")
            
            do {
                let decodedResponse = try JSONDecoder().decode(SearchResponse.self, from: data)
                DispatchQueue.main.async {
                    self.searchResults = decodedResponse.results
                    self.answerSummary = decodedResponse.answer_summary
                    print("Search results updated: \(self.searchResults)")
                    print("Answer summary: \(self.answerSummary ?? "None")")
                    NotificationCenter.default.post(name: NSNotification.Name("SearchResultsChanged"), object: nil)
                }
            } catch {
                print("Decoding error: \(error)")
            }
        }
        
        task.resume()
    }
    
    func handleItemSelection(_ item: SearchItem) {
        if item.type == "FILE" {
            openFile(item.source)
        } else if item.type == "URL" {
            openURL(item.source)
        }
    }
    
    func openFile(_ path: String) {
        if let url = URL(string: path) {
            NSWorkspace.shared.open(url)
        }
    }
    
    func openURL(_ urlString: String) {
        if let url = URL(string: urlString) {
            NSWorkspace.shared.open(url)
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
