from .lexer import Lexer, LexError

class ParseError(Exception): pass

class Parser:
    def __init__(self, source): self.t=Lexer(source).tokenize(); self.i=0
    def cur(self): return self.t[self.i]
    def peek(self,n=1): return self.t[min(self.i+n,len(self.t)-1)]
    def take(self): x=self.cur(); self.i+=1; return x
    def isv(self,v): return self.cur().value==v
    def match(self,*vs):
        if self.cur().value in vs: return self.take()
        return None
    def expect(self,v):
        if not self.isv(v): raise ParseError(f'{self.cur().line}:{self.cur().col}: انتظار {v!r} بود، {self.cur().value!r} دریافت شد')
        return self.take()
    def name(self):
        if self.cur().kind not in ('IDENT','KW') or self.cur().value in ('begin','end','if','else','while','for','in','return','class','function','let','const','show','new'):
            raise ParseError(f'{self.cur().line}:{self.cur().col}: نام معتبر انتظار می‌رفت')
        return self.take().value
    def parse(self):
        if self.match('forge'):
            self.expect('program')
            if self.cur().kind=='STRING': self.take()
        self.expect('begin'); body=self.block_until('end'); self.expect('end')
        if self.cur().kind!='EOF': raise ParseError(f'{self.cur().line}:{self.cur().col}: متن اضافی بعد از end')
        return ('block',body)
    def block_until(self,*ends):
        body=[]
        while self.cur().kind!='EOF' and self.cur().value not in ends:
            if self.match(';',','): continue
            body.append(self.stmt())
            self.match(';')
        return body
    def body(self):
        self.expect('begin'); b=self.block_until('end'); self.expect('end'); return ('block',b)
    def stmt(self):
        tok=self.cur(); v=tok.value
        if v in ('let','const'):
            const=self.take().value=='const'; name=self.name(); typ=None
            if self.match(':'): typ=self.name()
            value=None
            if self.match('='): value=self.expr()
            if value is None and not const: value=('literal',None)
            if value is None: raise ParseError(f'{tok.line}:{tok.col}: const باید مقدار اولیه داشته باشد')
            return ('decl',name,typ,value,const)
        if self.match('show'): return ('show',self.expr())
        if self.match('if'):
            cond=self.expr(); yes=self.body(); no=('block',[])
            if self.match('else'):
                if self.isv('if'): no=('block',[self.stmt()])
                else: no=self.body()
            return ('if',cond,yes,no)
        if self.match('while'): return ('while',self.expr(),self.body())
        if self.match('for'):
            var=self.name(); self.expect('in'); start=self.expr(); self.expect('..'); stop=self.expr(); step=('literal',1)
            if self.match('by'): step=self.expr()
            return ('for',var,start,stop,step,self.body())
        if self.match('function'):
            name=self.name(); params=self.params(); ret=None
            if self.match('->'): ret=self.name()
            return ('function',name,params,ret,self.body())
        if self.match('class'):
            name=self.name(); self.expect('begin'); members=[]
            while not self.isv('end') and self.cur().kind!='EOF':
                if self.match(';'): continue
                members.append(self.stmt())
            self.expect('end'); return ('class',name,members)
        if self.match('return'):
            if self.isv('end') or self.isv(';'): return ('return',('literal',None))
            return ('return',self.expr())
        if self.match('break'): return ('break',)
        if self.match('continue'): return ('continue',)
        if self.isv('begin'): return self.body()
        e=self.expr()
        if self.cur().value in ('=','+=','-=','*=','/='):
            op=self.take().value; return ('assign',e,op,self.expr())
        return ('exprstmt',e)
    def params(self):
        self.expect('('); p=[]
        if not self.isv(')'):
            while True:
                n=self.name(); typ=None
                if self.match(':'): typ=self.name()
                p.append((n,typ))
                if not self.match(','): break
        self.expect(')'); return p
    PRE={'or':1,'and':2,'==':3,'!=':3,'<':3,'>':3,'<=':3,'>=':3,'in':3,'+':4,'-':4,'*':5,'/':5,'%':5}
    def expr(self,minp=0):
        t=self.take(); v=t.value
        if t.kind in ('NUMBER','STRING'): left=('literal',v)
        elif v in ('true','false','null'): left=('literal',{'true':True,'false':False,'null':None}[v])
        elif v in ('-','+','!','not'):
            left=('unary',v,self.expr(6))
        elif v=='(':
            left=self.expr(); self.expect(')')
        elif v=='[':
            vals=[]
            if not self.isv(']'):
                while True:
                    vals.append(self.expr())
                    if not self.match(','): break
            self.expect(']'); left=('list',vals)
        elif v=='new': left=('new',self.name(),self.call_args())
        elif t.kind in ('IDENT','KW') and v not in ('end','else','begin'):
            left=('var',v)
        else: raise ParseError(f'{t.line}:{t.col}: عبارت نامعتبر {v!r}')
        while True:
            if self.isv('('): left=('call',left,self.call_args()); continue
            if self.match('.'):
                left=('member',left,self.name()); continue
            if self.match('['):
                idx=self.expr(); self.expect(']'); left=('index',left,idx); continue
            op=self.cur().value
            if op=='..' or op not in self.PRE or self.PRE[op]<minp: break
            prec=self.PRE[op]; self.take(); right=self.expr(prec+1); left=('binary',op,left,right)
        return left
    def call_args(self):
        self.expect('('); args=[]
        if not self.isv(')'):
            while True:
                args.append(self.expr())
                if not self.match(','): break
        self.expect(')'); return args

def parse(source):
    try: return Parser(source).parse()
    except LexError: raise
