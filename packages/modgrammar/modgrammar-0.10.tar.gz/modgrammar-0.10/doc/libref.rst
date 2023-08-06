***********************************************
:mod:`modgrammar` -- The Modular Grammar Engine
***********************************************

.. automodule:: modgrammar

Grammar Classes
===============

.. autoclass:: Grammar()

Class Attributes
----------------

   .. attribute:: Grammar.grammar

      A list of sub-grammars used to make up this grammar.  This attribute almost always needs to be specified when defining a new grammar class, and is the way in which full grammars can be built up from smaller grammar elements.  In order for this grammar to match an input text, it must completely match each of the sub-grammars listed in its :attr:`grammar` attribute, in order.

   .. attribute:: Grammar.grammar_tags

      A list of "tags" to be associated with match result objects produced by this grammar.  These tags can be used with the :meth:`find` and :meth:`find_all` methods to extract specific elements from a parse tree after a successful match.

   .. attribute:: Grammar.grammar_collapse

      If set to :const:`True`, indicates that this grammar element should be "collapsed" when constructing the final parse tree.  Any place in the parse tree where an instance of this grammar would normally occur will instead be replaced by the list of its sub-elements.  This can be used to make result parse trees simpler in cases where a grammar element has been defined for convenience of the grammar definition, but does not provide a lot of useful information in the resulting parse tree.

   .. attribute:: Grammar.grammar_name

      A string used to identify this grammar.  This is used in a variety of places, including :func:`repr`, :func:`str`, :func:`generate_ebnf`, etc.  (Defaults to the name of the grammar class.)

   .. attribute:: Grammar.grammar_desc

      A descriptive string for the grammar to be used in :exc:`ParseError` error messages. (Defaults to the same value as :attr:`grammar_name`.)

   .. attribute:: Grammar.grammar_noteworthy

      If :const:`False`, this grammar will not be mentioned as one of the possible matches when constructing :exc:`ParseError` error messages (this can be used for grammars which are so ubiquitous or implied that it's not generally necessary to mention them to the user).

   .. attribute:: Grammar.grammar_error_override

      If set, this grammar will report all match failures by its subgrammars as if it had failed itself.  This effectively "hides" the subgrammars in any :exc:`ParseError` (which will use this grammar's location and :attr:`grammar_desc` instead when constructing error messages, etc).

   .. attribute:: Grammar.grammar_whitespace_mode

      Determines how whitespace is treated between sub-elements of this grammar.  It can be set to one of the following values:

        *'explicit'* (default)
          Whitespace between sub-grammars will not be treated differently than any other syntactic element.  Any whitespace which is allowed must be specified explicitly as part of the grammar definition (for example, using :const:`WHITESPACE`), and any extra whitespace will be considered an error.
        *'optional'*
          The grammar will automatically skip over any whitespace found between its sub-grammars (it will be "whitespace consuming").
        *'required'*
          Like *'optional'*, the grammar will skip over whitespace, but it will also require that there must be some amount of whitespace between each of its sub-grammars (if two sub-grammars occur in the input without any whitespace between them, that will be considered an error).

      .. note:: In general, you will want to set this universally for your whole grammar.  The best way to do this is to define a ``grammar_whitespace_mode`` module-level variable in the same module as your grammar classes are defined.  If this is present, it will be used as the default for all grammar classes in that module.

   .. attribute:: Grammar.grammar_whitespace

      In the case where you want a grammar to be "whitespace consuming" but want something other than the normal definition of "whitespace", you can also set :attr:`~Grammar.grammar_whitespace` to a custom regular expression object to be used instead.  This regular expression should attempt to match as much whitespace as possible, starting at the specified position in the string (the actual match result is not used, except that its length is used to determine how far to skip ahead in the string).

      Modgrammar comes with two standard whitespace regexps which can be used "out of the box" for :attr:`~Grammar.grammar_whitespace`:

         =================== ===============================================
         Name                Meaning
         =================== ===============================================
         :const:`WS_DEFAULT` Any whitespace characters (default)
         :const:`WS_NOEOL`   Any whitespace characters except EOL characters
         =================== ===============================================

      (For more information on what constitutes whitespace and EOL characters, see :ref:`whitespace_newline`)

      Similar to :attr:`~Grammar.grammar_whitespace_mode`, you can also set ``grammar_whitespace`` as a module-level variable, in which case it will be used as the default for all grammar classes in that module.

   There are also a few less-commonly-used class attributes which may be useful when inspecting grammars, or may be overridden in special cases:

   .. attribute:: Grammar.grammar_terminal

      Determines whether this grammar is considered to be a "terminal" for the purposes of :meth:`terminals`, :meth:`tokens`, and :func:`generate_ebnf`.  By default, any grammar which contains no sub-grammars (an empty :attr:`grammar` attribute) is considered to be a terminal, and any grammar which has sub-grammars is not.

   .. attribute:: Grammar.grammar_greedy

      If set to :const:`True` (default), indicates that in cases where this grammar could match multiple instances of a sub-text (i.e. for grammars that match repetitions), it should attempt to match the longest possible string first.  By contrast, if set to :const:`False`, the grammar will attempt to match the shortest repetition first.

      .. note:: This attribute does not have any affect on most custom grammars (because most custom grammars are not themselves repetition grammars (instances of :class:`Repetition`)).  If you are looking to change this behavior in your own grammar definitions, you likely want to use the *greedy* parameter of :func:`REPEAT` (and related functions) instead.  Changing this attribute is mainly useful if for some reason you want to make a custom subclass of :class:`Repetition`, or if you are making a custom grammar element (with a custom :meth:`grammar_parse` definition) for which this setting might be significant.

   .. attribute:: Grammar.grammar_collapse_skip

      Specifies that, if an enclosing grammar is set to collapse, and this grammar is in its sub-grammar list, instances of this sub-grammar should also be left out of the resulting parse tree.

      .. note:: There is usually no reason to set this attribute.  (It is enabled by default for :func:`LITERAL` grammars, as it is often desirable to leave literal matches out when collapsing grammars since they usually provide no information which isn't already known to the grammar designer.)

Overridable Class Methods
-------------------------

   The following methods may be overridden in subclasses to change the default behavior of a grammar class:

   .. automethod:: Grammar.grammar_details
   .. automethod:: Grammar.grammar_ebnf_lhs
   .. automethod:: Grammar.grammar_ebnf_rhs
   .. automethod:: Grammar.grammar_parse

Useful Class Methods
--------------------

   The following methods are intended to be called on grammar classes by the application:

   .. automethod:: Grammar.parser
   .. automethod:: Grammar.grammar_resolve_refs

Result Objects
==============

As match result objects are actually instances of the grammar class which produced the match, it is also possible, when defining a new grammar class, to override or add new instance methods which will affect the behavior of any associated result objects.  Result objects also posess a number of attributes and methods which can be useful when examining parse results.

Overridable Instance Methods
----------------------------

   .. automethod:: Grammar.grammar_elem_init
   .. automethod:: Grammar.grammar_collapsed_elems

Useful Instance Attributes
--------------------------

   .. attribute:: Grammar.string

      Contains the portion of the text string which this match corresponds to.

   .. attribute:: Grammar.elements

      Contains result objects for each of the sub-grammars that make up this grammar match.  There is typically one entry in :attr:`elements` for each entry in :attr:`grammar` (though there may not be a direct correspondence if things like :attr:`grammar_collapse` are used)

Useful Instance Methods
-----------------------

   .. automethod:: Grammar.get
   .. automethod:: Grammar.get_all
   .. automethod:: Grammar.find
   .. automethod:: Grammar.find_all
   .. automethod:: Grammar.terminals
   .. automethod:: Grammar.tokens
 
Parser Objects
==============

.. autoclass:: GrammarParser()

Useful Methods
--------------

   .. automethod:: GrammarParser.parse_text
   .. automethod:: GrammarParser.parse_string
   .. automethod:: GrammarParser.parse_lines
   .. automethod:: GrammarParser.parse_file
   .. automethod:: GrammarParser.remainder
   .. automethod:: GrammarParser.clear_remainder
   .. automethod:: GrammarParser.reset
   .. automethod:: GrammarParser.skip

Built-In Grammars
=================

The following basic grammar classes/factories are provided from which more complicated grammars can be constructed.  For those that take arguments, in addition to the arguments listed, there are a number of standard keyword arguments which can also be provided to alter the default behaviors:

* For any grammars which involve repetition, the *min* and *max* parameters can be used to change the minimum and maximum number of repetitions which are allowed.  *count* can also be used to set *min* and *max* to the same value.

* There are also several standard keyword parameters which correspond to the standard class attributes for the Grammar class.  Setting these keyword arguments will have the same effect as if the corresponding class attribute had been specified in a class definition:

      ===================== ========================================
      Keyword               Class Attribute
      ===================== ========================================
      *collapse*            :attr:`~Grammar.grammar_collapse`
      *collapse_skip*       :attr:`~Grammar.grammar_collapse_skip`
      *error_override*      :attr:`~Grammar.grammar_error_override`
      *desc*                :attr:`~Grammar.grammar_desc`
      *greedy*              :attr:`~Grammar.grammar_greedy`
      *name*                :attr:`~Grammar.grammar_name`
      *noteworthy*          :attr:`~Grammar.grammar_noteworthy`
      *tags*                :attr:`~Grammar.grammar_tags`
      *whitespace_mode*     :attr:`~Grammar.grammar_whitespace_mode`
      *whitespace*          :attr:`~Grammar.grammar_whitespace`
      ===================== ========================================

.. autofunction:: GRAMMAR
.. function:: G(\*subgrammars, \**kwargs)

   This is a synonym for :func:`GRAMMAR`

.. autofunction:: LITERAL
.. function:: L(string, \**kwargs)

   This is a synonym for :func:`LITERAL`

.. autofunction:: WORD
.. autofunction:: ANY_EXCEPT
.. autofunction:: OR
.. autofunction:: EXCEPT
.. autofunction:: REPEAT
.. autofunction:: OPTIONAL
.. autofunction:: ZERO_OR_MORE
.. autofunction:: ONE_OR_MORE
.. autofunction:: LIST_OF(\*grammar, sep=",", \**kwargs)
.. autofunction:: NOT_FOLLOWED_BY

.. data:: ANY

   Match any single character.

.. data:: EMPTY

   Match the empty string.

   .. note:: In most cases, :const:`None` is also equivalent to :const:`EMPTY`

.. data:: BOL

   Match the beginning of a line.

   This grammar does not actually consume any of the input text, but can be used to ensure that the next token must occur at the beginning of a new line (i.e. either the beginning of the file, or following an :const:`EOL`).

.. data:: EOL

   Match the end of a line.

   This grammar will match any standard line-end character or character sequence.  For more information on what sequences are considered an "end of line", see :ref:`whitespace_newline`.  If you need something more specific, you may just want to use :func:`LITERAL` instead.

.. data:: EOF

   Match the end of the file.

   .. note:: This grammar will only match if the parse function is called with ``eof=True`` to indicate the end-of-file has been encountered.

.. data:: REST_OF_LINE

   Match everything up to (but not including) the next :const:`EOL`.

.. data:: WHITESPACE

   Match any string of whitespace.  For more information on what is considered whitespace, see :ref:`whitespace_newline`.

   .. note:: This may not match as you expect if your grammar is whitespace-consuming (see the :attr:`~Grammar.grammar_whitespace_mode` attribute).

.. data:: SPACE

   Match any string of whitespace except :const:`EOL` characters.  For more information on what is considered whitespace and "end of line" characters, see :ref:`whitespace_newline`.

   .. note:: This may not match as you expect if your grammar is whitespace-consuming (see the :attr:`~Grammar.grammar_whitespace_mode` attribute).

The :mod:`modgrammar.extras` module also contains some additional built-in grammars which can be useful in some contexts.

References
----------

In some cases, it is necessary to refer to a portion of your grammar before it has actually been defined (for example, for recursive grammar definitions).  In this case, the :func:`REF` function can be used to refer to a grammar by name, which will be resolved to an actual grammar later.  (This construct can also be used to define a grammar which includes some "user-defined" sub-grammar, which the calling application can then provide at runtime.)

.. autofunction:: REF

Constants
=========

The following default regular expressions are provided for use with the :attr:`~Grammar.grammar_whitespace` attribute:

.. data:: WS_DEFAULT

   Will match any series of one or more whitespace characters (default)

.. data:: WS_NOEOL

   Will match any series of whitespace characters except EOL characters

(For more information on what constitutes whitespace and EOL characters, see :ref:`whitespace_newline`)

Exceptions
==========

.. autoexception:: ParseError()
.. autoexception:: GrammarDefError
.. autoexception:: ReferenceError
.. autoexception:: UnknownReferenceError
.. autoexception:: BadReferenceError
.. autoexception:: InternalError

Miscellaneous
=============

.. autofunction:: generate_ebnf

.. _whitespace_newline:

Whitespace and Newline Handling
===============================

Several grammar constructs, such as :const:`SPACE`, and :const:`WHITESPACE` (as well as the :const:`WS_DEFAULT` and :const:`WS_NOEOL` regular expressions made available for use with :attr:`~Grammar.grammar_whitespace`) make reference of "whitespace characters".  Modgrammar considers a "whitespace character" to be any character which is defined in Unicode to have the "whitespace" character property (Note: This is also consistent with the behavior of the "\\s" regular expression escape sequence in Python).  Specifically, this includes the following characters:

         ========= ============ =========================
         Character Other Names  Description
         ========= ============ =========================
         \\u0009   \\t, ^I, HT  horizontal tab
         \\u000A   \\n, ^J, LF  line feed
         \\u000B   \\v, ^K, VT  vertical tab
         \\u000C   \\f, ^L, FF  form feed
         \\u000D   \\r, ^M, CR  carriage return
         \\u0020                space
         \\u0085   NEL          next line
         \\u00A0                no-break space
         \\u1680                ogham space mark
         \\u180E                mongolian vowel separator
         \\u2000                en quad
         \\u2001                em quad
         \\u2002                en space
         \\u2003                em space
         \\u2004                three-per-em space
         \\u2005                four-per-em space
         \\u2006                six-per-em space
         \\u2007                figure space
         \\u2008                punctuation space
         \\u2009                thin space
         \\u200A                hair space
         \\u2028                line separator
         \\u2029                paragraph separator
         \\u202F                narrow no-break space
         \\u205F                medium mathematical space
         \\u3000                ideographic space
         ========= ============ =========================

Note that this is a fairly generous definition of whitespace, designed to be fully Unicode, cross-language, and cross-platform conformant.  In some cases, however, this may not be desirable, as many standards specify a more limited set of characters which should be considered "whitespace".  In many cases, being more liberal on input (parsing) is not a problem, and can even be beneficial, but this should be evaluated on a case-by-case basis if you are writing a parser to match a particular standard definition.  Note also that for some applications it may be useful to, for example, have the parser treat \\u00A0 and \\u202F (non-breaking spaces) as non-whitespace (so that they won't be interpreted as token-separators), etc.

If you wish to have a different definition for "whitespace" in your grammar, you will need to change the value of :attr:`~Grammar.grammar_whitespace` to a custom regular expression which will match a string of whitespace characters according to whatever definition of "whitespace" you are using.  It may also be necessary to redefine the :const:`WHITESPACE` or :const:`SPACE` tokens to match, if your grammar makes use of them (or just not use them).

It is important to note that if you change :attr:`~Grammar.grammar_whitespace`, this will *not* automatically affect any of the other whitespace-based grammars (such as :const:`WHITESPACE`), which will still match the default definition of "whitespace".  If you wish those to change as well, you will need to define your own alternative versions and use those instead of the standard ones.

End-of-Line Characters
----------------------

Additionally, for :const:`EOL`, :const:`REST_OF_LINE`, :const:`SPACE`, and :const:`WS_NOEOL`, Modgrammar considers certain sequences of whitespace to also be "end of line" indicators.  An "end of line" sequence is any of the following:

         =============== ============= ===========================
         Sequence        Other Names   Description
         =============== ============= ===========================
         \\u000D\\u000A  \\r\\n, CRLF  carriage return + line feed
         \\u000A\\u000D  \\n\\r, LFCR  line feed + carriage return
         \\u000A         \\n, ^J, LF   line feed
         \\u000B         \\v, ^K, VT   vertical tab
         \\u000C         \\f, ^L, FF   form feed
         \\u000D         \\r, ^M, CR   carriage return
         \\u0085         NEL           next line
         \\u2028                       line separator
         \\u2029                       paragraph separator
         =============== ============= ===========================

Again, this is a fairly generous list of options, designed to support as wide a range of inputs as possible automatically and usually "do the right thing".  If, however, you need a different set of "end of line" sequences, you may need to define your own versions of some of the above constructs instead of using the default ones provided by Modgrammar.

Note that if you redefine :const:`EOL`, etc, this will not change how the parser calculates line numbers when parsing input, so the :attr:`~GrammarParser.line` and :attr:`~GrammarParser.col` parser attributes (as well as line/column information in :class:`~ParseError`\ s) will likely not match up with your language's actual interpretation of where lines end (Unfortunately, there is currently no support for changing how the parser interprets line boundaries).
