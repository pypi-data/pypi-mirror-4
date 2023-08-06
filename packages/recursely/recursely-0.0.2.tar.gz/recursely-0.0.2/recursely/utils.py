"""
Utility module.
"""
import functools


class SentinelList(list):
    """Modified version of standard :class:`list` that always has a `sentinel`
    element at the end, regardless of whatever modifications we perform on it.
    """
    def __init__(self, iterable, **kwargs):
        """Constructor.

        Sentinel should be provided as keyword argument ``sentinel``.
        Other than that, the constructor works the same way as in :class:`list`.
        """
        try:
            sentinel = kwargs['sentinel']
        except KeyError:
            raise TypeError("sentinel expected")

        iterable = list(iterable) + [sentinel]
        super(SentinelList, self).__init__(iterable)

    class __metaclass__(type):
        """Metaclass for batch redefinition of all relevant list operations."""

        OPERATORS = ('__delitem__', '__delslice__', '__iadd__', '__imul__',
                     '__setitem__', '__setslice__')
        METHODS = ('append', 'extend', 'insert', 'pop',
                   'remove', 'reverse', 'sort')

        def __new__(cls, name, bases, dict_):
            """Redefines all state-altering operations to preserve sentinel
            and creates the resulting :class:`list` subclass.
            """
            for op in cls.OPERATORS + cls.METHODS:
                dict_[op] = cls.with_preserved_sentinel(op)
            return type.__new__(cls, name, bases, dict_)

        @classmethod
        def with_preserved_sentinel(cls, op):
            """For given :class:`list` operation ``op``, returns a function
            encapsulating it within a code that preserves the sentinel element
            at the end of list.
            """
            def wrapper(self, *args, **kwargs):
                super_ = super(SentinelList, self)

                sentinel = super_.pop()
                try:
                    return getattr(super_, op)(*args, **kwargs)
                finally:
                    super_.append(sentinel)

            # original methods of ``list`` don't have ``__module__`` attribute,
            # so we need to use ``update_wrapper`` instead of typical ``wraps``
            functools.update_wrapper(wrapper, wrapped=getattr(list, op),
                                     assigned=('__name__', '__doc__'))
            return wrapper
