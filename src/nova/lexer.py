from dataclasses import dataclass

@dataclass
class Token:
    kind: str
    value: object
    line: int
    col: int

KEYWORDS = {
    'forge','program','begin','end','let','const','show','if','else','while','for','in',
    'function','return','class','new','true','false','null','and','or','not','break','continue',
    'Int','Float','Bool','Text','List','self'
}

class LexError(Exception): pass

class Lexer:
    def __init__(self, source): self.source=source; self.i=0; self.line=1; self.col=1
    def peek(self, n=0):
        j=self.i+n
        return self.source[j] if j < len(self.source) else '\0'
    def advance(self):
        c=self.peek(); self.i+=1
        if c=='\n': self.line+=1; self.col=1
        else: self.col+=1
        return c
    def tokenize(self):
        out=[]
        while self.peek()!='\0':
            c=self.peek()
            if c.isspace(): self.advance(); continue
            if c=='#' or (c=='/' and self.peek(1)=='/'):
                while self.peek() not in ('\n','\0'): self.advance()
                continue
            line,col=self.line,self.col
            if c.isalpha() or c=='_':
                s=''
                while self.peek().isalnum() or self.peek()=='_': s+=self.advance()
                out.append(Token('KW' if s in KEYWORDS else 'IDENT',s,line,col)); continue
            if c.isdigit():
                s=''
                while self.peek().isdigit(): s+=self.advance()
                if self.peek()=='.' and self.peek(1).isdigit():
                    s+=self.advance()
                    while self.peek().isdigit(): s+=self.advance()
                    out.append(Token('NUMBER',float(s),line,col))
                else: out.append(Token('NUMBER',int(s),line,col))
                continue
            if c in ('"', "'"):
                quote=self.advance(); s=''
                while self.peek()!=quote and self.peek()!='\0':
                    ch=self.advance()
                    if ch=='\\':
                        e=self.advance(); s += {'n':'\n','t':'\t','r':'\r','\\':'\\','"':'"',"'":"'"}.get(e,e)
                    else: s+=ch
                if self.peek()=='\0': raise LexError(f'{line}:{col}: رشته بسته نشده است')
                self.advance(); out.append(Token('STRING',s,line,col)); continue
            matched=False
            for op in ('==','!=','<=','>=','->','..','+=','-=','*=','/='):
                if self.source.startswith(op,self.i):
                    for _ in op: self.advance()
                    out.append(Token('OP',op,line,col)); matched=True; break
            if matched: continue
            if c in '+-*/%=<>!': self.advance(); out.append(Token('OP',c,line,col)); continue
            if c in '(){}[],:;.': self.advance(); out.append(Token('PUNC',c,line,col)); continue
            raise LexError(f'{line}:{col}: نویسهٔ ناشناخته {c!r}')
        out.append(Token('EOF','',self.line,self.col)); return out
