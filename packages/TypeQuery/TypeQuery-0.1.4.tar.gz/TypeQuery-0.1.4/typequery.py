# Copyright (c) 2011 Hong Minhee <http://dahlia.kr/>
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
""":mod:`typequery` --- Generic methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module offers a simple and dirty way to define generic methods to
existing types.

"""
import sys

__copyright__ = 'Copyright 2012, Hong Minhee'
__license__ = 'MIT License'
__author__ = 'Hong Minhee'
__email__ = 'minhee' '@' 'dahlia.kr'
__version__ = '0.1.4'


if sys.version_info < (2, 6, 0):
    # Python 2.5:
    # ABC (abstract base classes) were introduced since Python 2.6.
    # So we don't care in Python 2.5.
    # See PEP 3119 -- http://www.python.org/dev/peps/pep-3119/
    def is_abc(cls):
        return False
elif hasattr(sys, 'pypy_version_info'):
    # PyPy:
    # PyPy metaclasses share the same reference to __subclasscheck__.im_func
    # function object until these are explicitly overridden.
    def is_abc(cls):
        return (type(cls).__subclasscheck__.im_func is not
                type.__subclasscheck__.im_func)
elif hasattr(sys, 'JYTHON_JAR'):
    # Jython 2.7a1:
    # Jython metaclasses don't have __subclasscheck__ method until these
    # are explicitly overridden.
    def is_abc(cls):
        return hasattr(type(cls), '__subclasscheck__')
elif (2, 6, 0) <= sys.version_info < (2, 7, 0):
    # CPython 2.6 (probably):
    # CPython 2.6+ metaclasses (other than built-in types.TypeType)
    # expose '__subclasscheck__' key through its __dict__ attribute
    # only if these explictly override __subclasscheck__ method.
    def is_abc(cls):
        return (type(cls) is not type and
                '__subclasscheck__' in type(cls).__dict__)
else:
    # CPython 2.7+ (probably):
    # CPython 2.7+ metaclasses share the same reference to __subclasscheck__
    # method object until these are explicitly overridden.
    def is_abc(cls):
        return type(cls).__subclasscheck__ is not type.__subclasscheck__


class GenericMethod(object):
    """Generic method object.

    .. sourcecode:: pycon

       >>> compile = GenericMethod('compile')
       >>> compile  # doctest: +ELLIPSIS
       <typequery.GenericMethod 'compile' at ...>
       >>> compile.__name__
       'compile'

    :param name: the name of the generic method
    :param base: inherits other generic method.
                 ``None`` by default

    .. attribute:: __name__

       The name of the the generic method.

    """

    #: Registered functions by types in :class:`dict`.
    functions = None

    def __init__(self, name, base=None):
        self.__name__ = name
        self.base = base
        self.functions = {}
        self.abcs = {}
        self.abc_cache = {}
        self.latest_added_function = None

    def of(self, cls, with_receiver=False):
        """Returns a decorator to register a function.

        .. sourcecode:: pycon

           >>> compile = GenericMethod('compile')
           >>> @compile.of(int)
           ... @compile.of(float)
           ... def compile(value):
           ...     return 'number: ' + str(value)
           ...

        :param type: the type to define or override the method
        :type type: :class:`type <types.TypeType>`
        :param receiver: whether function takes a receiver
                         (:class:`GenericMethod` instance)
                         as its first argument
        :type receiver: :class:`bool`
        :returns: a :class:`Decorator` instance
        :rtype: :class:`Decorator`

        """
        return Decorator(self, cls, with_receiver=with_receiver)

    def clone(self, name):
        """Makes a clone of the generic method.  It is useful for
        register other types without chaning the original method.

        :param name: the name of the cloned generic method
        :returns: the cloned generic method
        :rtype: :class:`GenericMethod`

        """
        method = type(self)(name)
        method.functions = self.functions.copy()
        method.abcs = self.abcs.copy()
        return method

    def inherit(self, name):
        """Makes a generic method which inherits this.  It's similar to
        :meth:`clone()` except it reflects base method's runtime changes.

        :param name: the name of the inheriting method
        :returns: the inheriting method
        :rtype: :class:`GenericMethod`

        """
        return type(self)(name, base=self)

    def __contains__(self, cls):
        if isinstance(cls, type):
            for cls in cls.mro():
                if cls in self.functions:
                    return True
        return (cls in self.functions or
                self.base is not None and cls in self.base)

    def __getitem__(self, cls):
        funcs = self.functions
        if isinstance(cls, type):
            try:
                return self.abc_cache[cls]
            except KeyError:
                pass
            for subcls in cls.mro():
                try:
                    abcs = self.abcs[subcls]
                except KeyError:
                    pass
                else:
                    for abc in abcs:
                        if issubclass(cls, abc):
                            func = funcs[abc]
                            self.abc_cache[cls] = func
                            return func
                try:
                    return funcs[subcls]
                except KeyError:
                    pass
        try:
            return funcs[cls]
        except KeyError:
            if self.base is None:
                raise
        return self.base[cls]

    def __setitem__(self, cls, function):
        self.functions[cls] = function
        self.latest_added_function = function
        self.abc_cache = {}
        if is_abc(cls):
            abcs = self.abcs
            for subcls in cls.mro()[1:]:
                bases = abcs.setdefault(subcls, [])
                for i, base in enumerate(bases):
                    if issubclass(cls, base):
                        bases.insert(i, cls)
                        break
                else:
                    bases.append(cls)

    def __call__(self, *args, **kwargs):
        try:
            with_receiver, f = self[type(args[0])]
        except KeyError:
            raise TypeError(repr(args[0]) + ' does not match for the function '
                                          + repr(self.__name__))
        if with_receiver:
            return f(self, *args, **kwargs)
        return f(*args, **kwargs)

    def __repr__(self):
        return ('<' + __name__ + '.' + type(self).__name__ + ' ' +
                repr(self.__name__) + ' at ' + hex(id(self)) + '>')


class Decorator(object):
    """Decorator function object to register a function to :class:`Visitor`.
    Internally used.

    :param generic_method: a :class:`GenericMethod` instance
    :type generic_method: :class:`GenericMethod`
    :param cls: a class object
    :type cls: :class:`type <types.TypeType>`
    :param receiver: whether function takes a receiver
                     (:class:`GenericMethod` instance)
                     as its first argument
    :type receiver: :class:`bool`

    """

    __slots__ = 'generic_method', 'cls', 'with_receiver'

    def __init__(self, generic_method, cls, with_receiver):
        if not isinstance(generic_method, GenericMethod):
            raise TypeError('visitor must be a ' + __name__ + '.GenericMethod'
                            'instance, not ' + repr(generic_method))
        elif not isinstance(cls, type):
            raise TypeError('type must be a types.TypeType instance, not ' +
                            repr(cls))
        self.generic_method = generic_method
        self.cls = cls
        self.with_receiver = bool(with_receiver)

    def __call__(self, function):
        generic_method = self.generic_method
        if function is generic_method:
            function = generic_method.latest_added_function[1]
        generic_method[self.cls] = self.with_receiver, function
        return generic_method


class GenericClassMethod(GenericMethod):
    """Same as :class:`GenericMethod` except it deals with classes
    instead of instance.

    .. sourcecode:: pycon

       >>> compile = GenericClassMethod('compile')
       >>> compile  # doctest: +ELLIPSIS
       <typequery.GenericClassMethod 'compile' at ...>
       >>> compile.__name__
       'compile'

    """

    def __call__(self, *args, **kwargs):
        try:
            with_receiver, f = self[args[0]]
        except KeyError:
            raise TypeError(repr(args[0]) + ' does not match for the function '
                                          + repr(self.__name__))
        if with_receiver:
            return f(self, *args, **kwargs)
        return f(*args, **kwargs)
