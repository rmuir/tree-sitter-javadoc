package tree_sitter_javadoc_test

import (
	"testing"

	tree_sitter "github.com/tree-sitter/go-tree-sitter"
	tree_sitter_javadoc "github.com/rmuir/tree-sitter-javadoc/bindings/go"
)

func TestCanLoadGrammar(t *testing.T) {
	language := tree_sitter.NewLanguage(tree_sitter_javadoc.Language())
	if language == nil {
		t.Errorf("Error loading Javadoc grammar")
	}
}
