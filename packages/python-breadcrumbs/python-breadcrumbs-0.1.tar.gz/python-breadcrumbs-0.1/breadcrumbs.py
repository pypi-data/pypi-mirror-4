""" Python breacrumbs match the need for delayed usage of class instance
attributes.

People using the asynchronous programming pattern, mostly, often face
situations where a deferred call will need to access a specific attribute
of an object that is not yet instanciated. The default approach is to pass
the attribute name along with the deferred call.
This happens for attributes, but also for method calls, index access, etc.
Python breadcrumbs provides an elegant way of storing such information as
deferred attribute access, method call, list slicing, etc.

A simple use case::

   import breadcrumbs
   from breadcrumbs import root as self

   [...]

   deferred_access = self.foobar().foo["bar"]

   [...]

   # value = obj.foobar().foo["bar"]
   value = breadcrumbs.collapse(deferred_access, obj)
"""


class Breadcrumb(object):
    """ Breadcrumb object that store the deferred access data.

    :param parent: Parent breadcrumb.
    """

    def __init__(self, parent=None, function=lambda x: x, *args, **kwargs):
        self.__parent = parent
        self.__function = function
        self.__args = args
        self.__kwargs = kwargs

    def __apply(self, obj):
        """ Apply the breadcrumb.
        """
        return self.__function(obj, *self.__args, **self.__kwargs)

    def __getattr__(self, attr):
        return Breadcrumb(self, getattr, attr)

    def __getitem__(self, item):
        return Breadcrumb(self, getitem, item)

    def __call__(self, *args, **kwargs):
        return Breadcrumb(self, call, *args, **kwargs)


def collapse(breadcrumbs, obj):
    """ Does the recursive work to collapse a breadcrumb.
    """
    if breadcrumbs.__dict__['_Breadcrumb__parent']:
        obj = collapse(breadcrumbs.__dict__['_Breadcrumb__parent'], obj)
    return Breadcrumb._Breadcrumb__apply(breadcrumbs, obj)


def getitem(obj, item):
    """ Implement the getitem behavior.
    """
    return obj[item]


def call(obj, *args, **kwargs):
    """ Implement the call behavior.
    """
    return obj(*args, **kwargs)


root = Breadcrumb()
