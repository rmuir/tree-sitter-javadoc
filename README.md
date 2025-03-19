# tree-sitter-javadoc

Javadoc grammar for [tree-sitter](https://github.com/tree-sitter/tree-sitter)

## About

Features:
* Complete old-school HTML (`/**`)
* Basic new-school Markdown (`///`) support
* Highlight queries, especially for those important/pesky `@see` and `@link` references
* `@nospell` set for javadocs syntax regions, so you don't have to turn spellcheck off anymore
* Injection queries for `@snippet`, `@value`
* Tested on heaps of java code, popular open source codebases
* Not perfect, but javadocs parsing is a dirty business

Screenshot of highlighting:
![Syntax highlighting screenshot](https://github.com/user-attachments/assets/0c08c36b-6bd3-4ef8-8ab7-ea434b2c5342)
