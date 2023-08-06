CommandParser
=============

change objects to OptionParser instances via reflection

Overview
--------

It is a common pattern for command line interfaces to use subcomands (e.g.):

  hg commit -m 'foo bar'
  git push origin master

CommandParser does this via introspection of a given class.  When
invoked with a class, CommandParser uses the inspect module to pull
out the mandatory and optional arguments for each of the class's
methods, which are translated to subcommands, and make a OptionParser
instance from them. ``%prog help`` will then display all of the
subcommands and ``%prog help <subcommand>`` will give you help on the
``<subcommand>`` chosen.  Methods beginning with an underscore (`_`)
are passed over.  This gives an easy way to translate an API class
into a command line program::

  class Foo(object):
    """silly class that does nothing"""
    def __init__(self): pass
    def foo(self, value):
      print "The value is %s" % value
    def bar(self, fleem, verbose=False):
      """
      The good ole `bar` command
      - fleem: you know, that thing fleem
      - verbose: whether to print out more things or not
      """
      if verbose:
        print "You gave fleem=%s" % fleem
      return fleem * 2

  import commandparser
  parser = commandparser.CommandParser(Foo)
  parser.invoke()

(From http://k0s.org/hg/CommandParser/file/tip/tests/simpleexample.py )

Example invocation::

  (paint)│./simpleexample.py help
  Usage: simpleexample.py [options] command [command-options]
  
  silly class that does nothing
  
  Options:
    -h, --help  show this help message and exit
  
  Commands: 
    bar   The good ole `bar` command
    foo   
    help  print help for a given command
  (paint)│./simpleexample.py foo
  Usage: simpleexample.py foo <value>
  
  simpleexample.py: error: Not enough arguments given
  (paint)│./simpleexample.py foo 4
  The value is 4
  (paint)│./simpleexample.py bar blah
  blahblah

For optional arguments, the type of the default value will be
inspected from the function signature.  Currently, mandatory arguments
are all strings, though this is clearly a shortcoming.

The class docstring is used for ``%prog --help`` (and ``%prog help``,
same thing). The method docstrings (including those of ``__init__``
for global options) are used for subcommand help.  If the arguments
are listed in the docstring in the form given above
(``- <argument> : <something about the argument``) then these are used
to provide help on the individual options.  Otherwise, these are left
blank.

For straight-forward cases, it may be enough to pass your class
directly to the CommandParser constructor.  For more complex cases, it
is an advisable pattern to create a new class (either via subclassing
or e.g. rolling from scratch, as applicable) that is more amenable to
CommandParser rather than modifying an (e.g.) API class to fit what
CommandParser expects.  This allows the use of an object-oriented
interface for subcommands without sacrificing your API class, and if
you can subclass then there's really not much extra code to write.

See http://k0s.org/hg/CommandParser/file/tip/tests for tests and examples.

----

Jeff Hammel

http://k0s.org/hg/CommandParser

