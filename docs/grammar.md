# Nova v0.2 grammar (simplified)

```ebnf
program    = ["forge" "program" [STRING]] "begin" { statement } "end" ;
statement  = declaration | assignment | show | if | while | for | function | class | return | break | continue | expression ;
declaration= ("let" | "const") IDENT [":" TYPE] ["=" expression] ;
show       = "show" expression ;
if         = "if" expression block ["else" (block | if)] ;
while      = "while" expression block ;
for        = "for" IDENT "in" expression ".." expression ["by" expression] block ;
function   = "function" IDENT "(" [parameters] ")" ["->" TYPE] block ;
class      = "class" IDENT "begin" { function | declaration } "end" ;
block      = "begin" { statement } "end" ;
expression = literal | IDENT | list | call | member | index | unary | binary | "new" IDENT call ;
```

Statements can be separated by newlines or semicolons. The parser uses conventional precedence: `or`, `and`, comparisons, addition/subtraction, multiplication/division/modulo.
