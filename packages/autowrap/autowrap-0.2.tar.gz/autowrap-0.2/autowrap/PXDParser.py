import pdb
#encoding: utf-8
from Cython.Compiler.CmdLine import parse_command_line
from Cython.Compiler.Main import create_default_resultobj, CompilationSource
from Cython.Compiler import Pipeline
from Cython.Compiler.Scanning import FileSourceDescriptor
from Cython.Compiler.Nodes import *
from Cython.Compiler.ExprNodes import *

from Types import CppType

import re
import os

import logging as L

from collections import defaultdict, OrderedDict

"""
Methods in this module use Cythons Parser to build an Cython syntax tree
from the annotated .pxd files and creates a represenation of the
included classes and methods.
"""




def parse_class_annotations(node, lines):
    """ parses wrap-instructions inside comments below class def """
    start_at_line = node.pos[1]
    return _parse_multiline_annotations(lines[start_at_line:])


def _parse_multiline_annotations(lines):
    """ does the hard work for parse_class_annotations, and is
        better testable than this.
    """
    it = iter(lines)
    result = defaultdict(list)
    while it:
        try:
            line = it.next().strip()
        except StopIteration:
            break
        if not line:
            continue
        if line.startswith("#"):
            line = line[1:].strip()
            if line.endswith(":"):
                key = line.rstrip(":")
                line = it.next().strip()
                while line.startswith("#  "):
                    value = line[1:].strip()
                    result[key].append(value)
                    line = it.next().strip()
            else:
                key = line
                result[key] = True
        else:
            break
    return result


def parse_line_annotations(node, lines):
    """
       parses comments at end of line, in most cases the lines of
       method declarations
    """

    parts = lines[node.pos[1] - 1].split("#", 1)
    result = dict()
    if len(parts)==2:
        # parse_pxd_file python statements in comments
        fields = [ f.strip() for f in parts[1].split(" ") ]
        for f in fields:
            if ":" in f:
                key, value = f.split(":", 1)
            else:
                key, value = f, True
        result[key] = value
    return result


def _extract_type(base_type, decl):
    """ extracts type information from node in parse_pxd_file tree """

    template_parameters = None
    if isinstance(base_type, TemplatedTypeNode):
        template_parameters = []
        for arg in base_type.positional_args:
            if isinstance(arg, CComplexBaseTypeNode):
                arg_decl = arg.declarator
                is_ptr = isinstance(arg_decl, CPtrDeclaratorNode)
                is_ref = isinstance(arg_decl, CReferenceDeclaratorNode)
                is_unsigned = hasattr(arg.base_type, "signed") and not arg.base_type.signed
                is_long = hasattr(arg.base_type, "longness") and arg.base_type.longness
                name = arg.base_type.name
                ttype = CppType(name, None, is_ptr, is_ref, is_unsigned,
                        is_long)
                template_parameters.append(ttype)
            elif isinstance(arg, NameNode):
                name = arg.name
                template_parameters.append(CppType(name))
            elif isinstance(arg, IndexNode): # nested template !
                # only handles one nesting level !
                name = arg.base.name
                if hasattr(arg.index, "args"):
                    args = [ CppType(a.name) for a in arg.index.args ]
                else:
                    args = [ CppType(arg.index.name) ]
                tt = CppType(name, args)
                template_parameters.append(tt)
            else:
                raise Exception("can not handle template arg %r" % arg)

        base_type = base_type.base_type_node

    is_ptr = isinstance(decl, CPtrDeclaratorNode)
    is_ref = isinstance(decl, CReferenceDeclaratorNode)
    is_unsigned = hasattr(base_type, "signed") and not base_type.signed
    is_long = hasattr(base_type, "longness") and base_type.longness
    return CppType(base_type.name, template_parameters, is_ptr, is_ref,
                   is_unsigned, is_long)

class SubtreeParserInterfaceChecker(type):

    def __new__(mcs, name, bases, dict_):
        msg = "TreeHandlerInterface not implemented"
        parseTree = dict_.get("parseTree")
        assert parseTree is not None, msg
        assert isinstance(parseTree, classmethod), msg
        nargs = parseTree.__func__.func_code.co_argcount
        assert nargs == 4, msg
        return type(name, bases, dict_)


class BaseDecl(object):

    def __init__(self, name, annotations, pxd_path):
        self.name = name
        self.annotations = annotations
        self.pxd_path = pxd_path


class CTypeDefDecl(BaseDecl):

    __metaclass__ = SubtreeParserInterfaceChecker

    def __init__(self, new_name, type_,  annotations, pxd_path):
        super(CTypeDefDecl, self).__init__(new_name, annotations, pxd_path)
        self.type_ = type_

    @classmethod
    def parseTree(cls, node, lines, pxd_path):
        decl = node.declarator
        if isinstance(decl, CPtrDeclaratorNode):
            new_name = decl.base.name
        else:
            new_name = decl.name
        type_ = _extract_type(node.base_type, node.declarator)
        annotations = parse_line_annotations(node, lines)
        return cls(new_name, type_, annotations, pxd_path)


class EnumDecl(BaseDecl):

    __metaclass__ = SubtreeParserInterfaceChecker

    def __init__(self, name, items, annotations, pxd_path):
        super(EnumDecl, self).__init__(name, annotations, pxd_path)
        self.items = items
        self.template_parameters = None

    @classmethod
    def parseTree(cls, node, lines, pxd_path):
        name = node.name
        items = []
        annotations = parse_class_annotations(node, lines)
        current_value = 0
        for item in node.items:
            if item.value is not None:
                current_value = item.value.constant_result
            items.append((item.name, current_value))
            current_value += 1

        return cls(name, items, annotations, pxd_path)

    def __str__(self):
        res = "EnumDecl %s : " % self.name
        res += ", ".join("%s: %d" % (i, v) for (i, v) in self.items)
        return res

    def get_method_decls(self):
        return []


class CppClassDecl(BaseDecl):

    __metaclass__ = SubtreeParserInterfaceChecker

    def __init__(self, name, template_parameters, methods, attributes, annotations,
                 pxd_path):
        super(CppClassDecl, self).__init__(name, annotations, pxd_path)
        self.methods = methods
        self.attributes = attributes
        self.template_parameters = template_parameters

    @classmethod
    def parseTree(cls, node, lines, pxd_path):
        name = node.name
        template_parameters = node.templates
        class_annotations = parse_class_annotations(node, lines)
        methods = OrderedDict()
        attributes = []
        for att in node.attributes:
            decl = MethodOrAttributeDecl.parseTree(att, lines, pxd_path)
            if decl is not None:
                if isinstance(decl, CppMethodOrFunctionDecl):
                    # an OrderedDefaultDict(list) would be nice here:
                    methods.setdefault(decl.name,[]).append(decl)
                elif isinstance(decl, CppAttributeDecl):
                    attributes.append(decl)

        return cls(name, template_parameters, methods, attributes, class_annotations,
                   pxd_path)

    def __str__(self):
        rv = ["cppclass %s: " % (self.name, )]
        for meth_list in self.methods.values():
            rv += ["     " + str(method) for method in meth_list]
        return "\n".join(rv)

    def get_transformed_methods(self, mapping):
        result = defaultdict(list)
        for mdcl in self.get_method_decls():
            result[mdcl.name].append(mdcl.transformed(mapping))
        return result

    def get_method_decls(self):
        for name, method_decls in self.methods.items():
            for method_decl in method_decls:
                yield method_decl

    def has_method(self, other_decl):
        with_same_name = self.methods.get(other_decl.name)
        if with_same_name is None:
            return False
        return any(decl.matches(other_decl) for decl in with_same_name)

    def attach_base_methods(self, dd):
        for name, decls in dd.items():
            for decl in decls:
                if not self.has_method(decl):
                    self.methods.setdefault(decl.name,[]).append(decl)

class CppAttributeDecl(BaseDecl):

    def __init__(self, name, type_, annotations, pxd_path):
        super(CppAttributeDecl, self).__init__(name, annotations,
                                                      pxd_path)
        self.type_ = type_



class CppMethodOrFunctionDecl(BaseDecl):

    def __init__(self, result_type,  name, arguments, annotations, pxd_path):
        super(CppMethodOrFunctionDecl, self).__init__(name, annotations,
                                                      pxd_path)
        self.result_type = result_type
        self.arguments = arguments

    def transformed(self, typemap):
        result_type = self.result_type.transformed(typemap)
        args = [(n, t.transformed(typemap)) for n, t in self.arguments]
        return CppMethodOrFunctionDecl(result_type, self.name, args,
                                       self.annotations, self.pxd_path)

    def matches(self, other):
        """ only checks method name signature,
            does not consider argument names"""
        if self.name != other.name:
            return False
        self_key = [self.result_type] + [t for (__, t) in self.arguments]
        other_key = [other.result_type] + [t for (__, t) in other.arguments]
        return self_key == other_key


class MethodOrAttributeDecl(object):

    @classmethod
    def parseTree(cls, node, lines, pxd_path):
        annotations = parse_line_annotations(node, lines)
        if isinstance(node, CppClassNode):
            return None # nested classes only can be delcared in pxd

        decl, = node.declarators
        result_type = _extract_type(node.base_type, decl)

        if isinstance(decl, CNameDeclaratorNode):
            return CppAttributeDecl(decl.name, result_type, annotations,
                                                                      pxd_path)

        if isinstance(decl.base, CFuncDeclaratorNode):
            decl = decl.base

        name = decl.base.name
        args = []
        for arg in decl.args:
            argdecl = arg.declarator
            if isinstance(argdecl, CReferenceDeclaratorNode): 
                argname = argdecl.base.name
            elif isinstance(argdecl, CPtrDeclaratorNode):
                base = argdecl.base
                if isinstance(base, CPtrDeclaratorNode):
                    raise Exception("multi ptr not supported")
                argname = base.name
            else:
                if not hasattr(argdecl, "name"):
                    argname = argdecl.base.base.name
                else:
                    argname = argdecl.name
            tt = _extract_type(arg.base_type, argdecl)
            args.append((argname,tt))

        return CppMethodOrFunctionDecl(result_type, name, args, annotations, pxd_path)

    def __str__(self):
        rv = str(self.result_type)
        rv += " " + self.name
        argl = [str(type_) + " " + str(name) for name, type_ in self.arguments]
        return rv + "(" + ", ".join(argl) + ")"


def parse_str(what):
    import tempfile

    # delete=False keeps file after closing it !
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(what)
        fp.flush()
        fp.close() # needed for reading it on win
        result = parse_pxd_file(fp.name)
        return result


def parse_pxd_file(path):

    options, sources = parse_command_line(["--cplus", path])

    path = os.path.abspath(path)
    basename = os.path.basename(path)
    name, ext = os.path.splitext(basename)

    source_desc = FileSourceDescriptor(path, basename)
    source = CompilationSource(source_desc, name, os.getcwd())
    result = create_default_resultobj(source, options)

    context = options.create_context()
    pipeline = Pipeline.create_pyx_pipeline(context, options, result)
    context.setup_errors(options, result)
    root = pipeline[0](source)  # only parser

    def iter_bodies(tree):
        try:
            for n in tree.body.stats[0].stats:
                # cimports at head of file
                yield n
        except:
            pass
        if hasattr(tree.body, "stats"):
            for s in tree.body.stats:
                if isinstance(s, CDefExternNode):
                    body = s.body
                    if hasattr(body, "stats"):
                        for node in body.stats:
                            yield node
                    else:
                        yield body
        elif hasattr(tree.body, "body"):
            body = tree.body.body
            yield body
        else:
            raise Exception("parse_pxd_file failed: no valied .pxd file !")

    lines = open(path).readlines()

    def cimport(b, _, __):
        print "cimport", b.module_name, "as", b.as_name

    handlers = { CEnumDefNode : EnumDecl.parseTree,
                 CppClassNode : CppClassDecl.parseTree,
                 CTypeDefNode : CTypeDefDecl.parseTree,
                 CVarDefNode  : MethodOrAttributeDecl.parseTree,
                 CImportStatNode  : cimport,
                 }

    result = []
    for body in iter_bodies(root):
        handler = handlers.get(type(body))
        if handler is not None:
            L.info("parsed %s, handler=%s" % (body.__class__, handler.im_self))
            result.append(handler(body, lines, path))
        else:
            for node in getattr(body, "stats", []):
                handler = handlers.get(type(node))
                if handler is not None:
                    L.info("parsed %s, handler=%s" % (node.__class__,
                                                      handler.im_self))
                    result.append(handler(node, lines, path))
    return result

if __name__ == "__main__":

    import sys
    print parse_pxd_file(sys.argv[1])
