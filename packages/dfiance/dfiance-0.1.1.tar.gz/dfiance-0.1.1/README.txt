==========================================================
 Dfiance: Partial Serialization and Validation for Python
==========================================================

Dfiance is a tool for building serializers, deserializers, and validators for
python types.

Dfiance does not fully serialize things, because you deserve control over the
format of the data you pass around. Instead, it serializes python objects into
'dictified' objects, which are either basic types - strings, ints, floats, and
bools - or lists/dictionaries whose keys and values are all dictified objects.

The resulting objects are trivially serializable in JSON, YAML, XML, or pretty
much any other serialization protocol you like.

At the moment the majority of the documentation is embedded in the code. You can
browse it on github at <https://github.com/dplepage/dfiance>.