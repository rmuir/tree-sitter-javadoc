#!/usr/bin/env python3
"""Parses javadocs in java files from a git repository."""

import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

import tree_sitter_java as tsjava
import tree_sitter_javadoc as tsjavadoc
from tree_sitter import Language, Node, Parser, Query, QueryCursor

if TYPE_CHECKING:
    from collections.abc import Callable

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


def print_syntax(file: str) -> list[str]:
    """Parse java file, look for javadoc injections, parse those, print trees."""
    with Path.open(Path(file), "rb", buffering=0) as fd:
        contents = fd.read()
        java_parser.reset()
        tree = java_parser.parse(contents)
        cursor = QueryCursor(injection_query)
        captures = cursor.captures(tree.root_node)
        if nodelist := captures.get("injection.content"):
            # sort captures for reproducibility/diff
            nodelist.sort(key=lambda node: (node.start_byte, node.end_byte))
            for node in nodelist:
                javadoc_parser.reset()
                subtree = javadoc_parser.parse(contents[node.start_byte : node.end_byte])
                root = subtree.root_node_with_offset(node.start_byte, node.start_point)
                assert root
                print(f"{file}:{root.start_point.row + 1}:{root.start_point.column + 1}\n{root}\n")
    return []


def main() -> None:
    """CLI entrypoint."""
    start_time = time.monotonic()
    problems = 0
    count = 0

    parser = argparse.ArgumentParser(prog="injection_tester", description="tests javadoc injections")
    parser.set_defaults(func=check_syntax)
    _ = parser.add_argument("--cores", type=int, default=os.cpu_count(), help="number of CPU cores to use")
    _ = parser.add_argument(
        "--print", dest="func", action="store_const", const=print_syntax, help="print syntax trees only"
    )
    _ = parser.add_argument("root", help="filesystem path to a git repository")
    _ = parser.add_argument("file", nargs="*", default=["*.java"], help="git patterns of files")
    args = parser.parse_args()

    root: str = args.root
    func: Callable[[str], list[str]] = args.func
    files: list[str] = args.file
    cores: int = args.cores

    print(f"Scanning {files} in {root}...", file=sys.stderr)
    input_files = subprocess.Popen(["git", "ls-files", "--", *files], stdout=subprocess.PIPE, cwd=root)

    assert input_files.stdout

    lines = (str(Path(root) / line.strip().decode()) for line in input_files.stdout)
    with ProcessPoolExecutor(max_workers=cores) as executor:
        for results in executor.map(func, lines, chunksize=32):
            count += 1
            problems += len(results)
            for problem in results:
                print(problem)
    print(f"Found {problems} problems in {count} files. ({time.monotonic() - start_time:.2f}s)", file=sys.stderr)
    if problems or count == 0:
        sys.exit(1)
