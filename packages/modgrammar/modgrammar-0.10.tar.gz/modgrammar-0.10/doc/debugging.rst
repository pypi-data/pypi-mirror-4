************************************************************
:mod:`modgrammar.debugging` -- Debugging Modgrammar grammars
************************************************************

.. automodule:: modgrammar.debugging

Invoking Debug Mode
===================

Debugging mode can be turned on or off for each :class:`~modgrammar.GrammarParser` used, and debug output can be sent to any of a number of different places, depending on your requirements (including different output for different parsers).  When creating a new parser (using :meth:`~modgrammar.Grammar.parser`), enabling debug mode is done by setting the *debug* parameter.

By default, *debug* is set to :const:`False`, which causes all debugging to be disabled.  If it is set to :const:`True`, debugging will be enabled, and all debug output will be output using the Python :mod:`logging` subsystem.  By default, this is done using the "modgrammar" logger (i.e. by using ``logging.getLogger("modgrammar")``).

Alternately, if you wish debug logging output to go to a different logger object, you can specify a logger name instead (i.e. ``debugging="some.other.logger"``).  In this case, Modgrammar will use :meth:`logging.getLogger` to look up the appropriate logger to use.  Alternately, you can also just pass your own instance of :class:`logging.Logger` to use as well.

.. note::

   All debuging messages will be output to the specified logger using a log level of :const:`DEBUG`, which logger objects do not display by default.  You need to make sure that the log level of your logging heirarchy is set to display :const:`DEBUG` messages somewhere, or you will not see any of the Modgrammar debug output.

If you don't want to mess around with the Python :mod:`logging` framework and just want a quick-and-dirty way to print debugging information to a file or stream, you can also pass any open file-like object (descended from :class:`io.Base`) as the argument to *debug* (i.e. ``debug=sys.stderr``).  Debug messages will be output to that file prefixed by "--".

Finally, for advanced users, the *debug* parameter can also be set to an instance of a :class:`~modgrammar.debugging.GrammarDebugger` class (or subclass), which allows the ability to do entirely custom debugging.

Debugging Flags
===============

If debugging is enabled, the *debug_flags* parameter of :meth:`~modgrammar.Grammar.parser` can be used to specify what types of messages should be logged.  This is specified as a bitmask of any of the following constants or-ed together:

.. data:: DEBUG_TRY

   Show "Trying" debug messages whenever entering a grammar for the first time at a given position.

.. data:: DEBUG_RETRY

   Show "Retrying" debug messages whenever re-entering a grammar to try for additional matches at a given position (if a previous successful match did not work with the larger grammar).

.. data:: DEBUG_FAILURES

   Show match failures in debug output.

.. data:: DEBUG_SUCCESSES

   Show match successes in debug output.

.. data:: DEBUG_PARTIALS

   Show "partial match" results (where the parser needs more input (or EOF) to determine a match or failure) in debug output.

.. data:: DEBUG_WHITESPACE

   Show information about skipped whitespace in debug output.

.. data:: DEBUG_ALL

   Show all types of debug messages (this is equivalent to specifying all of the above together).

Additionally, there are some debug flags which determine what to display based on the grammar being parsed:

.. data:: DEBUG_TERMINALS

   Some grammars marked as "terminals" actually have sub-grammars (which are normally just hidden from the user).  Showing these can be confusing if one is not expecting them (and generally the grammars inside of terminals are fairly well tested already), so by default the debugger does not show information about sub-grammars of terminals.  Supplying this debug option will cause it to output this additional information.

.. data:: DEBUG_OR

   By default, to save some space, and because it usually does not supply any additional information, the debugger does not explicitly show :meth:`~modgrammar.OR` grammars as separate elements, but instead pretends that their subgrammars are called directly by the parent (this usually matches the way the grammars are written, when using the or-operator ("|"), and so is more intuitive).  However, if you want to display :meth:`~modgrammar.OR` grammars explicitly in the debug output, you can supply this flag.

.. data:: DEBUG_FULL

   Turn on all special debugging options.  This is equivalent to ``DEBUG_TERMINALS | DEBUG_OR``.

The following constants are also provided for convenience:

.. data:: DEBUG_DEFAULT

   The default debugging flags if none are specified.  This is equivalent to ``DEBUG_FAILURES | DEBUG_SUCCESSES | DEBUG_PARTIALS | DEBUG_WHITESPACE``.

.. data:: DEBUG_NONE

   Disable all debugging flags (this will produce no debugging output, but will still perform many of the additional correctness checks in the debugger, so can be useful if you suspect something may be wrong with the grammar parser code and want to perform additional sanity-checks).

The GrammarDebugger Class
=========================

.. autoclass:: GrammarDebugger()

Attributes
----------

Debugger objects have the following attributes, initialized based on the parameters provided to the constructor by :meth:`~modgrammar.Grammar.parser`:

  .. attribute:: GrammarDebugger.logger

     A :class:`logging.Logger` instance (or equivalent) which should be used for outputting debugging info.

  .. attribute:: GrammarDebugger.show_try 

     :const:`True` or :const:`False`, depending on whether :const:`DEBUG_TRY` was set in the debug flags

  .. attribute:: GrammarDebugger.show_retry 

     :const:`True` or :const:`False`, depending on whether :const:`DEBUG_RETRY` was set in the debug flags

  .. attribute:: GrammarDebugger.show_failures 

     :const:`True` or :const:`False`, depending on whether :const:`DEBUG_FAILURES` was set in the debug flags

  .. attribute:: GrammarDebugger.show_successes 

     :const:`True` or :const:`False`, depending on whether :const:`DEBUG_SUCCESSES` was set in the debug flags

  .. attribute:: GrammarDebugger.show_partials 

     :const:`True` or :const:`False`, depending on whether :const:`DEBUG_PARTIALS` was set in the debug flags

  .. attribute:: GrammarDebugger.show_whitespace 

     :const:`True` or :const:`False`, depending on whether :const:`DEBUG_WHITESPACE` was set in the debug flags

  .. attribute:: GrammarDebugger.debug_terminals 

     :const:`True` or :const:`False`, depending on whether :const:`DEBUG_TERMINALS` was set in the debug flags

  .. attribute:: GrammarDebugger.show_or 

     :const:`True` or :const:`False`, depending on whether :const:`DEBUG_OR` was set in the debug flags

Additionally, the default implementation of :meth:`~modgrammar.debugging.GrammarDebugger.debug_wrapper` maintains the following properties during debugging:

  .. attribute:: GrammarDebugger.stack

     A list of ``[(id(grammar), pos), grammar, lastmatch, [sub-element stacks]]`` entries, one for each level which has been descended into to reach this position.  (The stack format is difficult to explain concisely.  For detailed examples of how this works it is probably best to look at the source of the :class:`GrammarDebugger` methods (such as :meth:`~GrammarDebugger.stack_summary`))

  .. attribute:: GrammarDebugger.seen

     A set of ``(id(grammar), pos)`` tuples for all of the grammars and corresponding match positions which have been descended into to reach this point (this is used to quickly check for left-recursion).

  .. attribute:: GrammarDebugger.in_terminal

     If this attribute is non-zero, indicates that the parser is currently processing subgrammars inside a grammar which is marked as a terminal, and therefore debugging info should not be printed unless :attr:`debug_terminals` is :const:`True`.

Methods
-------

   .. automethod:: GrammarDebugger.__init__(output=True, flags=DEBUG_DEFAULT)
   .. automethod:: GrammarDebugger.debug_wrapper
   .. automethod:: GrammarDebugger.check_result
   .. automethod:: GrammarDebugger.ws_skipped
   .. automethod:: GrammarDebugger.ws_not_found
   .. automethod:: GrammarDebugger.error_left_recursion
   .. automethod:: GrammarDebugger.match_try
   .. automethod:: GrammarDebugger.match_retry
   .. automethod:: GrammarDebugger.match_failed
   .. automethod:: GrammarDebugger.match_partial
   .. automethod:: GrammarDebugger.match_success
   .. automethod:: GrammarDebugger.stack_summary
   .. automethod:: GrammarDebugger.event

