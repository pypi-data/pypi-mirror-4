Confetti
--------
Confetti is a Python library for dealing with hierarchical configuration data.


Updating Paths
==============

Setting paths is done by settings items::

 >>> c['a'] = 3
 >>> c.root.a
 3

Setting paths that didn't exist before is not allowed, unless you assign a config object::

 >>> c['b'] = 3 #doctest: +IGNORE_EXCEPTION_DETAIL
 Traceback (most recent call last):
  ...
 CannotSetValue: Cannot set key 'b'

 >>> c['b'] = Config(2)
 >>> c.root.b
 2

Assigning can also be done via the *root* proxy::

 >>> c.root.a = 3
 >>> c.root.a
 3

Backing Up/Restoring
====================

Whenever you want to preserve the configuration prior to a change and restore it later, you can do it with *backup()* and *restore()*. They work like a stack, so they push and pop states::

 >>> c = Config({"value":2})
 >>> c['value']
 2
 >>> c.backup()
 >>> c['value'] = 3
 >>> c['value']
 3
 >>> c.backup()
 >>> c['value'] = 4
 >>> c['value']
 4
 >>> c.restore()
 >>> c['value']
 3
 >>> c.restore()
 >>> c['value']
 2

Metadata
========

You can store metadata on config variables and paths. This is useful for documenting paths or for attaching arbitrary information::

 >>> from confetti import Metadata
 >>> c = Config({
 ...     "key" : "value" // Metadata(some_key="some_value"),
 ...     })

It can later be retrieved::

 >>> c.get_config("key").metadata
 {'some_key': 'some_value'}

Metadata can also be attached to config branches::

 >>> c = Config({
 ...     "key" : {
 ...         "a" : 1,
 ...         "b" : 2,
 ...         } // Metadata(doc="this is a nested dict")
 ...     }) // Metadata(doc="and this is the root")
 >>> c.metadata
 {'doc': 'and this is the root'}
 >>> c.get_config("key").metadata
 {'doc': 'this is a nested dict'}
 

Utilities
=========

Path Assignment
+++++++++++++++

It is possible to assign to a config via path assignment, e.g::

 >>> c = Config(dict(a=dict(b=dict(c=3))))
 >>> c.assign_path("a.b.c", 4)
 >>> c.root.a.b.c
 4

Expression Path Assignment
++++++++++++++++++++++++++

In some cases you would like to receive strings like this::

 a.b.c=2

And make sense of them in the context of the configuration. This might be because they originate from command line, overlay files, or whatever other source comes to mind. *confetti*'s utilities provide a function for this::

 >>> from confetti.utils import assign_path_expression
 >>> assign_path_expression(c, "a.b.c=2")
 >>> c.root.a.b.c
 '2'

Note that in this method, types are always strings. If your leaf already has a value, the *deduce_type* flag can be used to deduce the type from the current value::

 >>> c['a']['b']['c'] = 3
 >>> assign_path_expression(c, 'a.b.c=666', deduce_type=True)
 >>> c.root.a.b.c
 666

