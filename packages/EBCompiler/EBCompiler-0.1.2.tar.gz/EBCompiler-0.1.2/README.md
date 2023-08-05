EBCompiler
==========

Existential Boolean Compiler
----------------------------

Compiles simple statements of existence and boolean truth into valid SQL (i.e. for check constraints).

Example
-------

**Input:**

    (!is_dled && file_size!?) || (is_dled && file_size?)

**Output:**

    (is_dled IS FALSE AND file_size IS NULL) OR (is_dled IS TRUE AND file_size IS NOT NULL)

Syntax
------

A name (i.e. variable or column name) can have a variety of unary operators applied to it. A name can only start with a letter but can otherwise contain letters, numbers and underscores.

- no operator is interpreted `IS TRUE`
- `!` becomes `IS FALSE`
- `?` becomes `IS NOT NULL`
- `!?` becomes `IS NULL`

Other than that, you may use logical binary operators (`&&`, `||`) and parenthesis (`(`, `)`).

If your input doesn't follow these rules, there is no guarantee valid SQL will be generated.

Why?
----

Because I wanted to play around with writing a simple lexer. Also, it allows for writing SQL check constraints more easily.

**Q:** Wait, that's really not that sophisticed is it?  
**A:** Nope. Pretty trivial.

