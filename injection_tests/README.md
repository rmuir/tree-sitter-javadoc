# Injection tests

Parsing tests for [tree-sitter-javadoc](https://github.com/rmuir/tree-sitter-javadoc).
It works similar to [tree-sitter/parse-action](https://github.com/tree-sitter/parse-action), but for an injected language.

## Background

Treesitter has wonderful testing tools, but most do not work for injected languages.
The core [unit testing facility](https://tree-sitter.github.io/tree-sitter/creating-parsers/5-writing-tests.html) [works fine](../test/corpus).

The [syntax highlighting](https://tree-sitter.github.io/tree-sitter/3-syntax-highlighting.html#unit-testing) can't easily work, it is geared at using comments, and javadocs are themselves comments.

The [parsing](https://tree-sitter.github.io/tree-sitter/cli/parse.html) functionality typically used on large corpora can't easily work, as it does not support injected languages.

This module solves the parsing problem, so that large corpora can be tested in CI to prevent regressions.

## Adding new repos

Example addition of a new repo (Apache Lucene):

1. Create `data/.lucene.repo` containing parameters for cloning:

```
# List of parameters passed to git-clone(1)
# Specify a tag to keep CI stable
https://github.com/apache/lucene.git --branch releases/lucene/10.2.2
```

2. Create `data/.lucene.patterns` containing patterns to match files:

```
# List of file match patterns passed to git-ls-files(1)
# Include all java sources
*.java
# Ignore tests which are typically VERY messy
:!**test/**
```

## Challenges

* Most javadocs in the wild contain numerous syntax errors
* Javadocs are bonded at the hip with HTML, inviting many crazy problems
* Tools such as doclint as very new, and most developers disable them
* Java language is changing, new features are being introduced
* Difficult to make parsing more lenient without introducing ambiguity

## Features

* Parallel execution (cloning, testing, diffing): `make -Otarget -j test`, `make -Otarget -j dump`
* Parallel parsing with subprocesses to bypass GIL
* Repos pinned to repository tags
* Ability to ignore certain patterns such as tests
* No git submodules (can mess up cargo checkouts)
* Produces diff of parse trees across corpora on pull requests
