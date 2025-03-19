import XCTest
import SwiftTreeSitter
import TreeSitterJavadoc

final class TreeSitterJavadocTests: XCTestCase {
    func testCanLoadGrammar() throws {
        let parser = Parser()
        let language = Language(language: tree_sitter_javadoc())
        XCTAssertNoThrow(try parser.setLanguage(language),
                         "Error loading Javadoc grammar")
    }
}
