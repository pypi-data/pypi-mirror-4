import unittest
import sys
import re
from modgrammar import *
from modgrammar import OR_Operator
from modgrammar.util import RepeatingTuple
from . import util

###############################################################################
# These tests simply verify that the grammar_whitespace_mode attribute gets set
# correctly on all forms of grammar constructs when they're created.  Actual
# testing of whether each form of grammar actually deals with whitespace
# correctly on parsing should be tested in the basic_grammar tests.
###############################################################################

class G_Default (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')

class G_Default_Exp (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'explicit'

class G_Default_Req (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'required'

class G_Default_Opt (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'optional'

default_grammars = (
  ("G_Default", G_Default, 'optional'),
  ("G_Default_Exp", G_Default_Exp, 'explicit'),
  ("G_Default_Req", G_Default_Req, 'required'),
  ("G_Default_Opt", G_Default_Opt, 'optional'),
  ("GRAMMAR('A', 'B')", GRAMMAR('A', 'B'), 'optional'),
  ("G('A', 'B')", G('A', 'B'), 'optional'),
  ("REPEAT(L('A'))", REPEAT(L('A')), 'optional'),
  ("ZERO_OR_MORE(L('A'))", ZERO_OR_MORE(L('A')), 'optional'),
  ("ONE_OR_MORE(L('A'))", ONE_OR_MORE(L('A')), 'optional'),
  ("LIST_OF(L('A'), sep=L('A'))", LIST_OF(L('A'), sep=L('A')), 'optional'),

  # Override 'explicit':
  ("GRAMMAR('A', whitespace_mode='explicit')", GRAMMAR('A', whitespace_mode='explicit'), 'explicit'),
  ("G('A', whitespace_mode='explicit')", G('A', whitespace_mode='explicit'), 'explicit'),
  ("LITERAL('A', whitespace_mode='explicit')", LITERAL('A', whitespace_mode='explicit'), 'explicit'),
  ("L('A', whitespace_mode='explicit')", L('A', whitespace_mode='explicit'), 'explicit'),
  ("WORD('A', whitespace_mode='explicit')", WORD('A', whitespace_mode='explicit'), 'explicit'),
  ("ANY_EXCEPT('A', whitespace_mode='explicit')", ANY_EXCEPT('A', whitespace_mode='explicit'), 'explicit'),
  ("OR(L('A'), L('B'), whitespace_mode='explicit')", OR(L('A'), L('B'), whitespace_mode='explicit'), 'explicit'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='explicit')", EXCEPT(L('A'), L('B'), whitespace_mode='explicit'), 'explicit'),
  ("REPEAT(L('A'), whitespace_mode='explicit')", REPEAT(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("OPTIONAL(L('A'), whitespace_mode='explicit')", OPTIONAL(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='explicit')", ZERO_OR_MORE(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='explicit')", ONE_OR_MORE(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='explicit')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='explicit'), 'explicit'),

  # Override 'optional':
  ("GRAMMAR('A', whitespace_mode='optional')", GRAMMAR('A', whitespace_mode='optional'), 'optional'),
  ("G('A', whitespace_mode='optional')", G('A', whitespace_mode='optional'), 'optional'),
  ("LITERAL('A', whitespace_mode='optional')", LITERAL('A', whitespace_mode='optional'), 'optional'),
  ("L('A', whitespace_mode='optional')", L('A', whitespace_mode='optional'), 'optional'),
  ("WORD('A', whitespace_mode='optional')", WORD('A', whitespace_mode='optional'), 'optional'),
  ("ANY_EXCEPT('A', whitespace_mode='optional')", ANY_EXCEPT('A', whitespace_mode='optional'), 'optional'),
  ("OR(L('A'), L('B'), whitespace_mode='optional')", OR(L('A'), L('B'), whitespace_mode='optional'), 'optional'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='optional')", EXCEPT(L('A'), L('B'), whitespace_mode='optional'), 'optional'),
  ("REPEAT(L('A'), whitespace_mode='optional')", REPEAT(L('A'), whitespace_mode='optional'), 'optional'),
  ("OPTIONAL(L('A'), whitespace_mode='optional')", OPTIONAL(L('A'), whitespace_mode='optional'), 'optional'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='optional')", ZERO_OR_MORE(L('A'), whitespace_mode='optional'), 'optional'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='optional')", ONE_OR_MORE(L('A'), whitespace_mode='optional'), 'optional'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='optional')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='optional'), 'optional'),

  # Override 'required':
  ("GRAMMAR('A', whitespace_mode='required')", GRAMMAR('A', whitespace_mode='required'), 'required'),
  ("G('A', whitespace_mode='required')", G('A', whitespace_mode='required'), 'required'),
  ("LITERAL('A', whitespace_mode='required')", LITERAL('A', whitespace_mode='required'), 'required'),
  ("L('A', whitespace_mode='required')", L('A', whitespace_mode='required'), 'required'),
  ("WORD('A', whitespace_mode='required')", WORD('A', whitespace_mode='required'), 'required'),
  ("ANY_EXCEPT('A', whitespace_mode='required')", ANY_EXCEPT('A', whitespace_mode='required'), 'required'),
  ("OR(L('A'), L('B'), whitespace_mode='required')", OR(L('A'), L('B'), whitespace_mode='required'), 'required'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='required')", EXCEPT(L('A'), L('B'), whitespace_mode='required'), 'required'),
  ("REPEAT(L('A'), whitespace_mode='required')", REPEAT(L('A'), whitespace_mode='required'), 'required'),
  ("OPTIONAL(L('A'), whitespace_mode='required')", OPTIONAL(L('A'), whitespace_mode='required'), 'required'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='required')", ZERO_OR_MORE(L('A'), whitespace_mode='required'), 'required'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='required')", ONE_OR_MORE(L('A'), whitespace_mode='required'), 'required'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='required')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='required'), 'required'),

  # Always 'explicit' by default
  ("LITERAL('A')", LITERAL('A'), 'explicit'),
  ("L('A')", L('A'), 'explicit'),
  ("WORD('A')", WORD('A'), 'explicit'),
  ("ANY_EXCEPT('A')", ANY_EXCEPT('A'), 'explicit'),
  ("OR(L('A'), L('B'))", OR(L('A'), L('B')), 'explicit'),
  ("L('A') | L('B')", L('A') | L('B'), 'explicit'),
  ("OPTIONAL(L('A'))", OPTIONAL(L('A')), 'explicit'),
  ("EXCEPT(L('A'), L('B'))", EXCEPT(L('A'), L('B')), 'explicit'),
  ("ANY", ANY, 'explicit'),
  ("EOL", EOL, 'explicit'),
  ("EOF", EOF, 'explicit'),
  ("EMPTY", EMPTY, 'explicit'),
  ("REST_OF_LINE", REST_OF_LINE, 'explicit'),
  ("WHITESPACE", WHITESPACE, 'explicit'),
  ("NOT_FOLLOWED_BY('A')", NOT_FOLLOWED_BY('A'), 'explicit'),

  # GRAMMAR with a single element just returns that element, so the following
  # should resolve to LITERALs, which are always 'explicit' by default.
  ("GRAMMAR('A')", GRAMMAR('A'), 'explicit'),
  ("G('A')", G('A'), 'explicit'),
)

grammar_whitespace_mode = 'explicit'

class G_Exp (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')

class G_Exp_Exp (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'explicit'

class G_Exp_Req (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'required'

class G_Exp_Opt (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'optional'

modexp_grammars = (
  ("G_Exp", G_Exp, 'explicit'),
  ("G_Exp_Exp", G_Exp_Exp, 'explicit'),
  ("G_Exp_Req", G_Exp_Req, 'required'),
  ("G_Exp_Opt", G_Exp_Opt, 'optional'),
  ("GRAMMAR('A', 'B')", GRAMMAR('A', 'B'), 'explicit'),
  ("G('A', 'B')", G('A', 'B'), 'explicit'),
  ("REPEAT(L('A'))", REPEAT(L('A')), 'explicit'),
  ("ZERO_OR_MORE(L('A'))", ZERO_OR_MORE(L('A')), 'explicit'),
  ("ONE_OR_MORE(L('A'))", ONE_OR_MORE(L('A')), 'explicit'),
  ("LIST_OF(L('A'), sep=L('A'))", LIST_OF(L('A'), sep=L('A')), 'explicit'),

  # Override 'explicit':
  ("GRAMMAR('A', whitespace_mode='explicit')", GRAMMAR('A', whitespace_mode='explicit'), 'explicit'),
  ("G('A', whitespace_mode='explicit')", G('A', whitespace_mode='explicit'), 'explicit'),
  ("LITERAL('A', whitespace_mode='explicit')", LITERAL('A', whitespace_mode='explicit'), 'explicit'),
  ("L('A', whitespace_mode='explicit')", L('A', whitespace_mode='explicit'), 'explicit'),
  ("WORD('A', whitespace_mode='explicit')", WORD('A', whitespace_mode='explicit'), 'explicit'),
  ("ANY_EXCEPT('A', whitespace_mode='explicit')", ANY_EXCEPT('A', whitespace_mode='explicit'), 'explicit'),
  ("OR(L('A'), L('B'), whitespace_mode='explicit')", OR(L('A'), L('B'), whitespace_mode='explicit'), 'explicit'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='explicit')", EXCEPT(L('A'), L('B'), whitespace_mode='explicit'), 'explicit'),
  ("REPEAT(L('A'), whitespace_mode='explicit')", REPEAT(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("OPTIONAL(L('A'), whitespace_mode='explicit')", OPTIONAL(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='explicit')", ZERO_OR_MORE(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='explicit')", ONE_OR_MORE(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='explicit')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='explicit'), 'explicit'),

  # Override 'optional':
  ("GRAMMAR('A', whitespace_mode='optional')", GRAMMAR('A', whitespace_mode='optional'), 'optional'),
  ("G('A', whitespace_mode='optional')", G('A', whitespace_mode='optional'), 'optional'),
  ("LITERAL('A', whitespace_mode='optional')", LITERAL('A', whitespace_mode='optional'), 'optional'),
  ("L('A', whitespace_mode='optional')", L('A', whitespace_mode='optional'), 'optional'),
  ("WORD('A', whitespace_mode='optional')", WORD('A', whitespace_mode='optional'), 'optional'),
  ("ANY_EXCEPT('A', whitespace_mode='optional')", ANY_EXCEPT('A', whitespace_mode='optional'), 'optional'),
  ("OR(L('A'), L('B'), whitespace_mode='optional')", OR(L('A'), L('B'), whitespace_mode='optional'), 'optional'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='optional')", EXCEPT(L('A'), L('B'), whitespace_mode='optional'), 'optional'),
  ("REPEAT(L('A'), whitespace_mode='optional')", REPEAT(L('A'), whitespace_mode='optional'), 'optional'),
  ("OPTIONAL(L('A'), whitespace_mode='optional')", OPTIONAL(L('A'), whitespace_mode='optional'), 'optional'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='optional')", ZERO_OR_MORE(L('A'), whitespace_mode='optional'), 'optional'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='optional')", ONE_OR_MORE(L('A'), whitespace_mode='optional'), 'optional'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='optional')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='optional'), 'optional'),

  # Override 'required':
  ("GRAMMAR('A', whitespace_mode='required')", GRAMMAR('A', whitespace_mode='required'), 'required'),
  ("G('A', whitespace_mode='required')", G('A', whitespace_mode='required'), 'required'),
  ("LITERAL('A', whitespace_mode='required')", LITERAL('A', whitespace_mode='required'), 'required'),
  ("L('A', whitespace_mode='required')", L('A', whitespace_mode='required'), 'required'),
  ("WORD('A', whitespace_mode='required')", WORD('A', whitespace_mode='required'), 'required'),
  ("ANY_EXCEPT('A', whitespace_mode='required')", ANY_EXCEPT('A', whitespace_mode='required'), 'required'),
  ("OR(L('A'), L('B'), whitespace_mode='required')", OR(L('A'), L('B'), whitespace_mode='required'), 'required'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='required')", EXCEPT(L('A'), L('B'), whitespace_mode='required'), 'required'),
  ("REPEAT(L('A'), whitespace_mode='required')", REPEAT(L('A'), whitespace_mode='required'), 'required'),
  ("OPTIONAL(L('A'), whitespace_mode='required')", OPTIONAL(L('A'), whitespace_mode='required'), 'required'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='required')", ZERO_OR_MORE(L('A'), whitespace_mode='required'), 'required'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='required')", ONE_OR_MORE(L('A'), whitespace_mode='required'), 'required'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='required')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='required'), 'required'),

  # Always 'explicit' by default
  ("LITERAL('A')", LITERAL('A'), 'explicit'),
  ("L('A')", L('A'), 'explicit'),
  ("WORD('A')", WORD('A'), 'explicit'),
  ("ANY_EXCEPT('A')", ANY_EXCEPT('A'), 'explicit'),
  ("OR(L('A'), L('B'))", OR(L('A'), L('B')), 'explicit'),
  ("L('A') | L('B')", L('A') | L('B'), 'explicit'),
  ("OPTIONAL(L('A'))", OPTIONAL(L('A')), 'explicit'),
  ("EXCEPT(L('A'), L('B'))", EXCEPT(L('A'), L('B')), 'explicit'),
  ("ANY", ANY, 'explicit'),
  ("EOL", EOL, 'explicit'),
  ("EOF", EOF, 'explicit'),
  ("EMPTY", EMPTY, 'explicit'),
  ("REST_OF_LINE", REST_OF_LINE, 'explicit'),
  ("WHITESPACE", WHITESPACE, 'explicit'),
  ("NOT_FOLLOWED_BY('A')", NOT_FOLLOWED_BY('A'), 'explicit'),

  # GRAMMAR with a single element just returns that element, so the following
  # should resolve to LITERALs, which are always 'explicit' by default.
  ("GRAMMAR('A')", GRAMMAR('A'), 'explicit'),
  ("G('A')", G('A'), 'explicit'),
)

grammar_whitespace_mode = 'optional'

class G_Opt (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')

class G_Opt_Exp (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'explicit'

class G_Opt_Req (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'required'

class G_Opt_Opt (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'optional'

modopt_grammars = (
  ("G_Opt", G_Opt, 'optional'),
  ("G_Opt_Exp", G_Opt_Exp, 'explicit'),
  ("G_Opt_Req", G_Opt_Req, 'required'),
  ("G_Opt_Opt", G_Opt_Opt, 'optional'),
  ("GRAMMAR('A', 'B')", GRAMMAR('A', 'B'), 'optional'),
  ("G('A', 'B')", G('A', 'B'), 'optional'),
  ("REPEAT(L('A'))", REPEAT(L('A')), 'optional'),
  ("ZERO_OR_MORE(L('A'))", ZERO_OR_MORE(L('A')), 'optional'),
  ("ONE_OR_MORE(L('A'))", ONE_OR_MORE(L('A')), 'optional'),
  ("LIST_OF(L('A'), sep=L('A'))", LIST_OF(L('A'), sep=L('A')), 'optional'),

  # Override 'explicit':
  ("GRAMMAR('A', whitespace_mode='explicit')", GRAMMAR('A', whitespace_mode='explicit'), 'explicit'),
  ("G('A', whitespace_mode='explicit')", G('A', whitespace_mode='explicit'), 'explicit'),
  ("LITERAL('A', whitespace_mode='explicit')", LITERAL('A', whitespace_mode='explicit'), 'explicit'),
  ("L('A', whitespace_mode='explicit')", L('A', whitespace_mode='explicit'), 'explicit'),
  ("WORD('A', whitespace_mode='explicit')", WORD('A', whitespace_mode='explicit'), 'explicit'),
  ("ANY_EXCEPT('A', whitespace_mode='explicit')", ANY_EXCEPT('A', whitespace_mode='explicit'), 'explicit'),
  ("OR(L('A'), L('B'), whitespace_mode='explicit')", OR(L('A'), L('B'), whitespace_mode='explicit'), 'explicit'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='explicit')", EXCEPT(L('A'), L('B'), whitespace_mode='explicit'), 'explicit'),
  ("REPEAT(L('A'), whitespace_mode='explicit')", REPEAT(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("OPTIONAL(L('A'), whitespace_mode='explicit')", OPTIONAL(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='explicit')", ZERO_OR_MORE(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='explicit')", ONE_OR_MORE(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='explicit')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='explicit'), 'explicit'),

  # Override 'optional':
  ("GRAMMAR('A', whitespace_mode='optional')", GRAMMAR('A', whitespace_mode='optional'), 'optional'),
  ("G('A', whitespace_mode='optional')", G('A', whitespace_mode='optional'), 'optional'),
  ("LITERAL('A', whitespace_mode='optional')", LITERAL('A', whitespace_mode='optional'), 'optional'),
  ("L('A', whitespace_mode='optional')", L('A', whitespace_mode='optional'), 'optional'),
  ("WORD('A', whitespace_mode='optional')", WORD('A', whitespace_mode='optional'), 'optional'),
  ("ANY_EXCEPT('A', whitespace_mode='optional')", ANY_EXCEPT('A', whitespace_mode='optional'), 'optional'),
  ("OR(L('A'), L('B'), whitespace_mode='optional')", OR(L('A'), L('B'), whitespace_mode='optional'), 'optional'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='optional')", EXCEPT(L('A'), L('B'), whitespace_mode='optional'), 'optional'),
  ("REPEAT(L('A'), whitespace_mode='optional')", REPEAT(L('A'), whitespace_mode='optional'), 'optional'),
  ("OPTIONAL(L('A'), whitespace_mode='optional')", OPTIONAL(L('A'), whitespace_mode='optional'), 'optional'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='optional')", ZERO_OR_MORE(L('A'), whitespace_mode='optional'), 'optional'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='optional')", ONE_OR_MORE(L('A'), whitespace_mode='optional'), 'optional'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='optional')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='optional'), 'optional'),

  # Override 'required':
  ("GRAMMAR('A', whitespace_mode='required')", GRAMMAR('A', whitespace_mode='required'), 'required'),
  ("G('A', whitespace_mode='required')", G('A', whitespace_mode='required'), 'required'),
  ("LITERAL('A', whitespace_mode='required')", LITERAL('A', whitespace_mode='required'), 'required'),
  ("L('A', whitespace_mode='required')", L('A', whitespace_mode='required'), 'required'),
  ("WORD('A', whitespace_mode='required')", WORD('A', whitespace_mode='required'), 'required'),
  ("ANY_EXCEPT('A', whitespace_mode='required')", ANY_EXCEPT('A', whitespace_mode='required'), 'required'),
  ("OR(L('A'), L('B'), whitespace_mode='required')", OR(L('A'), L('B'), whitespace_mode='required'), 'required'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='required')", EXCEPT(L('A'), L('B'), whitespace_mode='required'), 'required'),
  ("REPEAT(L('A'), whitespace_mode='required')", REPEAT(L('A'), whitespace_mode='required'), 'required'),
  ("OPTIONAL(L('A'), whitespace_mode='required')", OPTIONAL(L('A'), whitespace_mode='required'), 'required'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='required')", ZERO_OR_MORE(L('A'), whitespace_mode='required'), 'required'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='required')", ONE_OR_MORE(L('A'), whitespace_mode='required'), 'required'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='required')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='required'), 'required'),

  # Always 'explicit' by default
  ("LITERAL('A')", LITERAL('A'), 'explicit'),
  ("L('A')", L('A'), 'explicit'),
  ("WORD('A')", WORD('A'), 'explicit'),
  ("ANY_EXCEPT('A')", ANY_EXCEPT('A'), 'explicit'),
  ("OR(L('A'), L('B'))", OR(L('A'), L('B')), 'explicit'),
  ("L('A') | L('B')", L('A') | L('B'), 'explicit'),
  ("OPTIONAL(L('A'))", OPTIONAL(L('A')), 'explicit'),
  ("EXCEPT(L('A'), L('B'))", EXCEPT(L('A'), L('B')), 'explicit'),
  ("ANY", ANY, 'explicit'),
  ("EOL", EOL, 'explicit'),
  ("EOF", EOF, 'explicit'),
  ("EMPTY", EMPTY, 'explicit'),
  ("REST_OF_LINE", REST_OF_LINE, 'explicit'),
  ("WHITESPACE", WHITESPACE, 'explicit'),
  ("NOT_FOLLOWED_BY('A')", NOT_FOLLOWED_BY('A'), 'explicit'),

  # GRAMMAR with a single element just returns that element, so the following
  # should resolve to LITERALs, which are always 'explicit' by default.
  ("GRAMMAR('A')", GRAMMAR('A'), 'explicit'),
  ("G('A')", G('A'), 'explicit'),
)

grammar_whitespace_mode = 'required'

class G_Req (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')

class G_Req_Exp (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'explicit'

class G_Req_Req (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'required'

class G_Req_Opt (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace_mode = 'optional'

modreq_grammars = (
  ("G_Req", G_Req, 'required'),
  ("G_Req_Exp", G_Req_Exp, 'explicit'),
  ("G_Req_Req", G_Req_Req, 'required'),
  ("G_Req_Opt", G_Req_Opt, 'optional'),
  ("GRAMMAR('A', 'B')", GRAMMAR('A', 'B'), 'required'),
  ("G('A', 'B')", G('A', 'B'), 'required'),
  ("REPEAT(L('A'))", REPEAT(L('A')), 'required'),
  ("ZERO_OR_MORE(L('A'))", ZERO_OR_MORE(L('A')), 'required'),
  ("ONE_OR_MORE(L('A'))", ONE_OR_MORE(L('A')), 'required'),
  ("LIST_OF(L('A'), sep=L('A'))", LIST_OF(L('A'), sep=L('A')), 'required'),

  # Override 'explicit':
  ("GRAMMAR('A', whitespace_mode='explicit')", GRAMMAR('A', whitespace_mode='explicit'), 'explicit'),
  ("G('A', whitespace_mode='explicit')", G('A', whitespace_mode='explicit'), 'explicit'),
  ("LITERAL('A', whitespace_mode='explicit')", LITERAL('A', whitespace_mode='explicit'), 'explicit'),
  ("L('A', whitespace_mode='explicit')", L('A', whitespace_mode='explicit'), 'explicit'),
  ("WORD('A', whitespace_mode='explicit')", WORD('A', whitespace_mode='explicit'), 'explicit'),
  ("ANY_EXCEPT('A', whitespace_mode='explicit')", ANY_EXCEPT('A', whitespace_mode='explicit'), 'explicit'),
  ("OR(L('A'), L('B'), whitespace_mode='explicit')", OR(L('A'), L('B'), whitespace_mode='explicit'), 'explicit'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='explicit')", EXCEPT(L('A'), L('B'), whitespace_mode='explicit'), 'explicit'),
  ("REPEAT(L('A'), whitespace_mode='explicit')", REPEAT(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("OPTIONAL(L('A'), whitespace_mode='explicit')", OPTIONAL(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='explicit')", ZERO_OR_MORE(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='explicit')", ONE_OR_MORE(L('A'), whitespace_mode='explicit'), 'explicit'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='explicit')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='explicit'), 'explicit'),

  # Override 'optional':
  ("GRAMMAR('A', whitespace_mode='optional')", GRAMMAR('A', whitespace_mode='optional'), 'optional'),
  ("G('A', whitespace_mode='optional')", G('A', whitespace_mode='optional'), 'optional'),
  ("LITERAL('A', whitespace_mode='optional')", LITERAL('A', whitespace_mode='optional'), 'optional'),
  ("L('A', whitespace_mode='optional')", L('A', whitespace_mode='optional'), 'optional'),
  ("WORD('A', whitespace_mode='optional')", WORD('A', whitespace_mode='optional'), 'optional'),
  ("ANY_EXCEPT('A', whitespace_mode='optional')", ANY_EXCEPT('A', whitespace_mode='optional'), 'optional'),
  ("OR(L('A'), L('B'), whitespace_mode='optional')", OR(L('A'), L('B'), whitespace_mode='optional'), 'optional'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='optional')", EXCEPT(L('A'), L('B'), whitespace_mode='optional'), 'optional'),
  ("REPEAT(L('A'), whitespace_mode='optional')", REPEAT(L('A'), whitespace_mode='optional'), 'optional'),
  ("OPTIONAL(L('A'), whitespace_mode='optional')", OPTIONAL(L('A'), whitespace_mode='optional'), 'optional'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='optional')", ZERO_OR_MORE(L('A'), whitespace_mode='optional'), 'optional'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='optional')", ONE_OR_MORE(L('A'), whitespace_mode='optional'), 'optional'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='optional')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='optional'), 'optional'),

  # Override 'required':
  ("GRAMMAR('A', whitespace_mode='required')", GRAMMAR('A', whitespace_mode='required'), 'required'),
  ("G('A', whitespace_mode='required')", G('A', whitespace_mode='required'), 'required'),
  ("LITERAL('A', whitespace_mode='required')", LITERAL('A', whitespace_mode='required'), 'required'),
  ("L('A', whitespace_mode='required')", L('A', whitespace_mode='required'), 'required'),
  ("WORD('A', whitespace_mode='required')", WORD('A', whitespace_mode='required'), 'required'),
  ("ANY_EXCEPT('A', whitespace_mode='required')", ANY_EXCEPT('A', whitespace_mode='required'), 'required'),
  ("OR(L('A'), L('B'), whitespace_mode='required')", OR(L('A'), L('B'), whitespace_mode='required'), 'required'),
  ("EXCEPT(L('A'), L('B'), whitespace_mode='required')", EXCEPT(L('A'), L('B'), whitespace_mode='required'), 'required'),
  ("REPEAT(L('A'), whitespace_mode='required')", REPEAT(L('A'), whitespace_mode='required'), 'required'),
  ("OPTIONAL(L('A'), whitespace_mode='required')", OPTIONAL(L('A'), whitespace_mode='required'), 'required'),
  ("ZERO_OR_MORE(L('A'), whitespace_mode='required')", ZERO_OR_MORE(L('A'), whitespace_mode='required'), 'required'),
  ("ONE_OR_MORE(L('A'), whitespace_mode='required')", ONE_OR_MORE(L('A'), whitespace_mode='required'), 'required'),
  ("LIST_OF(L('A'), sep=L('A'), whitespace_mode='required')", LIST_OF(L('A'), sep=L('A'), whitespace_mode='required'), 'required'),

  # Always 'explicit' by default
  ("LITERAL('A')", LITERAL('A'), 'explicit'),
  ("L('A')", L('A'), 'explicit'),
  ("WORD('A')", WORD('A'), 'explicit'),
  ("ANY_EXCEPT('A')", ANY_EXCEPT('A'), 'explicit'),
  ("OR(L('A'), L('B'))", OR(L('A'), L('B')), 'explicit'),
  ("L('A') | L('B')", L('A') | L('B'), 'explicit'),
  ("OPTIONAL(L('A'))", OPTIONAL(L('A')), 'explicit'),
  ("EXCEPT(L('A'), L('B'))", EXCEPT(L('A'), L('B')), 'explicit'),
  ("ANY", ANY, 'explicit'),
  ("EOL", EOL, 'explicit'),
  ("EOF", EOF, 'explicit'),
  ("EMPTY", EMPTY, 'explicit'),
  ("REST_OF_LINE", REST_OF_LINE, 'explicit'),
  ("WHITESPACE", WHITESPACE, 'explicit'),
  ("NOT_FOLLOWED_BY('A')", NOT_FOLLOWED_BY('A'), 'explicit'),

  # GRAMMAR with a single element just returns that element, so the following
  # should resolve to LITERALs, which are always 'explicit' by default.
  ("GRAMMAR('A')", GRAMMAR('A'), 'explicit'),
  ("G('A')", G('A'), 'explicit'),
)

class WhitespaceModeTestCase (util.TestCase):
  def __init__(self, module_setting, name, grammar, expected, modset_str=None):
    util.TestCase.__init__(self, 'perform_test')
    if module_setting is None:
      self.module_setting = 'optional'
      self.module_setting_str = '(unset)'
    else:
      self.module_setting = module_setting
      self.module_setting_str = repr(module_setting)
    if modset_str is not None:
      self.module_setting_str = modset_str
    self.name = name
    self.grammar = grammar
    self.expected = expected

  def __str__(self):
    return "grammar_whitespace_mode={}: {}".format(self.module_setting_str, self.name)

  def perform_test(self):
    self.check_recursive("{} (module grammar_whitespace_mode={})".format(self.name, self.module_setting_str), self.grammar, self.expected, self.module_setting)

  def check_recursive(self, name, g, expected, expected_sub):
    if g.grammar_whitespace_mode != expected:
      raise self.failureException("When testing {}: grammar_whitespace_mode for {!r} is {!r}".format(name, g, g.grammar_whitespace_mode))
    if issubclass(g, ListRepetition):
      if g.grammar[1].grammar_whitespace_mode != expected:
        raise self.failureException("When testing {}: grammar_whitespace_mode for {!r} is {!r}".format(name, g.grammar[1], g.grammar[1].grammar_whitespace_mode))
      sub_list = [g.grammar[0], g.sep]
    else:
      sub_list = g.grammar
      if isinstance(sub_list, RepeatingTuple):
        sub_list = [g.grammar[0]]
        if len(g.grammar) > 1:
          sub_list.append(g.grammar[1])
    for sub_g in sub_list:
      if issubclass(sub_g, (Terminal, OR_Operator)):
	# Terminals (and OR constructs) always normally have
	# grammar_whitespace_mode set to 'explicit' 
        self.check_recursive(name, sub_g, 'explicit', expected_sub)
      else:
        self.check_recursive(name, sub_g, expected_sub, expected_sub)

def load_tests(loader, tests, pattern):
  for name, g, expected in default_grammars:
    tests.addTest(WhitespaceModeTestCase(None, name, g, expected))
  for name, g, expected in modexp_grammars:
    tests.addTest(WhitespaceModeTestCase('explicit', name, g, expected))
  for name, g, expected in modopt_grammars:
    tests.addTest(WhitespaceModeTestCase('optional', name, g, expected))
  for name, g, expected in modreq_grammars:
    tests.addTest(WhitespaceModeTestCase('required', name, g, expected))
  return tests

