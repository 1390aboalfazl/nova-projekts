# Nova grammar (EBNF-like)

```text
program        = "forge", "program", STRING, NEWLINE,
                 "begin", NEWLINE, { statement, NEWLINE },
                 "end", [ NEWLINE ] ;
statement      = declaration | show_statement ;
declaration    = "let", IDENT, ":", TYPE, "=", expression ;
show_statement = "show", expression ;
expression     = term, { ("+" | "-"), term } ;
term           = unary, { ("*" | "/"), unary } ;
unary          = [ "-" ], primary ;
primary        = INT | FLOAT | STRING | "true" | "false" | IDENT
               | "(", expression, ")" ;
TYPE           = "Int" | "Float" | "Bool" | "Text" ;
```
