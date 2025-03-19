#!/home/rmuir/workspace/tree-sitter-javadoc/injection_tests/.venv/bin/python
"""
Ugly parser that parses files with java, looks for their javadoc injections,
parses those, and then looks for errors.
Works best on a real java repo like this:
git ls-files | grep ".java$" | xargs ~/workspace/tree-sitter-javadoc/injection_tests/tester.py
"""

import sys

import tree_sitter_java as tsjava
import tree_sitter_javadoc as tsjavadoc
from tree_sitter import Language, Parser

JAVA_LANGUAGE = Language(tsjava.language())
JAVADOC_LANGUAGE = Language(tsjavadoc.language())

java_parser = Parser(JAVA_LANGUAGE)
javadoc_parser = Parser(JAVADOC_LANGUAGE)

INJECTION_QUERY = JAVA_LANGUAGE.query(
    """
((block_comment) @injection.content
  (#match? @injection.content "^/[*][*][^*]"))
"""
)

ERROR_QUERY = JAVADOC_LANGUAGE.query(
    """
(ERROR) @errors
"""
)


# parses a java file, looks for javadocs injections, parses those, reports any errors
def main(file: str):
    with open(file, "rb") as fd:
        contents = fd.read()
        tree = java_parser.parse(contents)
        captures = INJECTION_QUERY.captures(tree.root_node)
        if captures.get("injection.content") is None:
            return
        nodelist = captures["injection.content"]
        for node in nodelist:
            injection_range = slice(node.start_byte, node.end_byte)
            injection = contents[injection_range]
            subtree = javadoc_parser.parse(injection)
            matches = ERROR_QUERY.matches(subtree.root_node)
            if len(matches) > 0:
                raise RuntimeError(f"error parsing {file}")


if __name__ == "__main__":
    errorfiles = []
    for file in sys.argv[1:]:
        try:
            main(file)
        except Exception:
            errorfiles.append(file)
    if len(errorfiles) > 0:
        for file in errorfiles:
            print(file)
        sys.exit(1)
