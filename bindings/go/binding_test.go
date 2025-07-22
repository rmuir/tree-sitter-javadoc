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

	parser := tree_sitter.NewParser()
	if parser == nil {
		t.Errorf("Error creating Javadoc parser")
	}

	version_mismatch := parser.SetLanguage(language)
	if version_mismatch != nil {
		t.Errorf("Version mismatch creating Javadoc parser: %s", version_mismatch.Error())
	}

	tree := parser.Parse([]byte("/** example **/"), nil)
	if tree.RootNode().HasError() {
		t.Errorf("Error parsing Javadoc sample: %s", tree.RootNode().ToSexp())
	}
}
