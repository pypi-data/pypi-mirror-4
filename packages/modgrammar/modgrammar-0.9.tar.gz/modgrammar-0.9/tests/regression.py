import modgrammar
from modgrammar import *
from . import util

grammar_whitespace_mode = 'optional'

class TestIssue1 (util.TestCase):
  """
  Issue 1: Fails with traceback if matchtype="longest" or "shortest" and
           there's more than one longest/shortest match with the same length
  """

  def test_longest_samelength(self):
    grammar = OR('aaa', 'aaa')
    o = grammar.parser().parse_text('aaaa', matchtype='longest')

  def test_shortest_samelength(self):
    grammar = OR('aaa', 'aaa')
    o = grammar.parser().parse_text('aaaa', matchtype='shortest')

class TestIssue2 (util.TestCase):
  """
  Issue 2: NameError: global name 'GrammarDefError' is not defined (oops)
  """

  def test_grammardeferror(self):
    self.assertTrue(hasattr(modgrammar, "GrammarDefError"))
    with self.assertRaises(modgrammar.GrammarDefError):
      GRAMMAR(1)

class TestIssue4 (util.TestCase):
  """
  Issue 4: Whitespace before EOF causes parse_lines to fail, even when parsing
           whitespace-consuming grammar (where it should work)
  """

  def test_whitespace_before_eof(self):
    grammar = GRAMMAR('A', whitespace_mode='optional')
    list(grammar.parser().parse_lines(["A "], eof=True))

class TestIssue10 (util.TestCase):
  """
  Issue 10: EXCEPT incorrectly matches on prefixes of the result
  """

  def test_except_prefix(self):
    grammar = EXCEPT('foobar', 'foo')
    try:
      o = grammar.parser().parse_text('foobar')
    except ParseError:
      self.fail("EXCEPT incorrectly matching on substring")

class TestIssue8 (util.TestCase):
  """
  Issue 8: Grammars with NOT_FOLLOWED_BY don't correctly return a parse error
           before terminating the generator
  """

  def test_iteration_not_followed_by(self):
    grammar = G('A', NOT_FOLLOWED_BY('A'))
    o = grammar.parser().parse_text('AB', matchtype='all')
    self.assertEqual([x.string for x in o], ['A'])
