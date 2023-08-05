configuration
=============

multi-level unified configuration for python consumption

 - you have a (python) program that wants to read configuration from
  configuration files (I currently support JSON and YAML) and also
  from the command line

 - you want to be able to serialize and deserialize configuration


Basic Usage
-----------

The ``configuration.Configuration`` class is an abstract base
class that extends ``optparse.OptionParser``.  The form of the
configuration is dictated by setting the ``options`` attribute on your
subclass.  ``options`` is a dictionary of the form::

  {'name': {<value>}}

``name`` is the name of the configuration option, and ``value`` is a
``dict`` that gives the form of the option.

``Configuration`` transforms these options into ``OptionParser`` options.

Options for ``value`` include:

 * help : what the option is about (translated to command line help)
 * default: default value for the option
 * required: if a true value, this option must be present in the
   configuration. If ``required`` is a string, it will be displayed if
   the option is not present. If the default is defined, you won't
   need required as the default value will be used
 * type: type of the option. Used to control the parsing of the option
 * flags: a list that, if present, will be used for the command line
   flags. Othwise, the option name prepended by ``--`` will be used.
   To disable as a command line option, use an empty list ``[]``

In addition, you may extend ``Configuration`` and have additional
useful items in the ``value`` dict for ``options``.

For an example, see
http://k0s.org/mozilla/hg/configuration/file/c831eb58fb52/tests/example.py#l7


Configuration Files
-------------------

Config files are useful for (IMHO) A. complicated setup;
B. reproducibility; C. being able to share run time configurations.
The latter is mostly useful if the configuration contains nothing
machine-specific (e.g. the path to an executable might vary from
machine to machine) or if the configuration is overridable from the
command line.

``configuration`` features the ability to serialize (dump) and deserialize
(load) configuration from a pluggable set of formats.  By default,
``--dump <filename>`` will dump the resultant configuration (that
gathered from the command line options and loaded configuration files)
to a file of format dictate by the file extension (Example:
``--dump mydumpfile.json`` will use JSON format).  The flag for the
option, e.g. ``--dump``, may be set via the ``dump`` parameter to
``Configuration``'s constructor.

``Configuration`` instances can also deserialize data.  The normal case of
using configuration is when you want to be able to read from
configuration files.  By default, ``Configuration`` instances read
positional arguments for configuration files to be loaded.  If you
specify a ``load`` argument to the ``Configuration`` constructor, this
option will be used instead.  Likewise, the file extension will be
used to determine the format.

The `configuration package <http://pypi.python.org/pypi/configuration>`_
requires ``json``(``simplejson`` on older python) and ``PyYAML`` so
these serializers/deserializers are available if you install the package.


Extending Configuration
-----------------------

``configuration`` is designed to be pluggable.  While you get a useful
set of behaviour out of the box, most of the handlers for
``configuration`` may be manipulated to do what you want to do.

``Configuration``'s constructor takes an argument, ``types``, which is
a dictionary of callables keyed on type that translate
``Configuration.options`` into ``optparse`` options.  If one of
``Configuration.options`` type isn't specified (or is ``None``), then
the default is used (``configuration.base_cli`` unless you override this).
If not passed, a ``Configuration`` instance uses ``configuration.types``.

The callables in ``types`` should take the option name and value
dictionary and should return the args and keyword args necessary to
instantiate an ``optparse.Option``.

``Configuration``'s constructor also accepts an option,
``configuration_providers``, that is a list of
serializers/deserializers to use.  These should be objects with a list
of ``extensions`` to use, a ``read(filename)`` method that will load
configuration, and a ``write(config, filename)`` method to write it.
``read`` should return the read configuration.
If ``write`` is not present the provider cannot serialize.

TODO
----

 * Add http://k0s.org/hg/ConfigOptionParser and deprecate it

----

Jeff Hammel

http://k0s.org/mozilla/hg/configuration
