#!/usr/bin/env python3
"""Metacircular evaluator — a language that interprets itself. #300 MILESTONE 🏆"""
import sys

def tokenize(s):return s.replace('(',' ( ').replace(')',' ) ').split()

def parse(tokens):
    if not tokens:raise SyntaxError("unexpected EOF")
    t=tokens.pop(0)
    if t=='(':
        L=[]
        while tokens[0]!=')':L.append(parse(tokens))
        tokens.pop(0);return L
    elif t==')':raise SyntaxError("unexpected )")
    try:return int(t)
    except:
        try:return float(t)
        except:return t

class Env(dict):
    def __init__(self,params=(),args=(),outer=None):
        self.update(zip(params,args));self.outer=outer
    def find(self,var):
        if var in self:return self
        if self.outer:return self.outer.find(var)
        raise NameError(f"unbound: {var}")

def eval_(x,env):
    if isinstance(x,str):return env.find(x)[x]
    if not isinstance(x,list):return x
    op=x[0]
    if op=='quote':return x[1]
    elif op=='if':return eval_(x[2],env) if eval_(x[1],env) else eval_(x[3] if len(x)>3 else False,env)
    elif op=='define':
        if isinstance(x[1],list):  # (define (f args) body)
            name,params=x[1][0],x[1][1:]
            env[name]=lambda *a,p=params,b=x[2:],e=env:[eval_(expr,Env(p,a,e)) for expr in b][-1]
        else:env[x[1]]=eval_(x[2],env)
    elif op=='set!':env.find(x[1])[x[1]]=eval_(x[2],env)
    elif op=='lambda':
        params,body=x[1],x[2:]
        return lambda *a,p=params,b=body,e=env:[eval_(expr,Env(p,a,e)) for expr in b][-1]
    elif op=='begin':
        val=None
        for expr in x[1:]:val=eval_(expr,env)
        return val
    elif op=='cond':
        for clause in x[1:]:
            if clause[0]=='else' or eval_(clause[0],env):return eval_(clause[1],env)
    elif op=='and':
        val=True
        for expr in x[1:]:
            val=eval_(expr,env)
            if not val:return val
        return val
    elif op=='or':
        for expr in x[1:]:
            val=eval_(expr,env)
            if val:return val
        return False
    elif op=='let':
        bindings,body=x[1],x[2:]
        params=[b[0] for b in bindings]
        args=[eval_(b[1],env) for b in bindings]
        return [eval_(expr,Env(params,args,env)) for expr in body][-1]
    elif op=='eval':  # metacircular!
        return eval_(eval_(x[1],env),env)
    else:
        proc=eval_(op,env)
        args=[eval_(a,env) for a in x[1:]]
        return proc(*args)

def standard_env():
    import operator as op,math
    e=Env()
    e.update({'+':op.add,'-':op.sub,'*':op.mul,'/':op.truediv,'//':op.floordiv,
        '%':op.mod,'>':op.gt,'<':op.lt,'>=':op.ge,'<=':op.le,'=':op.eq,
        'not':op.not_,'abs':abs,'max':max,'min':min,
        'car':lambda x:x[0],'cdr':lambda x:x[1:],'cons':lambda a,b:[a]+list(b),
        'list':lambda *x:list(x),'null?':lambda x:x==[],'length':len,
        'append':lambda *x:sum((list(a) for a in x),[]),
        'map':lambda f,l:list(map(f,l)),'filter':lambda f,l:list(filter(f,l)),
        'apply':lambda f,a:f(*a),'number?':lambda x:isinstance(x,(int,float)),
        'symbol?':lambda x:isinstance(x,str),'display':lambda x:print(x,end=''),
        'newline':lambda:print(),'sqrt':math.sqrt,'pi':math.pi,'#t':True,'#f':False})
    return e

def run(code):
    env=standard_env();tokens=tokenize(code);results=[]
    while tokens:results.append(eval_(parse(tokens),env))
    return results,env

def main():
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        r,_=run("(+ 1 2)")
        assert r[0]==3
        r,_=run("(define (fact n) (if (<= n 1) 1 (* n (fact (- n 1))))) (fact 10)")
        assert r[-1]==3628800
        r,_=run("(define (fib n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2))))) (fib 10)")
        assert r[-1]==55
        # Metacircular: eval a quoted expression
        r,_=run("(eval (quote (+ 2 3)))")
        assert r[0]==5
        # Higher-order
        r,_=run("(map (lambda (x) (* x x)) (list 1 2 3 4 5))")
        assert r[0]==[1,4,9,16,25]
        # Let
        r,_=run("(let ((a 10) (b 20)) (+ a b))")
        assert r[0]==30
        # Closures
        r,_=run("(define (make-adder n) (lambda (x) (+ n x))) (define add5 (make-adder 5)) (add5 10)")
        assert r[-1]==15
        print("All tests passed! 🏆 #300 MILESTONE")
    else:
        print("metacircular-py: A language that interprets itself 🏆")
        r,_=run("(define (fact n) (if (<= n 1) 1 (* n (fact (- n 1))))) (fact 20)")
        print(f"  20! = {r[-1]}")
        r,_=run("(eval (quote (* 6 7)))")
        print(f"  (eval '(* 6 7)) = {r[0]}")
if __name__=="__main__":main()
