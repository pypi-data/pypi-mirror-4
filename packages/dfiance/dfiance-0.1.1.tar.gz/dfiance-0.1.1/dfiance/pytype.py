from base import Invalid
from mapping import Mapping

class PyType(Mapping):
    '''Dictifier for python objects with constructor functions.

    This is a Mapping-based dictifier for objects that are described by a small
    number of attributes.

    The field_types arg specifies the types of the attributes of the objects you
    want to be able to dictify/undictify. These fields must all be exposed attrs
    of any instance you wish to dictify.

    The cls arg specifies the type of object you want to create.

    The ctor arg specifies a function that takes as keyword arguments the values
    named by the field_types argument. If ctor isn't provided, it defaults to
    the cls constructor.

    For example, suppose you're using the MailMessage class from above:

    >>> class MailMessage(object):
    ...     def __init__(self, subject, sender, body=None):
    ...         self.body, self.subject, self.sender = body, subject, sender

    You could build a dictifier for it much like

    >>> from basic import String
    >>> msg_dfier = PyType(
    ...     field_types = dict(
    ...         body = String(),
    ...         sender = String(),
    ...         subject = String()),
    ...     cls = MailMessage)

    And now msg_dfier can dictify/undictify MailMessages:

    >>> m = MailMessage("Business", "sender@foo.net")
    >>> data = msg_dfier.dictify(m)
    >>> sorted(data.items())
    [('body', None), ('sender', 'sender@foo.net'), ('subject', 'Business')]
    >>> m2 = msg_dfier.undictify(data)
    >>> isinstance(m2, MailMessage)
    True
    >>> (m2.body, m2.subject, m2.sender) == (m.body, m.subject, m.sender)
    True
    >>> msg_dfier.validate(m2)
    >>> msg_dfier.validate("not a message")
    Traceback (most recent call last):
    ...
    Invalid: type_error
    '''
    def __init__(self, field_types, cls, ctor=None, extra_field_policy='ignore'):
        super(PyType, self).__init__(field_types, extra_field_policy)
        self.cls = cls
        self.ctor = ctor or cls

    def undictify(self, value, **kwargs):
        '''Use the Schema machinery, then extract to a new object.'''
        mapping = super(PyType, self).undictify(value, **kwargs)
        return self.ctor(**mapping)

    def _obj_to_mapping(self, obj):
        mapping = {}
        for key in self.field_types:
            mapping[key] = getattr(obj, key)
        return mapping

    def dictify(self, value, **kwargs):
        mapping = self._obj_to_mapping(value)
        return super(PyType, self).dictify(mapping, **kwargs)

    def validate(self, value, **kwargs):
        if not isinstance(value, self.cls):
            raise Invalid('type_error')
        mapping = self._obj_to_mapping(value)
        super(PyType, self).validate(mapping, **kwargs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
