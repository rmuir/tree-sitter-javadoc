import SwiftTreeSitter
import TreeSitterJavadoc
import XCTest

final class TreeSitterJavadocTests: XCTestCase {
    func testCanLoadGrammar() throws {
        let parser = Parser()
        let language = Language(language: tree_sitter_javadoc())
        XCTAssertNoThrow(
            try parser.setLanguage(language),
            "Error loading Javadoc grammar")
        if let tree = parser.parse("/** example **/"), let root = tree.rootNode {
            XCTAssertFalse(root.hasError, root.sExpressionString!)
        } else {
            XCTFail("Error parsing Javadoc document")
        }
    }
}
