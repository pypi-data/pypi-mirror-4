import os.path as op
import inspect

from .base import (PYTYPE2SPEC, tmpl_replace, copy_objp_unit, ArgSpec, MethodSpec, ClassSpec,
    get_objc_signature)

TEMPLATE_HEADER = """
#import <Cocoa/Cocoa.h>
#import <Python.h>
%%imports%%

@interface %%classname%%:NSObject %%protocols%%
{
    PyObject *_py;
}
- (PyObject *)pyRef;
%%methods%%
@end
"""

TEMPLATE_HEADER_INHERITED = """
#import <Cocoa/Cocoa.h>
#import <Python.h>
%%imports%%

@interface %%classname%%:%%superclass%% %%protocols%% {}
%%methods%%
@end
"""

TEMPLATE_UNIT = """
#import "%%classname%%.h"
#import "ObjP.h"

@implementation %%classname%%
- (void)dealloc
{
    OBJP_LOCKGIL;
    Py_DECREF(_py);
    OBJP_UNLOCKGIL;
    [super dealloc];
}

- (PyObject *)pyRef
{
    return _py;
}

%%methods%%
@end
"""

TEMPLATE_UNIT_INHERITED = """
#import "%%classname%%.h"
#import "ObjP.h"

@implementation %%classname%%
%%methods%%
@end
"""

TEMPLATE_INIT_METHOD = """
- %%signature%%
{
    self = [super init];
    OBJP_LOCKGIL;
    PyObject *pFunc = ObjP_findPythonClass(@"%%classname%%", nil);
    %%funccall%%
    _py = pResult;
    OBJP_UNLOCKGIL;
    return self;
}
"""

TEMPLATE_METHOD = """
- %%signature%%
{
    OBJP_LOCKGIL;
    PyObject *pFunc = PyObject_GetAttrString(_py, "%%pyname%%");
    OBJP_ERRCHECK(pFunc);
    %%funccall%%
    %%returncode%%
}
"""

TEMPLATE_FUNCCALL = """
%%argscreate%%
    PyObject *pResult = PyObject_CallFunctionObjArgs(pFunc, %%argslist%%);
%%argsdecref%%
    OBJP_ERRCHECK(pResult);
    Py_DECREF(pFunc);
"""

TEMPLATE_RETURN_VOID = """
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;
"""

TEMPLATE_RETURN = """
    %%type%% result = %%pyconversion%%;
    Py_DECREF(pResult);
    OBJP_UNLOCKGIL;
    return result;
"""

def camelcase(s):
    elems = s.split('_')
    elems = [elems[0]] + [e.title() for e in elems[1:]]
    return ''.join(elems)

def internalize_argspec(name, argspec, is_inherited):
    # take argspec from the inspect module and returns MethodSpec
    args = argspec.args[1:] # remove self
    ann = argspec.annotations
    assert all(arg in ann for arg in args)
    assert all(argtype in PYTYPE2SPEC for argtype in ann.values())
    argspecs = []
    for arg in args:
        ts = PYTYPE2SPEC[ann[arg]]
        argspecs.append(ArgSpec(arg, ts))
    if name == '__init__':
        # generate objcname from args and always have an object return type
        returntype = PYTYPE2SPEC[object]
        if argspecs:
            argnames = [camelcase(arg.argname) for arg in argspecs]
            argnames[0] = argnames[0].title()
            objcname = 'initWith' + ':'.join(argnames) + ':'
        else:
            objcname = 'init'
    else:
        if 'return' in ann:
            returntype = PYTYPE2SPEC[ann['return']]
        else:
            returntype = None
        objcname = name.replace('_', ':')
    return MethodSpec(name, objcname, argspecs, returntype, is_inherited)

def get_arg_c_code(argspecs):
    result = []
    for arg in argspecs:
        result.append(arg.typespec.o2p_code % arg.argname)
    result.append('NULL') # We have to add a NULL item in va_args in PyObject_CallMethodObjArgs
    return ', '.join(result)

def get_objc_method_code(clsspec, methodspec):
    signature = get_objc_signature(methodspec)
    argspecs = methodspec.argspecs
    fmt = '    PyObject *p%s = %s;'
    tmpl_argscreate = '\n'.join([fmt % (arg.argname, arg.typespec.o2p_code % arg.argname) for arg in argspecs])
    tmpl_argslist = ', '.join(['p' + arg.argname for arg in argspecs] + ['NULL'])
    fmt = '    Py_DECREF(p%s);'
    tmpl_argsdecref = '\n'.join([fmt % (arg.argname) for arg in argspecs])
    tmpl_funccall = tmpl_replace(TEMPLATE_FUNCCALL, argscreate=tmpl_argscreate,
        argslist=tmpl_argslist, argsdecref=tmpl_argsdecref)
    if methodspec.returntype is not None:
        ts = methodspec.returntype
        tmpl_pyconversion = ts.p2o_code % 'pResult'
        returncode = tmpl_replace(TEMPLATE_RETURN, type=ts.objctype, pyconversion=tmpl_pyconversion)
    else:
        returncode = TEMPLATE_RETURN_VOID
    if methodspec.pyname == '__init__':
        code = tmpl_replace(TEMPLATE_INIT_METHOD, signature=signature, classname=clsspec.clsname,
            funccall=tmpl_funccall)
    else:
        code = tmpl_replace(TEMPLATE_METHOD, signature=signature, pyname=methodspec.pyname,
            funccall=tmpl_funccall, returncode=returncode)
    sig = '- %s;' % signature
    return (code, sig)

def spec_from_python_class(class_):
    methods = inspect.getmembers(class_, inspect.isfunction)
    methodspecs = []
    for name, meth in methods:
        if getattr(meth, 'dontwrap', False):
            continue
        argspec = inspect.getfullargspec(meth)
        is_inherited = name not in class_.__dict__
        try:
            if hasattr(meth, 'objcname'):
                name = meth.objcname
            methodspec = internalize_argspec(name, argspec, is_inherited)
            methodspecs.append(methodspec)
        except AssertionError:
            print("Warning: Couldn't generate spec for %s" % name)
            continue
    if not any(ms.pyname == '__init__' for ms in methodspecs):
        # Always create a default init method.
        methodspecs.insert(0, MethodSpec('__init__', 'init', [], PYTYPE2SPEC[object], True))
    follow_protocols = getattr(class_, 'FOLLOW_PROTOCOLS', [])
    superclass = class_.__bases__[0].__name__ if class_.__bases__[0] is not object else None
    return ClassSpec(class_.__name__, superclass, methodspecs, True, follow_protocols)

def generate_objc_code(class_, destfolder, inherit=False):
    clsspec = spec_from_python_class(class_)
    clsname = clsspec.clsname
    method_code = []
    method_sigs = []
    for methodspec in clsspec.methodspecs:
        if inherit and methodspec.is_inherited and methodspec.pyname != '__init__':
            continue
        try:
            code, sig = get_objc_method_code(clsspec, methodspec)
        except AssertionError:
            print("Warning: Couldn't generate code for %s" % methodspec.pyname)
            continue
        method_code.append(code)
        method_sigs.append(sig)
    if clsspec.follow_protocols:
        tmpl_imports = '\n'.join('#import "%s.h"' % imp for imp in clsspec.follow_protocols)
        tmpl_protocols = '<%s>' % ','.join(clsspec.follow_protocols)
    else:
        tmpl_protocols = ''
        tmpl_imports = ''
    if inherit and clsspec.superclass:
        tmpl_superclass = clsspec.superclass
        tmpl_imports += '\n#import "%s.h"' % clsspec.superclass
        header = tmpl_replace(TEMPLATE_HEADER_INHERITED, classname=clsname, methods='\n'.join(method_sigs),
            imports=tmpl_imports, protocols=tmpl_protocols, superclass=tmpl_superclass)
        implementation = tmpl_replace(TEMPLATE_UNIT_INHERITED, classname=clsname, methods=''.join(method_code))
    else:
        header = tmpl_replace(TEMPLATE_HEADER, classname=clsname, methods='\n'.join(method_sigs),
                imports=tmpl_imports, protocols=tmpl_protocols)
        implementation = tmpl_replace(TEMPLATE_UNIT, classname=clsname, methods=''.join(method_code))
    copy_objp_unit(destfolder)
    with open(op.join(destfolder, '%s.h' % clsname), 'wt') as fp:
        fp.write(header)
    with open(op.join(destfolder, '%s.m' % clsname), 'wt') as fp:
        fp.write(implementation)
