def repl(code):
    compiled = ""
    for l, line in enumerate(code):
        compiled += line + '\n'
    base.reset()
    exec(compiled)
