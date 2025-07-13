#!/usr/bin/env python3
"""Parses javadocs in java files from a git repository."""

import argparse
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import tree_sitter_java as tsjava
import tree_sitter_javadoc as tsjavadoc
from tree_sitter import Language, Node, Parser, Query, QueryCursor

java = Language(tsjava.language())
javadoc = Language(tsjavadoc.language())
java_parser = Parser(java)
javadoc_parser = Parser(javadoc)
injection_query = Query(
    java,
    """
((block_comment) @injection.content
  (#match? @injection.content "^/[*][*][^*]"))
""",
)
error_query = Query(
    javadoc,
    """
[(ERROR)(MISSING)] @error
""",
)


def format_node(node: Node) -> str:
    """Human readable node name."""
    if node.is_named:
        return node.type.replace("_", " ").replace(" declaration", "")
    return f"'{node.type}'"


def format_context(java_node: Node) -> str:
    """Concise formatting of java node being documented."""
    node_type = format_node(java_node)

    # for e.g. fields and constants, look at child declarator node
    if decl := java_node.child_by_field_name("declarator"):
        java_node = decl

    # type 'name' if it has a name
    if (name := java_node.child_by_field_name("name")) and (text := name.text):
        return f"{node_type} '{text.decode()}'"

    # otherwise just the type: typically https://errorprone.info/bugpattern/NotJavadoc
    return node_type


def format_error(node: Node) -> str:
    """Concise formatting of matched error node."""
    if node.is_missing:
        return f"missing {format_node(node)}"
    return "syntax error"


def format_errors(file: str, contents: bytes, java_node: Node, root: Node) -> list[str]:
    """Create error message from a specific javadoc injection."""
    context = format_context(java_node)
    errors: list[str] = []

    cursor = QueryCursor(error_query)
    captures = cursor.captures(root)
    nodelist = captures.get("error")
    assert nodelist
    for node in nodelist:
        location = f"{file}:{node.start_point.row + 1}:{node.start_point.column + 1}"
        text = contents.splitlines()[node.start_point.row].decode().expandtabs(tabsize=1)
        length = 1 + (
            node.end_point.column - node.start_point.column
            if node.end_point.row == node.start_point.row
            else len(text) - node.start_point.column
        )
        caret = (" " * node.start_point.column) + ("^" * length)
        errors.append(f"{location}\n{format_error(node)} in javadoc for {context}:\n | {text}\n | {caret}\n\n")
    return errors


def check_syntax(file: str) -> list[str]:
    """Parse java file, look for javadoc injections, parse those, report errors."""
    errors: list[str] = []
    with Path.open(Path(file), "rb", buffering=0) as fd:
        contents = fd.read()
        java_parser.reset()
        tree = java_parser.parse(contents)
        cursor = QueryCursor(injection_query)
        captures = cursor.captures(tree.root_node)
        if nodelist := captures.get("injection.content"):
            for node in nodelist:
                javadoc_parser.reset()
                subtree = javadoc_parser.parse(contents[node.start_byte : node.end_byte])
                if subtree.root_node.has_error:
                    java_node = node.next_sibling or node
                    offset_node = subtree.root_node_with_offset(node.start_byte, node.start_point)
                    assert offset_node
                    errors += format_errors(file, contents, java_node, offset_node)
    return errors


def main() -> None:
    """CLI entrypoint."""
    start_time = time.monotonic()
    problems = 0
    count = 0

    executor = ProcessPoolExecutor()

    parser = argparse.ArgumentParser(prog="injection_tester", description="tests javadoc injections")
    _ = parser.add_argument("root", help="filesystem path to a git repository")
    _ = parser.add_argument("file", nargs="*", default=["*.java"], help="git patterns of files")
    args = parser.parse_args()

    root: str = args.root
    files: list[str] = args.file

    print(f"Scanning {files} in {root}...")
    input_files = subprocess.Popen(["git", "ls-files", "--", *files], stdout=subprocess.PIPE, cwd=root)

    assert input_files.stdout

    lines = (str(Path(root) / line.strip().decode()) for line in input_files.stdout)
    for results in executor.map(check_syntax, lines, chunksize=32):
        count += 1
        problems += len(results)
        for problem in results:
            print(problem)
    print(f"Found {problems} problems in {count} files. ({time.monotonic() - start_time:.2f}s)")
    if problems or count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
