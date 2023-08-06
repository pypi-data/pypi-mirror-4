import os
import sys
import glob
import autowrap.version
import autowrap.Code
import argparse

def main():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("pxds", action="store", nargs="+")
    parser.add_argument("--addons", action="store", nargs="*",
            metavar="addon")
    parser.add_argument("--converters", action="store", nargs="*",
            metavar="converter")
    parser.add_argument("--out", action="store", nargs=1, metavar="pyx file")
    version_str = "%d.%d.%d" % autowrap.version
    parser.add_argument("--version", action='version', version='%(prog)s '\
                                                                 + version_str)

    input_ = parser.parse_args()
    out, = input_.out
    __, out_ext = os.path.splitext(out)

    if out_ext != ".pyx":
        parser.exit(1, "\nout file has wrong extension: '.pyx' required\n")

    def collect(from_, extension):
        collected = []
        if from_ is None:
            return collected
        for item in from_:
            if os.path.isdir(item):
                for basename in os.listdir(item):
                    collected.append((os.path.join(item, basename)))
            else:
                collected.extend(glob.glob(item))
        collected = sorted(set(collected))
        result = []
        for item in collected:
            __, ext = os.path.splitext(item)
            if ext != extension:
                print "WARNING: ignore %s" % item
            else:
                result.append(item)
        return result

    pxds = collect(input_.pxds, ".pxd")
    if not pxds:
        parser.exit(1, "\nno pxd input files specified\n")
    addons = collect(input_.addons, ".pyx")
    converters = collect(input_.converters, ".py")
    print
    print "STATUS:"
    print "   %5d pxd input files to parse" % len(pxds)
    print "   %5d add on files to process" % len(addons)
    print "   %5d type converter files to consider" % len(converters)
    print

    run(pxds, addons, converters, out)


def run(pxds, addons, converters, out, extra_inc_dirs=None, extra_opts=None):

    manual_code = dict()
    cimports = []
    for name in addons:
        clz_name, __  = os.path.splitext(os.path.basename(name))
        line_iter = open(name, "r")
        for line in line_iter:
            if line and line[0] not in "\n\r\t ":
                cimports.append(line)
            else:
                break
        remainder = "".join(line_iter)
        manual_code.setdefault(clz_name, autowrap.Code.Code()).add(remainder)

    #manual_code = dict( (k, [v]) for (k,v) in extra_methods.items())

    from ConversionProvider import special_converters, TypeConverterBase

    sys.path.insert(0, ".")
    for conv_module in converters:
        mod_name = os.path.splitext(conv_module)[0].replace(os.sep, ".")
        if "__init__" in mod_name:
            continue
        try:
            mod = __import__(mod_name)
        except ImportError, e:
            raise ImportError(e.message +
                                     ", maybe __init__.py files are missing")

        for part in mod_name.split(".")[1:]:
            mod = getattr(mod, part)
        for name, obj in vars(mod).items():
            if hasattr(obj, "__mro__"):
                if obj != TypeConverterBase and TypeConverterBase in obj.__mro__:
                    try:
                        inst = obj()
                    except NotImplementedError:
                        # for abstract base classes
                        continue
                    special_converters.append(inst)

    inc_dirs = autowrap.parse_and_generate_code(pxds, ".", out, False,
                                                                manual_code,
                                                                cimports)
    if extra_inc_dirs is not None:
        inc_dirs += extra_inc_dirs

    from Cython.Compiler.Main import compile, CompilationOptions
    from Cython.Compiler.Options import directive_defaults
    directive_defaults["boundscheck"] = False
    directive_defaults["wraparound"] = False
    options = dict(include_path=inc_dirs,
                   compiler_directives=directive_defaults,
                   #output_dir=".",
                   #gdb_debug=True,
                   cplus=True)
    if extra_opts is not None:
        options.update(extra_opts)
    options = CompilationOptions(**options)

    compile(out, options=options)

    return inc_dirs
