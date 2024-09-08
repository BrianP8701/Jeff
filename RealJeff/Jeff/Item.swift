//
//  Item.swift
//  Jeff
//
//  Created by Brian Przezdziecki on 9/7/24.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
