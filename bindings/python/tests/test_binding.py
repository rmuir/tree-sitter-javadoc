from unittest import TestCase

import tree_sitter_javadoc

from tree_sitter import Language, Parser


def language():
    return Language(tree_sitter_javadoc.language())


class TestLanguage(TestCase):
    def test_can_load_grammar(self):
        _ = language()

    def test_can_create_parser(self):
        _ = Parser(language())

    def test_can_parse_docs(self):
        parser = Parser(language())
        doc = "/** test */".encode()
        tree = parser.parse(doc)
        assert not tree.root_node.has_error
