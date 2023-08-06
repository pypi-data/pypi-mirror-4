Overview
--------
confetti is a generic mechanism for storing, loading and manipulating configuration.

Usage
-----

Basics
======

Given a file like this::

 >>> f = open("/tmp/my_file.cfg", "w")
 >>> _ = f.write("""
 ... CONFIG = {
 ...    "a" : {
 ...       "b" : 2,
 ...    }
 ... }""")
 >>> f.close()

Obtaining a configuration object is done via::

 >>> from confetti import Config
 >>> c = Config.from_filename("/tmp/my_file.cfg")
 >>> c.root.a.b
 2

Cross References
================

In many cases you want to set a single value in your configuration, and have other leaves take it by default. Instead of repeating yourself like so::

 >>> cfg = Config(dict(
 ...     my_value = 1337,
 ...     value_1 = 1337,
 ...     x = dict(
 ...         y = dict(
 ...             z = 1337,
 ...         )
 ...     )
 ... ))

You can do this:

 >>> from confetti import Ref
 >>> cfg = Config(dict(
 ...     my_value = 1337,
 ...     value_1 = Ref(".my_value"),
 ...     x = dict(
 ...         y = dict(
 ...             z = Ref("...my_value"),
 ...         )
 ...     )
 ... ))
 >>> cfg.root.x.y.z
 1337

Or you can apply a custom filter to the reference, to create derived values::

 >>> cfg = Config(dict(
 ...     my_value = 1337,
 ...     value_1 = Ref(".my_value", filter="I am {0}".format),
 ... ))
 >>> cfg.root.value_1
 'I am 1337'

Loading From Other Sources
==========================

You can also load from string::

 >>> c = Config.from_string("CONFIG = {'a' : 2}")
 >>> c.root.a
 2

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
 >>> from confetti.utils import assign_path
 >>> assign_path(c, "a.b.c", 4)
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
