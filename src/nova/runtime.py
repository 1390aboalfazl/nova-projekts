from dataclasses import dataclass
import math

class NovaRuntimeError(Exception): pass
class ReturnSignal(Exception):
    def __init__(self,value): self.value=value
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass

class Env:
    def __init__(self,parent=None): self.parent=parent; self.values={}; self.types={}; self.constants=set()
    def define(self,n,v,typ=None,const=False):
        if n in self.values: raise NovaRuntimeError(f'متغیر {n!r} قبلاً تعریف شده است')
        check_type(n,v,typ); self.values[n]=v; self.types[n]=typ
        if const: self.constants.add(n)
    def get(self,n):
        if n in self.values: return self.values[n]
        if self.parent: return self.parent.get(n)
        raise NovaRuntimeError(f'متغیر یا تابع {n!r} تعریف نشده است')
    def owner(self,n):
        if n in self.values: return self
        if self.parent: return self.parent.owner(n)
        raise NovaRuntimeError(f'متغیر {n!r} تعریف نشده است')
    def set(self,n,v):
        e=self.owner(n)
        if n in e.constants: raise NovaRuntimeError(f'نمی‌توان مقدار ثابت {n!r} را تغییر داد')
        check_type(n,v,e.types.get(n)); e.values[n]=v

def check_type(name,value,typ):
    if typ is None or value is None: return
    ok={'Int':lambda x:isinstance(x,int) and not isinstance(x,bool),'Float':lambda x:isinstance(x,(int,float)) and not isinstance(x,bool),'Bool':lambda x:isinstance(x,bool),'Text':lambda x:isinstance(x,str),'List':lambda x:isinstance(x,list)}
    if typ in ok and not ok[typ](value): raise NovaRuntimeError(f'نوع مقدار {name!r} با نوع {typ} سازگار نیست')

@dataclass
class Function:
    name: str; params: list; body: tuple; closure: Env
@dataclass
class NovaClass:
    name: str; methods: dict
@dataclass
class Instance:
    klass: NovaClass; fields: dict
@dataclass
class BoundMethod:
    function: Function; instance: Instance

class Interpreter:
    def __init__(self, output=print, input_fn=input):
        self.output=output; self.input_fn=input_fn; self.global_env=Env(); self.gui_root=None; self._install_builtins()
    def _install_builtins(self):
        for n,f in {'input':self._input,'len':lambda x:len(x),'str':self._str,'int':self._int,'float':self._float,'abs':abs,'sqrt':math.sqrt,'round':round,'range':lambda a,b=None: list(range(a)) if b is None else list(range(a,b)),'append':self._append,'remove':self._remove,'clear':self._clear,'gui_window':self._gui_window,'gui_label':self._gui_label,'gui_button':self._gui_button}.items(): self.global_env.values[n]=f
    def _input(self,prompt=''): return self.input_fn(str(prompt))
    def _str(self,x): return self.display(x)
    def _int(self,x):
        try: return int(x)
        except Exception: raise NovaRuntimeError(f'تبدیل {x!r} به Int ممکن نیست')
    def _float(self,x):
        try: return float(x)
        except Exception: raise NovaRuntimeError(f'تبدیل {x!r} به Float ممکن نیست')
    def _append(self,a,x):
        if not isinstance(a,list): raise NovaRuntimeError('append آرایه می‌خواهد')
        a.append(x); return a
    def _remove(self,a,x):
        if not isinstance(a,list): raise NovaRuntimeError('remove آرایه می‌خواهد')
        a.remove(x); return a
    def _clear(self,a):
        if isinstance(a,list): a.clear(); return None
        raise NovaRuntimeError('clear آرایه می‌خواهد')
    def _gui_window(self,title='Nova',width=500,height=300):
        try:
            import tkinter as tk
            root=tk.Tk(); root.title(str(title)); root.geometry(f'{int(width)}x{int(height)}'); self.gui_root=root; return None
        except Exception as e: raise NovaRuntimeError(f'ساخت پنجره ممکن نشد: {e}')
    def _gui_label(self,text=''):
        try:
            import tkinter as tk
            root=self.gui_root
            if root is None: raise NovaRuntimeError('اول gui_window را صدا بزن')
            w=tk.Label(root,text=str(text)); w.pack(); root.update_idletasks(); return None
        except NovaRuntimeError: raise
        except Exception as e: raise NovaRuntimeError(f'ساخت label ممکن نشد: {e}')
    def _gui_button(self,text='Button'):
        try:
            import tkinter as tk
            root=self.gui_root
            if root is None: raise NovaRuntimeError('اول gui_window را صدا بزن')
            tk.Button(root,text=str(text)).pack(); root.update_idletasks(); return None
        except NovaRuntimeError: raise
        except Exception as e: raise NovaRuntimeError(f'ساخت button ممکن نشد: {e}')
    def display(self,v):
        if isinstance(v,bool): return 'true' if v else 'false'
        if v is None: return 'null'
        if isinstance(v,list): return '['+', '.join(self.display(x) for x in v)+']'
        if isinstance(v,Instance): return f'<{v.klass.name} object>'
        return str(v)
    def run(self,tree):
        try:
            self.exec_block(tree[1],self.global_env,scoped=False)
            if self.gui_root is not None: self.gui_root.mainloop()
        except ReturnSignal: raise NovaRuntimeError('return خارج از تابع استفاده شده است')
        except BreakSignal: raise NovaRuntimeError('break خارج از حلقه استفاده شده است')
        except ContinueSignal: raise NovaRuntimeError('continue خارج از حلقه استفاده شده است')
    def exec_block(self,stmts,env,scoped=True):
        local=Env(env) if scoped else env
        for s in stmts: self.exec_stmt(s,local)
    def exec_stmt(self,s,e):
        k=s[0]
        if k=='block': self.exec_block(s[1],e); return
        if k=='decl':
            _,n,t,x,c=s; e.define(n,self.eval(x,e),t,c); return
        if k=='show': self.output(self.display(self.eval(s[1],e))); return
        if k=='exprstmt': self.eval(s[1],e); return
        if k=='assign':
            _,target,op,x=s; val=self.eval(x,e)
            if op!='=': val=self.binary(op[0],self.eval(target,e),val)
            self.assign(target,val,e); return
        if k=='if': self.exec_block(s[2][1],e) if self.truth(self.eval(s[1],e)) else self.exec_block(s[3][1],e); return
        if k=='while':
            guard=0
            while self.truth(self.eval(s[1],e)):
                guard+=1
                if guard>1_000_000: raise NovaRuntimeError('حلقه بیش از حد طولانی شد')
                try: self.exec_block(s[2][1],e)
                except ContinueSignal: continue
                except BreakSignal: break
            return
        if k=='for':
            _,n,a,b,step,body=s; start=self.eval(a,e); stop=self.eval(b,e); delta=self.eval(step,e)
            if not all(isinstance(x,(int,float)) and not isinstance(x,bool) for x in (start,stop,delta)) or delta==0: raise NovaRuntimeError('بازهٔ for باید عددی و گام غیرصفر باشد')
            i=start; guard=0
            while i<stop if delta>0 else i>stop:
                guard+=1
                if guard>1_000_000: raise NovaRuntimeError('حلقه بیش از حد طولانی شد')
                loop=Env(e); loop.define(n,i)
                try: self.exec_block(body[1],loop)
                except ContinueSignal: pass
                except BreakSignal: break
                i+=delta
            return
        if k=='function':
            _,n,p,r,b=s; e.define(n,Function(n,p,b,e)); return
        if k=='class':
            _,n,members=s; methods={}
            for m in members:
                if m[0]=='function':
                    _,mn,p,r,b=m; methods[mn]=Function(mn,p,b,e)
                elif m[0]=='decl': pass
                else: raise NovaRuntimeError('درون class فقط فیلد یا function مجاز است')
            e.define(n,NovaClass(n,methods)); return
        if k=='return': raise ReturnSignal(self.eval(s[1],e))
        if k=='break': raise BreakSignal()
        if k=='continue': raise ContinueSignal()
        raise NovaRuntimeError(f'دستور ناشناخته: {k}')
    def truth(self,v): return bool(v)
    def eval(self,x,e):
        k=x[0]
        if k=='literal': return x[1]
        if k=='var': return e.get(x[1])
        if k=='list': return [self.eval(a,e) for a in x[1]]
        if k=='unary':
            op=self.eval(x[2],e)
            if x[1]=='-': return -op
            if x[1]=='+': return +op
            return not bool(op)
        if k=='binary':
            op=x[1]; a=self.eval(x[2],e)
            if op=='and': return bool(a) and bool(self.eval(x[3],e))
            if op=='or': return bool(a) or bool(self.eval(x[3],e))
            b=self.eval(x[3],e); return self.binary(op,a,b)
        if k=='member':
            obj=self.eval(x[1],e); n=x[2]
            if isinstance(obj,Instance):
                if n in obj.fields: return obj.fields[n]
                if n in obj.klass.methods: return BoundMethod(obj.klass.methods[n],obj)
            if isinstance(obj,dict) and n in obj: return obj[n]
            raise NovaRuntimeError(f'عضو {n!r} وجود ندارد')
        if k=='index':
            obj=self.eval(x[1],e); idx=self.eval(x[2],e)
            try: return obj[idx]
            except Exception: raise NovaRuntimeError('اندیس نامعتبر است')
        if k=='call':
            fn=self.eval(x[1],e); args=[self.eval(a,e) for a in x[2]]
            if isinstance(fn,BoundMethod): return self.call_function(fn.function,args,fn.instance)
            if isinstance(fn,Function): return self.call_function(fn,args)
            if callable(fn):
                try: return fn(*args)
                except NovaRuntimeError: raise
                except Exception as ex: raise NovaRuntimeError(f'خطا در فراخوانی: {ex}')
            raise NovaRuntimeError('این عبارت قابل فراخوانی نیست')
        if k=='new':
            cls=e.get(x[1]); args=[self.eval(a,e) for a in x[2]]
            if not isinstance(cls,NovaClass): raise NovaRuntimeError(f'{x[1]} یک class نیست')
            inst=Instance(cls,{})
            if 'init' in cls.methods: self.call_function(cls.methods['init'],args,inst)
            elif args: raise NovaRuntimeError('این class سازنده ندارد')
            return inst
        raise NovaRuntimeError(f'عبارت ناشناخته: {k}')
    def binary(self,op,a,b):
        try:
            if op=='+': return a+b
            if op=='-': return a-b
            if op=='*': return a*b
            if op=='/': return a/b
            if op=='%': return a%b
            if op=='==': return a==b
            if op=='!=': return a!=b
            if op=='<': return a<b
            if op=='>': return a>b
            if op=='<=': return a<=b
            if op=='>=': return a>=b
            if op=='in': return a in b
        except Exception as ex: raise NovaRuntimeError(f'عملگر {op} برای این مقادیر معتبر نیست: {ex}')
        raise NovaRuntimeError(f'عملگر ناشناخته {op}')
    def assign(self,target,value,e):
        if target[0]=='var': e.set(target[1],value); return
        if target[0]=='member':
            obj=self.eval(target[1],e)
            if not isinstance(obj,Instance): raise NovaRuntimeError('فقط ویژگی شیء قابل تغییر است')
            obj.fields[target[2]]=value; return
        if target[0]=='index':
            obj=self.eval(target[1],e); idx=self.eval(target[2],e)
            try: obj[idx]=value; return
            except Exception: raise NovaRuntimeError('نمی‌توان این اندیس را تغییر داد')
        raise NovaRuntimeError('سمت چپ انتساب باید متغیر، ویژگی یا اندیس باشد')
    def call_function(self,fn,args,instance=None):
        if len(args)!=len(fn.params): raise NovaRuntimeError(f'{fn.name} به {len(fn.params)} آرگومان نیاز دارد؛ {len(args)} داده شد')
        env=Env(fn.closure)
        if instance is not None: env.define('self',instance)
        for (n,t),v in zip(fn.params,args): env.define(n,v,t)
        try: self.exec_block(fn.body[1],env,scoped=False)
        except ReturnSignal as r: return r.value
        return None
