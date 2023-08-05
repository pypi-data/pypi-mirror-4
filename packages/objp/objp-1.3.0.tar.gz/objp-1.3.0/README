ObjP's goal is to create a two-way bridge between Python and Objective-C. Unlike PyObjC, which uses
dynamic calls to methods on runtime, ObjP generates static code. It generates either Objective-C
interfaces to Python code or Python modules to interface Objective-C code.

The library is exceedingly simple and it's intended that way. Unlike PyObjC, there's no way ObjP
could possibly wrap the whole Cocoa framework, there's way too many things to support. ObjP is made
to allow you to bridge your own code.

Also note that ObjP works on Python 3.2 and up.

The best way to learn how to use ObjP is, I think, to look at an example. There are many of them in
the 'demos' subfolder. These are built using ``waf`` (it's already included in here, no need to
install it). For example, if you want to build the ``simple`` demo, do::

    $ cd demos/simple
    $ ./waf configure build
    $ cd build
    $ ./HelloWorld

That programs calls a simple Python script from Objective-C, and that python script itself calls
an Objective-C class.

Usage
-----

There are two types of bridge: Objective-C class wrapping a Python class (o2p) and Python class
wrapping an Objective-C class (p2o).

To generate an o2p wrapper, you need a target class. Moreover, for this class' methods to be
wrapped, you need to have its arguments and return value correctly annotated (You can browse the
demos for good examples of how to do it). This is an example of a correctly annotated class::

    class Foo:
        def hello_(self, name: str) -> str:
            return "Hello {}".format(name)

To wrap this class, you'll use ``objp.o2p.generate_objc_code()`` in this fashion::

    import foo
    import objp.o2p
    objp.o2p.generate_objc_code(foo.Foo, 'destfolder')

This will generate "Foo.h|m" as well as "ObjP.h|m" in "destfolder". These source files directly
use the Python API and have no other dependencies.

To generate a p2o wrapper, you either need an Objective-C header file containing an interface or
protocol or a Python class describing that interface::

    @interface Foo: NSObject {}
    - (NSString *)hello:(NSString *)name;
    @end

To generate a python wrapper from this, you can do::

    import objp.p2o
    objp.p2o.generate_python_proxy_code(['Foo.h'], 'destfolder/Foo.m')

This will generate the code for a Python extension module wrapping ``Foo``. The name of the
extension module is determined by the name of the destination source file. You can wrap more than
one class in the same unit::

    objp.p2o.generate_python_proxy_code(['Foo.h', 'Bar.h'], 'destfolder/mywrappers.m')

Method name conversion
----------------------

ObjP follows PyObjC's convention for converting method names. The ":" character being illegal in
Python method names, they're replaced by underscores. Thus, a method
``- (BOOL)foo:(NSInteger)arg1 bar:(NSString *)arg2;`` is converted to
``def foo_bar_(self, arg1: int, arg2: str) -> bool:`` and vice versa.

Note that if your method's argument count doesn't correspond to the number of underscores in your
method name, objp will issue a warning and ignore the method.

Argument Types
--------------

Only a few argument types are supported by ObjP, the goal being to keep the project simple.

* ``int/NSInteger``
* ``float/CGFloat``
* ``str/NSString*``
* ``bool/BOOL``
* ``list/NSArray*``
* ``dict/NSDictionary*``
* ``nspoint/NSPoint``
* ``nssize/NSSize``
* ``nsrect/NSRect``

ObjP also supports ``object`` which dynamically converts the argument depending on its type and
returns an ``NSObject`` subclass (which means that ``int``, ``float`` and ``bool`` convert to
``NSNumber`` instead of converting to ``NSInteger``, ``CGFloat`` and ``BOOL``). This type of
conversion is used to convert the contents of ``list`` and ``dict`` (it's impossible to have an
NSArray directly containing ``BOOL``).

Another special argument type is ``pyref`` (which you must import from ``objp.util`` in your code)
which simply passes the ``PyObject*`` instance around without converting it.

The structure arguments allow you to transform tuples to native objc structures and vice-versa.
Python has no "native" structure for points, sizes and rects, so that's why we convert to/from
tuples (``(x, y)``, ``(w, h)`` and ``(x, y, w, h)``). Like ``pyref``, the ``ns*`` signature
arguments have to be imported from ``objp.util``.

Utilities
---------

``objp.util`` contains the ``pyref`` and ``ns*`` argument types, but it also contains two useful
method decorators: ``dontwrap`` and ``objcname``. A method decorated with ``dontwrap`` will be
ignored by the code generator, and a method decorated with ``@objcname('some:selector:')`` will use
this name for generating objc code instead of the automatically generated name.

Constant conversion
-------------------

When having code in two different languages, we sometimes have to share constants in between the
two. To avoid having to manually maintain an Objective-C counterpart to your Python constants,
``objp`` offers a small utility, ``objp.const.generate_objc_code(module, dest)``. This takes all
elements in ``module``'s namespace and convert them to an Objective-C's constant unit at ``dest``.

``int``, ``float`` and ``str`` types are going to be converted to ``#define <name> <str(value)>``
(with ``@""`` around ``str`` values). You can also have enum classes in your python constant
module. A class is considered an enum if it has integer members. For example::

    class Foo:
        Bar = 1
        Baz = 2

will be converted to::

    typedef enum {
        FooBar=1,
        FooBaz=2
    } Foo;

Because this function will choke on any value that it can't convert, it is recommended that you use
it on modules specifically written for that, for example a ``cocoa_const.py`` that imports from
your real const unit. Since constants in Objective-C often have prefixes, you can also add them in
that unit. It could look like that::

    from real_const import FOO as XZFOO, BAR as XZBAR, MyEnum as XZMyEnum
