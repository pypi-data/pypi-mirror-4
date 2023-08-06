supertools
==========

A simple python 2 decorator that provide ``.__super`` member to python2 classes as private static member 
in order to not have to specify the current class name.

Without super nor supertools::

    class MyClass(MyParent) :
        def __init__(self) :
            MyParent.__init__(self)

Classical implementation using super (python 2 syntax)::

    class MyClass(MyParent) :
        def __init__(self) :
            super(MyClass,self).__init__()

Using supertools::

    from supertools import superable

    @superable
    class MyClass(MyParent) :
        def __init__(self) :
            self.__super.__init__()

Syntax is nice, dosn't repeat neither classname nor parent classname, and doesn't parse callstack at runtime like
other similar modules does.

Note that this syntax is however not compatible with python 3 syntax, which would be in this case::

    class MyClass(MyParent) :
        def __init__(self) :
            super().__init__()


