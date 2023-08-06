# Python Code Sandboxing Utility
 #-
 # Copyright (c) 2013 Clint Banis (hereby known as "The Author")
 # All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions
 # are met:
 # 1. Redistributions of source code must retain the above copyright
 #    notice, this list of conditions and the following disclaimer.
 # 2. Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the
 #    documentation and/or other materials provided with the distribution.
 # 3. All advertising materials mentioning features or use of this software
 #    must display the following acknowledgement:
 #        This product includes software developed by The Author, Clint Banis.
 # 4. The name of The Author may not be used to endorse or promote products
 #    derived from this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS
 # ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 # TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 # PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
 # BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 # CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 # SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 # INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 # CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 # ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 # POSSIBILITY OF SUCH DAMAGE.
 #
# Todo: from common tools.
from compiler.transformer import Transformer
from compiler.pycodegen import ExpressionCodeGenerator
from compiler import syntax, misc
from compiler.ast import Node, Name, CallFunc, Getattr

class Sandbox(dict):
    def parse(self, expr):
        return Transformer().parseexpr(expr)

    def compile(self, expr, filename = None):
        # Parse input to AST.
        ast = self.parse(expr)

        # Scrub out any unsafe code.
        ast = self.scrubtree(ast)

        # Compile transformed tree to bytecode.
        misc.set_filename(filename or '', ast)
        syntax.check(ast)

        gen = ExpressionCodeGenerator(ast)
        return gen.getCode()

    def eval(self, expr, filename = None):
        # I don't know if this can be blocked, so we just ignore it.
        self['__builtins__'] = {}

        return eval(self.compile(expr, filename = filename),
                    self, self)

    def scrubtree(self, ast):
        # Scrub member functions, any functions not in namespace.
        def w(n):
            # Walk the syntax tree, looking for improper Names and CallFuncs.
            if isinstance(n, Node):
                if isinstance(n, Name):
                    if n.name not in self:
                        raise NameError(n.name)

                elif isinstance(n, CallFunc):
                    if not isinstance(n.node, Name):
                        raise SyntaxError('Only simple function calls allowed')

                # Todo: hide underscored attributes.
                elif isinstance(n, Getattr):
                    if n.attrname.startswith('_'):
                        raise AttributeError(n.attrname)

                # Recursive traversal.
                for c in n.getChildren():
                    w(c)

        w(ast)
        return ast

    def derive(self, **kwd):
        sub = Sandbox(self)
        sub.update(kwd)
        return sub

    def __call__(self, expr, **kwd):
        # No filename?
        return self.derive(**kwd).eval(expr)

    # Tools:
    def toLiteral(self, expr):
        r = self.eval(expr)
        if not isinstance(r, (int, long, float, basestring, list, tuple, dict)):
            raise TypeError(type(r).__name__)

        return r

    def extract(self, expr):
        def _(node):
            if isinstance(node, Node):
                if isinstance(node, (Name, CallFunc)):
                    yield node

                for c in node.getChildren():
                    for x in _(c):
                        yield x

        return list(_(self.parse(expr)))

    def examine(self, expr):
        # Show structure.
        def _(ast, indent = 0):
            tab = '  ' * indent
            if isinstance(ast, (int, float, long, basestring)):
                print '%s%r' % (tab, ast)
            else:
                print '%s%s' % (tab, ast.__class__.__name__)

            try: children = ast.getChildren()
            except AttributeError: pass
            else:
                for c in children:
                    if c is not None:
                        _(c, indent + 1)

        _(self.parse(expr))

# Exposed (safe) functions:
def safe(function):
    function._is_safe = True
    return function

def CallOpaqueMethod(object, name, *args, **kwd):
    # Perform the method-call on an object that is otherwise not allowed.
    # This is required for the submethod pattern.
    method = getattr(object, name)
    if not getattr(method, '_is_safe', False):
        raise AttributeError('Unsafe method: ' + name)

    return method(*args, **kwd)

def print_(*args):
    print ' '.join(map(str, args))

def percentage(a, b, n = 2):
    f = '%%.%df' % min(max(0, int(n)), 8)
    return f % ((float(a) / b) * 100)


# Default sandbox (commonly-used symbols):
##    from string import join
##    s = Sandbox(pr = print_,
##                join = join,
##                percentage = percentage,
##                str = str,
##                lbrace = '{',
##                rbrace = '}',
##                call = CallOpaqueMethod,
##                xrange = xrange)
