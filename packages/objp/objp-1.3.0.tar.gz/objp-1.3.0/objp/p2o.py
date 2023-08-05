import re
import os.path as op
from .base import (tmpl_replace, OBJCTYPE2SPEC, copy_objp_unit, ArgSpec, MethodSpec, ClassSpec,
    get_objc_signature)

TEMPLATE_UNIT = """
#define PY_SSIZE_T_CLEAN
#import <Python.h>
#import "structmember.h"
#import "ObjP.h"

%%classes%%

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

static struct PyModuleDef %%modulename%%Def = {
    PyModuleDef_HEAD_INIT,
    "%%modulename%%",
    NULL,
    -1,
    module_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyObject *
PyInit_%%modulename%%(void)
{
    PyObject *m;
    m = PyModule_Create(&%%modulename%%Def);
    if (m == NULL) {
        return NULL;
    }
    
    %%clsaddtomod%%
    
    return m;
}

"""

TEMPLATE_CLASS = """
%%objcinterface%%

typedef struct {
    PyObject_HEAD
    %%typedecl%%objc_ref;
    unsigned char is_retained;
} %%clsname%%_Struct;

static PyTypeObject %%clsname%%_Type; /* Forward declaration */

/* Methods */

static void
%%clsname%%_dealloc(%%clsname%%_Struct *self)
{
    if (self->is_retained) {
        [self->objc_ref release];
    }
    Py_TYPE(self)->tp_free((PyObject *)self);
}

%%initfunc%%

%%methods%%

static PyMethodDef %%clsname%%_methods[] = {
 %%methodsdef%%
{NULL}  /* Sentinel */
};

static PyTypeObject %%clsname%%_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "%%modulename%%.%%clsname%%", /*tp_name*/
    sizeof(%%clsname%%_Struct), /*tp_basicsize*/
    0, /*tp_itemsize*/
    (destructor)%%clsname%%_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_reserved*/
    0, /*tp_repr*/
    0, /*tp_as_number*/
    0, /*tp_as_sequence*/
    0, /*tp_as_mapping*/
    0, /*tp_hash */
    0, /*tp_call*/
    0, /*tp_str*/
    0, /*tp_getattro*/
    0, /*tp_setattro*/
    0, /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "%%clsname%% object", /* tp_doc */
    0, /* tp_traverse */
    0, /* tp_clear */
    0, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    0, /* tp_iter */
    0, /* tp_iternext */
    %%clsname%%_methods,/* tp_methods */
    0, /* tp_members */
    0, /* tp_getset */
    0, /* tp_base */
    0, /* tp_dict */
    0, /* tp_descr_get */
    0, /* tp_descr_set */
    0, /* tp_dictoffset */
    (initproc)%%clsname%%_init,      /* tp_init */
    0, /* tp_alloc */
    0, /* tp_new */
    0, /* tp_free */
    0, /* tp_is_gcc */
    0, /* tp_bases */
    0, /* tp_mro */
    0, /* tp_cache */
    0, /* tp_subclasses */
    0  /* tp_weaklist */
};
"""

TEMPLATE_CLASS_ADD_TO_MOD = """
    %%clsname%%_Type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&%%clsname%%_Type) < 0) {
        return NULL;
    }
    Py_INCREF(&%%clsname%%_Type);
    PyModule_AddObject(m, "%%clsname%%", (PyObject *)&%%clsname%%_Type);
"""

TEMPLATE_TARGET_PROTOCOL = """
@protocol %%clsname%% <NSObject>
%%methods%%
@end
"""

TEMPLATE_TARGET_INTERFACE = """
@interface %%clsname%%: NSObject {}
%%methods%%
@end
"""

TEMPLATE_INITFUNC_CREATE = """
static int
%%clsname%%_init(%%clsname%%_Struct *self, PyObject *args, PyObject *kwds)
{
    PyObject *pRefCapsule = NULL;
    unsigned char should_retain = 1;
    if (!PyArg_ParseTuple(args, "|Ob", &pRefCapsule, &should_retain)) {
        return -1;
    }
    
    if (pRefCapsule == NULL) {
        self->objc_ref = %%objc_create%%
        self->is_retained = 1;
    }
    else {
        self->objc_ref = PyCapsule_GetPointer(pRefCapsule, NULL);
        self->is_retained = should_retain;
        if (should_retain) {
            [self->objc_ref retain];
        }
    }
    
    return 0;
}
"""

TEMPLATE_METHOD_NOARGS = """
static PyObject *
%%clsname%%_%%methname%%(%%clsname%%_Struct *self)
{
    PyThreadState *_save; _save = PyEval_SaveThread();
    %%retvalassign%%[self->objc_ref %%methname%%];
    PyEval_RestoreThread(_save);
    %%retvalreturn%%
}
"""

TEMPLATE_METHOD_VARARGS = """
static PyObject *
%%clsname%%_%%methname%%(%%clsname%%_Struct *self, PyObject *args)
{
    PyObject %%argliststar%%;
    if (!PyArg_ParseTuple(args, "%%argfmt%%", %%arglistamp%%)) {
        return NULL;
    }
    %%conversion%%
    
    PyThreadState *_save; _save = PyEval_SaveThread();
    %%retvalassign%%[self->objc_ref %%methcall%%];
    PyEval_RestoreThread(_save);
    %%retvalreturn%%
}
"""

TEMPLATE_METHODDEF = """
{"%%methname%%", (PyCFunction)%%clsname%%_%%methname%%, %%methtype%%, ""},
"""

def parse_objc_header(header):
    is_protocol = False
    re_class = re.compile(r"@interface\s+(\w*?)\s*:\s*\w*?.*?{.*?}(.*?)@end", re.MULTILINE | re.DOTALL)
    match = re_class.search(header)
    if match is None:
        re_protocol = re.compile(r"@protocol\s+(\w*).*?\n+(.*?)@end", re.MULTILINE | re.DOTALL)
        match = re_protocol.search(header)
        is_protocol = True
    assert match is not None
    clsname, methods = match.groups()
    re_method = re.compile(r"-\s*\(\s*([\w *]+?)\s*\)(.+?);")
    methods = re_method.findall(methods)
    method_specs = []
    re_method_elems = re.compile(r"(\w+)\s*:\s*\(\s*(\w+?\s*\*?)\s*\)\s*(\w+)")
    for resulttype, rest in methods:
        if resulttype == 'void':
            resulttype = None
        else:
            resulttype = OBJCTYPE2SPEC[resulttype]
        elems = re_method_elems.findall(rest)
        args = []
        if not elems: # no arguments
            name = rest
        else:
            name = ':'.join(elem[0] for elem in elems)
            if not name.endswith(':'):
                name += ':'
            for elem in elems:
                argname = elem[2]
                argtype = OBJCTYPE2SPEC[elem[1]]
                args.append(ArgSpec(argname, argtype))
        pyname = name.replace(':', '_')
        method_specs.append(MethodSpec(pyname, name, args, resulttype, False))
    return ClassSpec(clsname, '', method_specs, is_protocol, [])

def generate_objc_header(clsspec):
    clsname = clsspec.clsname
    signatures = ['- %s;' % get_objc_signature(methodspec) for methodspec in clsspec.methodspecs]
    template = TEMPLATE_TARGET_PROTOCOL if clsspec.is_protocol else TEMPLATE_TARGET_INTERFACE
    return tmpl_replace(template, clsname=clsname, methods='\n'.join(signatures))

def generate_class_code(clsspec):
    objcinterface = generate_objc_header(clsspec)
    clsname = clsspec.clsname
    if clsspec.is_protocol:
        tmpl_objc_create = "NULL; // Never supposed to happen"
    else:
        tmpl_objc_create = "[[%s alloc] init];" % clsname
    tmpl_initfunc = tmpl_replace(TEMPLATE_INITFUNC_CREATE, clsname=clsname,
        objc_create=tmpl_objc_create)
    tmpl_methods = []
    tmpl_methodsdef = []
    for pyname, objcname, args, resulttype, is_inherited in clsspec.methodspecs:
        if pyname == '__init__':
            continue
        tmplval = {}
        tmplval['methname'] = pyname
        if resulttype is None:
            tmplval['retvalassign'] = ''
            tmplval['retvalreturn'] = 'Py_RETURN_NONE;'
        else:
            tmplval['retvalassign'] = '%s retval = ' % resulttype.objctype
            fmt = 'PyObject *pResult = %s; return pResult;'
            tmplval['retvalreturn'] = fmt % (resulttype.o2p_code % 'retval')
        if args:
            argnames = [arg.argname for arg in args]
            tmplval['methtype'] = 'METH_VARARGS'
            tmplval['argliststar'] = ', '.join('*p'+name for name in argnames)
            tmplval['arglistamp'] = ', '.join('&p'+name for name in argnames)
            tmplval['argfmt'] = 'O' * len(args)
            conversion = []
            for arg in args:
                name = arg.argname
                ts = arg.typespec
                conversion.append('%s %s = %s;' % (ts.objctype, name, ts.p2o_code % ('p'+name)))
            tmplval['conversion'] = '\n'.join(conversion)
            elems = objcname.split(':')
            elems_and_args = [elem + ':' + argname for elem, (argname, _) in zip(elems, args)]
            tmplval['methcall'] = ' '.join(elems_and_args)
            tmpl_methods.append(tmpl_replace(TEMPLATE_METHOD_VARARGS, clsname=clsname, **tmplval))
        else:
            tmplval['methtype'] = 'METH_NOARGS'
            tmpl_methods.append(tmpl_replace(TEMPLATE_METHOD_NOARGS, clsname=clsname, **tmplval))
        tmpl_methodsdef.append(tmpl_replace(TEMPLATE_METHODDEF, clsname=clsname, **tmplval))
    tmpl_methods = ''.join(tmpl_methods)
    tmpl_methodsdef = ''.join(tmpl_methodsdef)
    typedecl = "id <%s>" % clsname if clsspec.is_protocol else "%s *" % clsname
    return tmpl_replace(TEMPLATE_CLASS, clsname=clsname, typedecl=typedecl,
        objcinterface=objcinterface, initfunc=tmpl_initfunc, methods=tmpl_methods,
        methodsdef=tmpl_methodsdef)

def generate_add_to_module_code(clsspec):
    return tmpl_replace(TEMPLATE_CLASS_ADD_TO_MOD, clsname=clsspec.clsname)

def generate_python_proxy_code_from_clsspec(clsspecs, destpath):
    if not isinstance(clsspecs, (list, tuple)):
        clsspecs = [clsspecs]
    clscode = []
    clsaddtomodcode = []
    for clsspec in clsspecs:
        clscode.append(generate_class_code(clsspec))
        clsaddtomodcode.append(generate_add_to_module_code(clsspec))
    modulename = op.splitext(op.basename(destpath))[0]
    result = tmpl_replace(TEMPLATE_UNIT, classes='\n'.join(clscode), modulename=modulename,
        clsaddtomod='\n'.join(clsaddtomodcode))
    copy_objp_unit(op.dirname(destpath))
    with open(destpath, 'wt') as fp:
        fp.write(result)

def generate_python_proxy_code(header_paths, destpath):
    # The name of the file in destpath will determine the name of the module. For example,
    # "foo/bar.m" will result in a module name "bar".
    if not isinstance(header_paths, (list, tuple)):
        header_paths = [header_paths]
    clsspecs = []
    for header_path in header_paths:
        with open(header_path, 'rt') as fp:
            header = fp.read()
        clsspecs.append(parse_objc_header(header))
    generate_python_proxy_code_from_clsspec(clsspecs, destpath)
    
