//
//  ContentView.swift
//  Jeff
//
//  Created by Ayush Goel on 9/7/24.
//

import SwiftUI
import Network

struct SearchItem: Codable, Identifiable, Equatable {
    let type: String
    let value: String
    let distance: Float
    var id: String { value }
    
    static func == (lhs: SearchItem, rhs: SearchItem) -> Bool {
        return lhs.type == rhs.type && lhs.value == rhs.value && lhs.distance == rhs.distance
    }
}

typealias SearchResponse = [SearchItem]

struct SearchRequest: Codable {
    let query: String
    let limit: Int
}

struct ContentView: View {
    @State private var searchText = ""
    @State var searchResults: [SearchItem] = []
    @State private var isSearching = false
    @State private var isServerReachable = false
    
    var body: some View {
        VStack(spacing: 0) {
            TextField("Search...", text: $searchText, onCommit: performSearch)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(5)
                .onChange(of: searchText) { _ in
                    performSearch()
                }
            
            if !searchResults.isEmpty {
                List(searchResults) { item in
                    HStack {
                        Image(systemName: item.type == "FILE" ? "doc" : "link")
                        Text(item.value)
                    }
                    .onTapGesture {
                        handleItemSelection(item)
                    }
                }
                .frame(height: min(CGFloat(searchResults.count) * 44, 220))
            }
        }
        .frame(width: 600)
        .background(Color(NSColor.windowBackgroundColor))
        .cornerRadius(10)
        .shadow(radius: 10)
        .edgesIgnoringSafeArea(.all)
        .onAppear {
            checkServerReachability()
        }
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
                    self.searchResults = decodedResponse
                    print("Search results updated: \(self.searchResults)")
                }
            } catch {
                print("Decoding error: \(error)")
            }
        }
        
        task.resume()
    }
    
    func handleItemSelection(_ item: SearchItem) {
        if item.type == "FILE" {
            openFile(item.value)
        } else if item.type == "URL" {
            openURL(item.value)
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
