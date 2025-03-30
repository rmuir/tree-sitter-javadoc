// swift-tools-version:5.3

import Foundation
import PackageDescription

var sources = ["src/parser.c"]
if FileManager.default.fileExists(atPath: "src/scanner.c") {
    sources.append("src/scanner.c")
}

let package = Package(
    name: "TreeSitterJavadoc",
    products: [
        .library(name: "TreeSitterJavadoc", targets: ["TreeSitterJavadoc"]),
    ],
    dependencies: [
        .package(url: "https://github.com/ChimeHQ/SwiftTreeSitter", from: "0.8.0"),
    ],
    targets: [
        .target(
            name: "TreeSitterJavadoc",
            dependencies: [],
            path: ".",
            sources: sources,
            resources: [
                .copy("queries")
            ],
            publicHeadersPath: "bindings/swift",
            cSettings: [.headerSearchPath("src")]
        ),
        .testTarget(
            name: "TreeSitterJavadocTests",
            dependencies: [
                "SwiftTreeSitter",
                "TreeSitterJavadoc",
            ],
            path: "bindings/swift/TreeSitterJavadocTests"
        )
    ],
    cLanguageStandard: .c11
)
