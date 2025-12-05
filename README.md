# Subset C Parser (mini-compiler project)

Structure:
- ast.py          : token and AST node definitions
- lexer.py        : lexer that tokenizes a subset of C
- parser.py       : recursive-descent parser producing an AST (Program)
- visualizer.py   : draws AST to PNG using matplotlib
- main.py         : CLI runner (process single .c or run examples/)
- examples/       : 10 C example files (5 valid, 5 invalid)

Usage:
```bash
python3 main.py             # runs all examples in examples/
python3 main.py examples/valid1.c   # processes a single C file
```

Notes:
- This implements a realistic subset of C (functions, var decls, if/while/for, expressions).
- Does NOT implement pointers, structs, preprocessing, or full C type system.
- AST images saved to ./trees/
