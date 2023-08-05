"""Convert ASTs into L{pydoctor.model.Documentable} instances."""
from pydoctor import model, ast_pp

from compiler import visitor, transformer, ast
import symbol, token

class str_with_orig(str):
    """Hack to allow recovery of the literal that gave rise to a docstring in an AST.

    We do this to allow the users to edit the original form of the docstring in the
    editing server defined in the L{server} module.

    @ivar orig: The literal that gave rise to this constant in the AST.
    """
    pass

class MyTransformer(transformer.Transformer):
    """Custom transformer that creates Nodes with L{str_with_orig} instances for docstrings."""
    def get_docstring(self, node, n=None):
        """Override C{transformer.Transformer.get_docstring} to return a L{str_with_orig} object."""
        if n is None:
            n = node[0]
            node = node[1:]
        if n == symbol.suite:
            if len(node) == 1:
                return self.get_docstring(node[0])
            for sub in node:
                if sub[0] == symbol.stmt:
                    return self.get_docstring(sub)
            return None
        if n == symbol.file_input:
            for sub in node:
                if sub[0] == symbol.stmt:
                    return self.get_docstring(sub)
            return None
        if n == symbol.atom:
            if node[0][0] == token.STRING:
                s = ''
                for t in node:
                    s = s + eval(t[1])
                r = str_with_orig(s)
                r.orig = ''.join(t[1] for t in node)
                r.linenumber = node[0][2]
                return r
            return None
        if n == symbol.stmt or n == symbol.simple_stmt \
           or n == symbol.small_stmt:
            return self.get_docstring(node[0])
        if n in transformer._doc_nodes and len(node) == 1:
            return self.get_docstring(node[0])
        return None


def parseFile(path):
    """Duplicate of L{compiler.parseFile} that uses L{MyTransformer}."""
    f = open(path, "U")
    src = f.read() + "\n"
    f.close()
    return parse(src)


def parse(buf):
    """Duplicate of L{compiler.parse} that uses L{MyTransformer}."""
    return MyTransformer().parsesuite(buf)


class ModuleVistor(object):
    def __init__(self, builder, module):
        self.builder = builder
        self.system = builder.system
        self.module = module

    def default(self, node):
        for child in node.getChildNodes():
            self.visit(child)

    def visitModule(self, node):
        assert self.module.docstring is None
        self.module.docstring = node.doc
        self.builder.push(self.module)
        self.default(node)
        self.builder.pop(self.module)

    def visitClass(self, node):
        rawbases = []
        bases = []
        baseobjects = []
        current = self.builder.current
        for n in node.bases:
            str_base = ast_pp.pp(n)
            rawbases.append(str_base)
            base = current.dottedNameToFullName(str_base)
            bob = self.system.objForFullName(base)
            if not bob and self.system.options.resolvealiases:
                base = self.system.resolveAlias(base)
                bob = self.system.objForFullName(base)
            if bob:
                assert (bob.parentMod is self.builder.currentMod or
                        bob.parentMod.state > 0)
            bases.append(base)
            baseobjects.append(bob)

        cls = self.builder.pushClass(node.name, node.doc)
        cls.decorators = []

        def node2data(node):
            parts = []
            while isinstance(node, ast.Getattr):
                parts.append(node.attrname)
                node = node.expr
            if isinstance(node, ast.Name):
                parts.append(node.name)
            else:
                return None
            dotted_name = '.'.join(reversed(parts))
            full_name = self.builder.current.dottedNameToFullName(dotted_name)
            obj = self.system.allobjects.get(full_name)
            return (dotted_name, full_name, obj)

        if node.decorators:
            for decnode in node.decorators:
                if isinstance(decnode, ast.CallFunc):
                    args = []
                    for arg in decnode.args:
                        args.append(node2data(arg))
                    base = node2data(decnode.node)
                else:
                    base = node2data(decnode)
                    args = None
                cls.decorators.append((base, args))

        if node.lineno is not None:
            cls.linenumber = node.lineno
        if cls.parentMod.sourceHref:
            cls.sourceHref = cls.parentMod.sourceHref + '#L' + \
                             str(cls.linenumber)
        cls.rawbases = rawbases
        cls.bases = bases
        cls.baseobjects = baseobjects
        for b in cls.baseobjects:
            if b is not None:
                b.subclasses.append(cls)
        self.default(node)
        self.builder.popClass()

    def visitFrom(self, node):
        modname = self.builder.expandModname(node.modname)
        mod = self.system.getProcessedModule(modname)
        if mod is not None:
            assert mod.state in [model.PROCESSING, model.PROCESSED]
        name2fullname = self.builder.current._name2fullname
        for fromname, asname in node.names:
            if fromname == '*':
                if mod is None:
                    self.builder.warning("import * from unknown", modname)
                    return
                self.builder.warning("import *", modname)
                if mod.all is not None:
                    names = mod.all
                else:
                    names = [k for k in mod.contents.keys()
                             if not k.startswith('_')]
                for n in names:
                    name2fullname[n] = modname + '.' + n
                return
            if asname is None:
                asname = fromname
            if isinstance(self.builder.current, model.Module) and \
                   self.builder.current.all is not None and \
                   asname in self.builder.current.all and \
                   modname in self.system.allobjects:
                mod = self.system.allobjects[modname]
                if isinstance(mod, model.Module) and \
                       fromname in mod.contents and \
                       (mod.all is None or fromname not in mod.all):
                    self.system.msg(
                        "astbuilder",
                        "moving %r into %r"
                        % (mod.contents[fromname].fullName(),
                           self.builder.current.fullName()))
                    # this code attempts to preserve "rather a lot" of
                    # invariants assumed by various bits of pydoctor
                    # and that are of course not written down anywhere
                    # :/
                    ob = mod.contents[fromname]
                    targetmod = self.builder.current
                    del self.system.allobjects[ob.fullName()]
                    ob.parent = ob.parentMod = targetmod
                    ob.prefix = targetmod.fullName() + '.'
                    ob.name = asname
                    self.system.allobjects[ob.fullName()] = ob
                    del mod.contents[fromname]
                    mod.orderedcontents.remove(ob)
                    mod._name2fullname[fromname] = ob.fullName()
                    targetmod.contents[asname] = ob
                    targetmod.orderedcontents.append(ob)
                    targetmod._name2fullname[ob.name] = ob.fullName()
                    continue
            if isinstance(
                self.system.objForFullName(modname), model.Package):
                self.system.getProcessedModule(modname + '.' + fromname)
            name2fullname[asname] = modname + '.' + fromname

    def visitImport(self, node):
        """Process an import statement.

        The grammar for the statement is roughly:

        mod_as := DOTTEDNAME ['as' NAME]
        import_stmt := 'import' mod_as (',' mod_as)*

        and this is translated into a node which is an instance of Import wih
        an attribute 'names', which is in turn a list of 2-tuples
        (dotted_name, as_name) where as_name is None if there was no 'as foo'
        part of the statement.
        """
        name2fullname = self.builder.current._name2fullname
        for fromname, asname in node.names:
            fullname = self.builder.expandModname(fromname)
            self.system.getProcessedModule(fullname)
            if asname is None:
                asname = fromname.split('.', 1)[0]
                # aaaaargh! python sucks.
                parts = fullname.split('.')
                for i, part in enumerate(fullname.split('.')[::-1]):
                    if part == asname:
                        fullname = '.'.join(parts[:len(parts)-i])
                        name2fullname[asname] = fullname
                        break
                else:
                    fullname = '.'.join(parts)
                    name2fullname[asname] = '.'.join(parts)
            else:
                name2fullname[asname] = fullname

    def visitAssign(self, node):
        if isinstance(self.builder.current, model.Class):
            if len(node.nodes) != 1:
                return
            if not isinstance(node.nodes[0], ast.AssName):
                return
            target = node.nodes[0].name
            if not isinstance(node.expr, ast.CallFunc):
                return
            func = node.expr.node
            if not isinstance(func, ast.Name):
                return
            func = func.name
            args = node.expr.args
            if len(args) != 1:
                return
            arg, = args
            if not isinstance(arg, ast.Name):
                return
            arg = arg.name
            if target == arg and func in ['staticmethod', 'classmethod']:
                target = self.builder.current.contents.get(target)
                if target and isinstance(target, model.Function):
                    if target.kind != 'Method':
                        self.system.msg('ast', 'XXX')
                    else:
                        target.kind = func.title().replace('m', ' M')

    def visitFunction(self, node):
        func = self.builder.pushFunction(node.name, node.doc)
        func.decorators = node.decorators
        if isinstance(func.parent, model.Class) and node.decorators:
            isclassmethod = False
            isstaticmethod = False
            for d in node.decorators.nodes:
                if isinstance(d, ast.Name):
                    if d.name == 'classmethod':
                        isclassmethod = True
                    elif d.name == 'staticmethod':
                        isstaticmethod = True
            if isstaticmethod:
                if isclassmethod:
                    self.system.msg(
                        'ast', '%r is both class- and static-method?'%(
                        func.fullName(),), thresh=-1)
                else:
                    func.kind = 'Static Method'
            elif isclassmethod:
                func.kind = 'Class Method'
        if node.lineno is not None:
            func.linenumber = node.lineno
        if func.parentMod.sourceHref:
            func.sourceHref = func.parentMod.sourceHref + '#L' + \
                              str(func.linenumber)
        # ast.Function has a pretty lame representation of
        # arguments. Let's convert it to a nice concise format
        # somewhat like what inspect.getargspec returns
        argnames = node.argnames[:]
        kwname = starargname = None
        if node.kwargs:
            kwname = argnames.pop(-1)
        if node.varargs:
            starargname = argnames.pop(-1)
        defaults = []
        for default in node.defaults:
            try:
                defaults.append(ast_pp.pp(default))
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception, e:
                self.builder.warning("unparseable default",
                                     "%s: %s %r"%(e.__class__.__name__,
                                                  e, default))
                defaults.append('???')
        # argh, convert unpacked-arguments from tuples to lists,
        # because that's what getargspec uses and the unit test
        # compares it
        argnames2 = []
        for argname in argnames:
            if isinstance(argname, tuple):
                argname = list(argname)
            argnames2.append(argname)
        func.argspec = (argnames2, starargname, kwname, tuple(defaults))
        #self.postpone(func, node.code)
        self.builder.popFunction()

class ASTBuilder(object):
    ModuleVistor = ModuleVistor

    def __init__(self, system):
        self.system = system
        self.current = None
        self.currentMod = None
        self._stack = []
        self.ast_cache = {}

    def _push(self, cls, name, docstring):
        obj = cls(self.system, name, docstring, self.current)
        self.system.addObject(obj)
        self.push(obj)
        # Method-level import to avoid a circular dependency.
        from pydoctor import epydoc2stan
        for attrobj in epydoc2stan.extract_fields(obj):
            self.system.addObject(attrobj)
        return obj

    def _pop(self, cls):
        assert isinstance(self.current, cls)
        self.pop(self.current)

    def push(self, obj):
        self._stack.append(self.current)
        self.current = obj
        if isinstance(obj, model.Module):
            assert self.currentMod is None
            obj.parentMod = self.currentMod = obj
        elif self.currentMod is not None:
            if obj.parentMod is not None:
                assert obj.parentMod is self.currentMod
            else:
                obj.parentMod = self.currentMod
        else:
            assert obj.parentMod is None

    def pop(self, obj):
        assert self.current is obj, "%r is not %r"%(self.current, obj)
        self.current = self._stack.pop()
        if isinstance(obj, model.Module):
            self.currentMod = None

    def pushClass(self, name, docstring):
        return self._push(self.system.Class, name, docstring)
    def popClass(self):
        self._pop(self.system.Class)

    def pushModule(self, name, docstring):
        return self._push(self.system.Module, name, docstring)
    def popModule(self):
        self._pop(self.system.Module)

    def pushFunction(self, name, docstring):
        return self._push(self.system.Function, name, docstring)
    def popFunction(self):
        self._pop(self.system.Function)

    def pushPackage(self, name, docstring):
        return self._push(self.system.Package, name, docstring)
    def popPackage(self):
        self._pop(self.system.Package)

    def warning(self, type, detail):
        self.system._warning(self.current, type, detail)

    def processModuleAST(self, ast, mod):
        findAll(ast, mod)
        visitor.walk(ast, self.ModuleVistor(self, mod))

    def expandModname(self, modname, givewarning=True):
        if '.' in modname:
            prefix, suffix = modname.split('.', 1)
            suffix = '.' + suffix
        else:
            prefix, suffix = modname, ''
        package = self.current.parentMod.parent
        if package is None:
            return modname
        if prefix in package.contents:
            if givewarning:
                self.warning("local import", modname)
            return package.contents[prefix].fullName() + suffix
        else:
            return modname

    def parseFile(self, filePath):
        if filePath in self.ast_cache:
            return self.ast_cache[filePath]
        try:
            ast = parseFile(filePath)
        except (SyntaxError, ValueError):
            self.warning("cannot parse", filePath)
            ast = None
        self.ast_cache[filePath] = ast
        return ast

model.System.defaultBuilder = ASTBuilder

def findAll(modast, mod):
    """Find and attempt to parse into a list of names the __all__ of a module's AST."""
    for node in modast.node.nodes:
        if isinstance(node, ast.Assign) and \
               len(node.nodes) == 1 and \
               isinstance(node.nodes[0], ast.AssName) and \
               node.nodes[0].name == '__all__':
            if mod.all is not None:
                mod.system.msg('all', "multiple assignments to %s.__all__ ??"%(mod.fullName(),))
            if not isinstance(node.expr, (ast.List, ast.Tuple)):
                mod.system.msg('all', "couldn't parse %s.__all__"%(mod.fullName(),))
                continue
            items = node.expr.nodes
            names = []
            for item in items:
                if not isinstance(item, ast.Const) or not isinstance(item.value, str):
                    mod.system.msg('all', "couldn't parse %s.__all__"%(mod.fullName(),))
                    continue
                names.append(item.value)
                mod.all = names

