from M30W.parser import get_spec


class Block():
    def __init__(self, code, cargs):
        """__init__(code (Line object), cargs) -> Block object

        Returns a new Block object."""
        self.cargs = cargs
        self.code = code
        self.sprite = code.sprite
        self.line = code.line

        self.spec = get_spec(self.code)
        if not self.spec:
            raise SyntaxError("""SyntaxError at line %s in sprite %s.
Could not parse %s.""" % (self.line + 1, self.sprite, self.code))
        self.args = self.spec.get_args(self.code)

    def __call__(self):
        """__call__()

        Executes this block (NOT queuing up)
        Returns when finished running (or never)"""
        args = []
        #If inputs are reporters
        for arg in self.args:
            if not arg.__class__ == Block:
                args.append(arg)
            else:
                args.append(arg())
        try:
            getattr(self.sprite, self.handler)(args=args, cargs=self.cargs)
        except Exception:
            raise RuntimeError('Caught runtime exception at line %s.')
