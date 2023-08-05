import unittest
import sys
import re
from modgrammar import *
from modgrammar import OR_Operator
from modgrammar.util import RepeatingTuple
from . import util

grammar_whitespace_mode = 'optional'

WS_CUSTOM = re.compile('-*')

###############################################################################
# These tests simply verify that the grammar_whitespace attribute gets set
# correctly on all forms of grammar constructs when they're created.  Actual
# testing of whether each form of grammar actually deals with whitespace
# correctly on parsing should be tested in the basic_grammar tests.
###############################################################################

# Note: The following grammars are predefined constants and thus don't have the
# ability to change their grammar_whitespace based on module setting, etc.
# This is ok, because these are all 'explicit' mode anyway (verified in
# whitespace_mode.py tests), so we don't care what their grammar_whitespace is
# set to:
#   WHITESPACE
#   ANY
#   EOL
#   EOF
#   EMPTY
#   REST_OF_LINE

class G_Default (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')

class G_Default_DEF (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace = WS_DEFAULT

class G_Default_CUST (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace = WS_CUSTOM

default_grammars = (
  ("G_Default", G_Default, WS_DEFAULT),
  ("G_Default_DEF", G_Default_DEF, WS_DEFAULT),
  ("G_Default_CUST", G_Default_CUST, WS_CUSTOM),
  ("GRAMMAR('A', 'B')", GRAMMAR('A', 'B'), WS_DEFAULT),
  ("G('A', 'B')", G('A', 'B'), WS_DEFAULT),
  ("REPEAT(L('A'))", REPEAT(L('A')), WS_DEFAULT),
  ("ZERO_OR_MORE(L('A'))", ZERO_OR_MORE(L('A')), WS_DEFAULT),
  ("ONE_OR_MORE(L('A'))", ONE_OR_MORE(L('A')), WS_DEFAULT),
  ("LIST_OF(L('A'), sep=L('A'))", LIST_OF(L('A'), sep=L('A')), WS_DEFAULT),
  ("LITERAL('A')", LITERAL('A'), WS_DEFAULT),
  ("L('A')", L('A'), WS_DEFAULT),
  ("WORD('A')", WORD('A'), WS_DEFAULT),
  ("ANY_EXCEPT('A')", ANY_EXCEPT('A'), WS_DEFAULT),
  ("OR(L('A'), L('B'))", OR(L('A'), L('B')), WS_DEFAULT),
  ("L('A') | L('B')", L('A') | L('B'), WS_DEFAULT),
  ("OPTIONAL(L('A'))", OPTIONAL(L('A')), WS_DEFAULT),
  ("EXCEPT(L('A'), L('B'))", EXCEPT(L('A'), L('B')), WS_DEFAULT),
  # GRAMMAR with a single element just returns that element, so the following
  # should resolve to LITERALs:
  ("GRAMMAR('A')", GRAMMAR('A'), WS_DEFAULT),
  ("G('A')", G('A'), WS_DEFAULT),

  # Override WS_DEFAULT:
  ("GRAMMAR('A', whitespace=WS_DEFAULT)", GRAMMAR('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("G('A', whitespace=WS_DEFAULT)", G('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("LITERAL('A', whitespace=WS_DEFAULT)", LITERAL('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("L('A', whitespace=WS_DEFAULT)", L('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("WORD('A', whitespace=WS_DEFAULT)", WORD('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("ANY_EXCEPT('A', whitespace=WS_DEFAULT)", ANY_EXCEPT('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("OR(L('A'), L('B'), whitespace=WS_DEFAULT)", OR(L('A'), L('B'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("EXCEPT(L('A'), L('B'), whitespace=WS_DEFAULT)", EXCEPT(L('A'), L('B'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("REPEAT(L('A'), whitespace=WS_DEFAULT)", REPEAT(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("OPTIONAL(L('A'), whitespace=WS_DEFAULT)", OPTIONAL(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("ZERO_OR_MORE(L('A'), whitespace=WS_DEFAULT)", ZERO_OR_MORE(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("ONE_OR_MORE(L('A'), whitespace=WS_DEFAULT)", ONE_OR_MORE(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("LIST_OF(L('A'), sep=L('A'), whitespace=WS_DEFAULT)", LIST_OF(L('A'), sep=L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),

  # Override WS_CUSTOM:
  ("GRAMMAR('A', whitespace=WS_CUSTOM)", GRAMMAR('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("G('A', whitespace=WS_CUSTOM)", G('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("LITERAL('A', whitespace=WS_CUSTOM)", LITERAL('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("L('A', whitespace=WS_CUSTOM)", L('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("WORD('A', whitespace=WS_CUSTOM)", WORD('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("ANY_EXCEPT('A', whitespace=WS_CUSTOM)", ANY_EXCEPT('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("OR(L('A'), L('B'), whitespace=WS_CUSTOM)", OR(L('A'), L('B'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("EXCEPT(L('A'), L('B'), whitespace=WS_CUSTOM)", EXCEPT(L('A'), L('B'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("REPEAT(L('A'), whitespace=WS_CUSTOM)", REPEAT(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("OPTIONAL(L('A'), whitespace=WS_CUSTOM)", OPTIONAL(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("ZERO_OR_MORE(L('A'), whitespace=WS_CUSTOM)", ZERO_OR_MORE(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("ONE_OR_MORE(L('A'), whitespace=WS_CUSTOM)", ONE_OR_MORE(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("LIST_OF(L('A'), sep=L('A'), whitespace=WS_CUSTOM)", LIST_OF(L('A'), sep=L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
)

grammar_whitespace = WS_DEFAULT

class G_DEF (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')

class G_DEF_CUST (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace = WS_CUSTOM

class G_DEF_DEF (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace = WS_DEFAULT

moddef_grammars = (
  ("G_DEF", G_DEF, WS_DEFAULT),
  ("G_DEF_CUST", G_DEF_CUST, WS_CUSTOM),
  ("G_DEF_DEF", G_DEF_DEF, WS_DEFAULT),
  ("GRAMMAR('A', 'B')", GRAMMAR('A', 'B'), WS_DEFAULT),
  ("G('A', 'B')", G('A', 'B'), WS_DEFAULT),
  ("REPEAT(L('A'))", REPEAT(L('A')), WS_DEFAULT),
  ("ZERO_OR_MORE(L('A'))", ZERO_OR_MORE(L('A')), WS_DEFAULT),
  ("ONE_OR_MORE(L('A'))", ONE_OR_MORE(L('A')), WS_DEFAULT),
  ("LIST_OF(L('A'), sep=L('A'))", LIST_OF(L('A'), sep=L('A')), WS_DEFAULT),
  ("LITERAL('A')", LITERAL('A'), WS_DEFAULT),
  ("L('A')", L('A'), WS_DEFAULT),
  ("WORD('A')", WORD('A'), WS_DEFAULT),
  ("ANY_EXCEPT('A')", ANY_EXCEPT('A'), WS_DEFAULT),
  ("OR(L('A'), L('B'))", OR(L('A'), L('B')), WS_DEFAULT),
  ("L('A') | L('B')", L('A') | L('B'), WS_DEFAULT),
  ("OPTIONAL(L('A'))", OPTIONAL(L('A')), WS_DEFAULT),
  ("EXCEPT(L('A'), L('B'))", EXCEPT(L('A'), L('B')), WS_DEFAULT),
  # GRAMMAR with a single element just returns that element, so the following
  # should resolve to LITERALs:
  ("GRAMMAR('A')", GRAMMAR('A'), WS_DEFAULT),
  ("G('A')", G('A'), WS_DEFAULT),

  # Override WS_DEFAULT:
  ("GRAMMAR('A', whitespace=WS_DEFAULT)", GRAMMAR('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("G('A', whitespace=WS_DEFAULT)", G('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("LITERAL('A', whitespace=WS_DEFAULT)", LITERAL('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("L('A', whitespace=WS_DEFAULT)", L('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("WORD('A', whitespace=WS_DEFAULT)", WORD('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("ANY_EXCEPT('A', whitespace=WS_DEFAULT)", ANY_EXCEPT('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("OR(L('A'), L('B'), whitespace=WS_DEFAULT)", OR(L('A'), L('B'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("EXCEPT(L('A'), L('B'), whitespace=WS_DEFAULT)", EXCEPT(L('A'), L('B'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("REPEAT(L('A'), whitespace=WS_DEFAULT)", REPEAT(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("OPTIONAL(L('A'), whitespace=WS_DEFAULT)", OPTIONAL(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("ZERO_OR_MORE(L('A'), whitespace=WS_DEFAULT)", ZERO_OR_MORE(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("ONE_OR_MORE(L('A'), whitespace=WS_DEFAULT)", ONE_OR_MORE(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("LIST_OF(L('A'), sep=L('A'), whitespace=WS_DEFAULT)", LIST_OF(L('A'), sep=L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),

  # Override WS_CUSTOM:
  ("GRAMMAR('A', whitespace=WS_CUSTOM)", GRAMMAR('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("G('A', whitespace=WS_CUSTOM)", G('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("LITERAL('A', whitespace=WS_CUSTOM)", LITERAL('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("L('A', whitespace=WS_CUSTOM)", L('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("WORD('A', whitespace=WS_CUSTOM)", WORD('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("ANY_EXCEPT('A', whitespace=WS_CUSTOM)", ANY_EXCEPT('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("OR(L('A'), L('B'), whitespace=WS_CUSTOM)", OR(L('A'), L('B'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("EXCEPT(L('A'), L('B'), whitespace=WS_CUSTOM)", EXCEPT(L('A'), L('B'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("REPEAT(L('A'), whitespace=WS_CUSTOM)", REPEAT(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("OPTIONAL(L('A'), whitespace=WS_CUSTOM)", OPTIONAL(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("ZERO_OR_MORE(L('A'), whitespace=WS_CUSTOM)", ZERO_OR_MORE(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("ONE_OR_MORE(L('A'), whitespace=WS_CUSTOM)", ONE_OR_MORE(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("LIST_OF(L('A'), sep=L('A'), whitespace=WS_CUSTOM)", LIST_OF(L('A'), sep=L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
)

grammar_whitespace = WS_CUSTOM

class G_CUST (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')

class G_CUST_CUST (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace = WS_CUSTOM

class G_CUST_DEF (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B')
  grammar_whitespace = WS_DEFAULT

modcust_grammars = (
  ("G_CUST", G_CUST, WS_CUSTOM),
  ("G_CUST_CUST", G_CUST_CUST, WS_CUSTOM),
  ("G_CUST_DEF", G_CUST_DEF, WS_DEFAULT),
  ("GRAMMAR('A', 'B')", GRAMMAR('A', 'B'), WS_CUSTOM),
  ("G('A', 'B')", G('A', 'B'), WS_CUSTOM),
  ("REPEAT(L('A'))", REPEAT(L('A')), WS_CUSTOM),
  ("ZERO_OR_MORE(L('A'))", ZERO_OR_MORE(L('A')), WS_CUSTOM),
  ("ONE_OR_MORE(L('A'))", ONE_OR_MORE(L('A')), WS_CUSTOM),
  ("LIST_OF(L('A'), sep=L('A'))", LIST_OF(L('A'), sep=L('A')), WS_CUSTOM),
  ("LITERAL('A')", LITERAL('A'), WS_CUSTOM),
  ("L('A')", L('A'), WS_CUSTOM),
  ("WORD('A')", WORD('A'), WS_CUSTOM),
  ("ANY_EXCEPT('A')", ANY_EXCEPT('A'), WS_CUSTOM),
  ("OR(L('A'), L('B'))", OR(L('A'), L('B')), WS_CUSTOM),
  ("L('A') | L('B')", L('A') | L('B'), WS_CUSTOM),
  ("EXCEPT(L('A'), L('B'))", EXCEPT(L('A'), L('B')), WS_CUSTOM),
  # GRAMMAR with a single element just returns that element, so the following
  # should resolve to LITERALs:
  ("GRAMMAR('A')", GRAMMAR('A'), WS_CUSTOM),
  ("G('A')", G('A'), WS_CUSTOM),

  # Override WS_DEFAULT:
  ("GRAMMAR('A', whitespace=WS_DEFAULT)", GRAMMAR('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("G('A', whitespace=WS_DEFAULT)", G('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("LITERAL('A', whitespace=WS_DEFAULT)", LITERAL('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("L('A', whitespace=WS_DEFAULT)", L('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("WORD('A', whitespace=WS_DEFAULT)", WORD('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("ANY_EXCEPT('A', whitespace=WS_DEFAULT)", ANY_EXCEPT('A', whitespace=WS_DEFAULT), WS_DEFAULT),
  ("OR(L('A'), L('B'), whitespace=WS_DEFAULT)", OR(L('A'), L('B'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("EXCEPT(L('A'), L('B'), whitespace=WS_DEFAULT)", EXCEPT(L('A'), L('B'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("REPEAT(L('A'), whitespace=WS_DEFAULT)", REPEAT(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("OPTIONAL(L('A'), whitespace=WS_DEFAULT)", OPTIONAL(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("ZERO_OR_MORE(L('A'), whitespace=WS_DEFAULT)", ZERO_OR_MORE(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("ONE_OR_MORE(L('A'), whitespace=WS_DEFAULT)", ONE_OR_MORE(L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),
  ("LIST_OF(L('A'), sep=L('A'), whitespace=WS_DEFAULT)", LIST_OF(L('A'), sep=L('A'), whitespace=WS_DEFAULT), WS_DEFAULT),

  # Override WS_CUSTOM:
  ("GRAMMAR('A', whitespace=WS_CUSTOM)", GRAMMAR('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("G('A', whitespace=WS_CUSTOM)", G('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("LITERAL('A', whitespace=WS_CUSTOM)", LITERAL('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("L('A', whitespace=WS_CUSTOM)", L('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("WORD('A', whitespace=WS_CUSTOM)", WORD('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("ANY_EXCEPT('A', whitespace=WS_CUSTOM)", ANY_EXCEPT('A', whitespace=WS_CUSTOM), WS_CUSTOM),
  ("OR(L('A'), L('B'), whitespace=WS_CUSTOM)", OR(L('A'), L('B'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("EXCEPT(L('A'), L('B'), whitespace=WS_CUSTOM)", EXCEPT(L('A'), L('B'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("REPEAT(L('A'), whitespace=WS_CUSTOM)", REPEAT(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("OPTIONAL(L('A'), whitespace=WS_CUSTOM)", OPTIONAL(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("ZERO_OR_MORE(L('A'), whitespace=WS_CUSTOM)", ZERO_OR_MORE(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("ONE_OR_MORE(L('A'), whitespace=WS_CUSTOM)", ONE_OR_MORE(L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
  ("LIST_OF(L('A'), sep=L('A'), whitespace=WS_CUSTOM)", LIST_OF(L('A'), sep=L('A'), whitespace=WS_CUSTOM), WS_CUSTOM),
)

class WhitespaceModeTestCase (util.TestCase):
  def __init__(self, module_setting, name, grammar, expected, modset_str=None):
    util.TestCase.__init__(self, 'perform_test')
    if module_setting is None:
      self.module_setting = WS_DEFAULT
      self.module_setting_str = '(unset)'
    else:
      self.module_setting = module_setting
      self.module_setting_str = self.wsre_name(module_setting)
    if modset_str is not None:
      self.module_setting_str = modset_str
    self.name = name
    self.grammar = grammar
    self.expected = expected

  def wsre_name(self, ws_setting):
    mapdict = {WS_DEFAULT: 'WS_DEFAULT', WS_NOEOL: 'WS_NOEOL', WS_CUSTOM: 'WS_CUSTOM'}
    return mapdict.get(ws_setting, repr(ws_setting))

  def __str__(self):
    return "grammar_whitespace={}: {}".format(self.module_setting_str, self.name)

  def perform_test(self):
    self.check_recursive("{} (module grammar_whitespace={})".format(self.name, self.module_setting_str), self.grammar, self.expected, self.module_setting)

  def check_recursive(self, name, g, expected, expected_sub):
    if g.grammar_whitespace_mode != 'explicit':
      if g.grammar_whitespace != expected:
        raise self.failureException("When testing {}: grammar_whitespace for {!r} is {}".format(name, g, self.wsre_name(g.grammar_whitespace)))
    if issubclass(g, ListRepetition):
      if g.grammar[1].grammar_whitespace != expected:
        raise self.failureException("When testing {}: grammar_whitespace for {!r} is {}".format(name, g.grammar[1], self.wsre_name(g.grammar[1].grammar_whitespace)))
      sub_list = [g.grammar[0], g.sep]
    else:
      sub_list = g.grammar
      if isinstance(sub_list, RepeatingTuple):
        sub_list = [g.grammar[0]]
        if len(g.grammar) > 1:
          sub_list.append(g.grammar[1])
    for sub_g in sub_list:
      self.check_recursive(name, sub_g, expected_sub, expected_sub)

def load_tests(loader, tests, pattern):
  for name, g, expected in default_grammars:
    tests.addTest(WhitespaceModeTestCase(None, name, g, expected))
  for name, g, expected in moddef_grammars:
    tests.addTest(WhitespaceModeTestCase(WS_DEFAULT, name, g, expected))
  for name, g, expected in modcust_grammars:
    tests.addTest(WhitespaceModeTestCase(WS_CUSTOM, name, g, expected, 'WS_CUSTOM'))
  return tests

###############################################################################
# The following tests the use of a custom regular expression for
# grammar_whitespace
###############################################################################

grammar_whitespace = WS_DEFAULT

class WSNormGrammar (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B', 'C')

grammar_whitespace = WS_CUSTOM

class WSCUSTGrammar (Grammar):
  grammar = (ONE_OR_MORE('A'), 'B', 'C')

class WSMixGrammar (Grammar):
  grammar = (ONE_OR_MORE('A', whitespace=WS_DEFAULT), 'B', 'C')

class TestWSNorm (util.BasicGrammarTestCase):
  def setUp(self):
    self.grammar = WSNormGrammar
    self.grammar_name = "WSNormGrammar"
    self.grammar_details = "(REPEAT(L('A')), L('B'), L('C'))"
    self.subgrammar_types = (Repetition, Literal, Literal)
    self.terminal = False
    self.check_min_max = False
    self.matches = ('ABC', 'AABC', 'A A B C')
    self.fail_matches = ('A-BC', 'A-ABC', 'AB-C')

class TestWSCUST (util.BasicGrammarTestCase):
  ws_strs = ('-',)
  def setUp(self):
    self.grammar = WSCUSTGrammar
    self.grammar_name = "WSCUSTGrammar"
    self.grammar_details = "(REPEAT(L('A')), L('B'), L('C'))"
    self.subgrammar_types = (Repetition, Literal, Literal)
    self.terminal = False
    self.check_min_max = False
    self.matches = ('ABC', 'AABC', 'A-A-B-C', 'A--A--B--C')
    self.fail_matches = ('A BC', 'A ABC', 'AB C')

class TestWSMix (util.BasicGrammarTestCase):
  ws_strs = (' ', '-')
  def setUp(self):
    self.grammar = WSMixGrammar
    self.grammar_name = "WSMixGrammar"
    self.grammar_details = "(REPEAT(L('A')), L('B'), L('C'))"
    self.subgrammar_types = (Repetition, Literal, Literal)
    self.terminal = False
    self.check_min_max = False
    self.matches = ('ABC', 'AABC', 'A-BC', 'AA-B-C', 'A A-B-C', 'A  ABC')
    self.fail_matches = ('A BC', 'A-ABC', 'AB C')

