# tree-sitter-javadoc

Javadoc grammar for [tree-sitter](https://github.com/tree-sitter/tree-sitter)

## About

Features:

* Complete old-school HTML (`/**`)
* Basic new-school Markdown (`///`) support
* Highlight queries, especially for those important/pesky `@see` and `@link` references
* `@nospell` set for javadocs syntax regions, so you don't have to turn spellcheck off anymore
* Injection queries for `@snippet`, `@value`
* Support for custom inline and block doclet tags
* Tested on heaps of java code, [popular open source codebases](https://github.com/rmuir/tree-sitter-javadoc/tree/main/injection_tests)
* Not perfect, but javadocs parsing is a dirty business

## Neovim Installation (for use in your editor)

Install [nvim-treesitter](https://github.com/nvim-treesitter/nvim-treesitter), then from neovim:

```text
:TSInstall java javadoc html css printf comment
```

It is recommended to install at least these parsers for treesitter support of java code.

## Bindings Installation (for development)

Bindings are published to `pypi`, `npm`, and `crates.io` as `tree-sitter-javadoc`.
Wasm and source code artifacts are published to [GitHub releases](https://github.com/rmuir/tree-sitter-javadoc/releases)

## Customize

You can customize highlighting by creating custom [query](https://neovim.io/doc/user/treesitter.html#_treesitter-queries) files in `~/.config/nvim/queries/`:

### Example customization: conventions-based highlighting

This `;; extends` the default queries, and adds additional queries based on standard coding conventions.
Many treesitter parsers do this, including java, but neovim is trying to move away from it.
If you use an LSP with semantic token support, you don't need this. Otherwise, it might be useful to you.

`~/.config/nvim/queries/javadoc/highlights.scm`:

```tsq
;; extends

; Capitalized methods in javadoc references are treated as constructors.
(((method
    (identifier) @constructor)
    (#lua-match? @constructor "^[A-Z]")))

; Screaming-case members are treated as constants.
((member
  (identifier) @constant)
  (#lua-match? @constant "^[A-Z_][A-Z0-9_]+$"))

; Camel-case members are treated as types.
((member
  (identifier) @type)
  (#lua-match? @type "^[A-Z].*[a-z]"))
```

### Example customization: disable HTML and markdown highlighting

The default highlighting incorporates highlighting of HTML and markdown tags via their respective parsers.
For a more minimal approach with just highlighting of block and inline tags, you can override the injections.

`~/.config/nvim/queries/javadoc/injections.scm`:

```tsq
; overriding with an empty query file to disable injections
```

## Screenshot of highlights

![Syntax highlighting screenshot](https://github.com/user-attachments/assets/0c08c36b-6bd3-4ef8-8ab7-ea434b2c5342)
