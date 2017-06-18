import execjs

print(execjs.eval("'1 2 3'.split()"))
ctx = execjs.compile("""
    function add(x, y){
        return x + y;
    }
""")
print(ctx.call('add', 1, 2))
