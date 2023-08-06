'''subclass.py: metaclass for programmatically subclassable classes.

Subclasses of the Subclassable class have classmethods called subclass(**kwargs)
and __subclass__(**kwargs).

Whenever such a class is subclassed, the __subclass__() method is called and
passed the contents of the new class's dictionary.

cls.subclass(**kwargs) is equivalent to creating a new subclass with the
contents of kwargs written out within it.

For example:

>>> class Point(Subclassable):
...   round = False
...   def __init__(self, x, y):
...     if self.round:
...        x, y = int(x), int(y)
...     self.x, self.y = x, y
...
>>> p = Point(.5, 3.25)
>>> p.x, p.y
(0.5, 3.25)

The following two subclasses are (nearly) equivalent

>>> class IntPoint1(Point):
...   round = True
...
>>> IntPoint2 = Point.subclass(round=True)
>>> p1 = IntPoint1(.5, 3.25)
>>> p2 = IntPoint2(.5, 3.25)
>>> p1.x, p1.y
(0, 3)
>>> p2.x, p2.y
(0, 3)

The only difference is in their names:

>>> IntPoint1.__name__
'IntPoint1'
>>> IntPoint2.__name__
'Point_sub'

This can be rectified via the special __class_name attribute:

>>> IntPoint3 = Point.subclass(round=True, __class_name="IntPoint1")
>>> IntPoint3.__name__
'IntPoint1'

'''


class SubclassableMeta(type):
    '''Metaclass for classes that can easily programmatically subclass.'''
    def __new__(cls, name, supers, kwargs):
        t = type.__new__(cls, name, supers, {})
        # Force __subclass__ to be a classmethod
        if not isinstance(t.__subclass__, classmethod):
            t.__subclass__ = classmethod(t.__subclass__.im_func)
        t.__subclass__(**kwargs)
        return t

    def __subclass__(cls, **kwargs):
        for name, val in kwargs.items():
            setattr(cls, name, val)

    def subclass(cls, **kwargs):
        '''
        Programmatically generate subclasses of this class.

        The generated subclass will be called <name of this class>_sub unless
        the special parameter __class_name is passed in.
        '''
        if '__class_name' in kwargs:
            class_name = kwargs.pop('__class_name')
        else:
            class_name = cls.__name__ + "_sub"
        subcls = type(class_name, (cls,), kwargs)
        return subcls



class Subclassable(object):
    '''Base class for programmatically subclassable types.'''
    __metaclass__ = SubclassableMeta

if __name__ == '__main__':
    import doctest
    doctest.testmod()
