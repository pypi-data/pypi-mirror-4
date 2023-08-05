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

class TestIssue8 (util.TestCase):
  """
  Issue 8: Grammars with NOT_FOLLOWED_BY don't correctly return a parse error
           before terminating the generator
  """

  def test_iteration_not_followed_by(self):
    grammar = G('A', NOT_FOLLOWED_BY('A'))
    o = grammar.parser().parse_text('AB', matchtype='all')
    self.assertEqual([x.string for x in o], ['A'])

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

class TestIssue20 (util.TestCase):
  """
  Issue 20: Repetitions incorrectly allowing null subtokens
  """

  def test_repeat_empty_match(self):
    grammar = REPEAT(EMPTY, min=0, max=1)
    o = grammar.parser().parse_text('foobar')
    if o.elements:
      self.fail("REPEAT allowed null subtoken")

class TestIssue23 (util.TestCase):
  """
  Issue 23: EXCEPT stops after first successful match, even if it doesn't meet
            other criteria
  """

  def test_except_multimatch(self):
    grammar = EXCEPT(WORD('a-z', longest=True), L('foo') | L('foobar'))
    with self.assertRaises(modgrammar.ParseError):
      # What should happen here:
      #   1. Successful match on the primary grammar (WORD)
      #   2. Try to match the first exception grammar (L('foo')) (success)
      #   3. EXCEPT notices that the exception grammar is only a prefix so
      #      discards it (see Issue 10)
      #   4. Try to match the second exception grammar (L('foobar')) (success)
      #   5. Exception match is fully valid, so the EXCEPT clause fails.
      # In the buggy case, steps 4-5 do not actually get run and the EXCEPT
      # clause incorrectly returns success.
      o = grammar.parser().parse_text('foobar', eof=True)

class TestIssue24 (util.TestCase):
  """
  Issue 24: hash() breaks on recursive grammars after grammar_resolve_refs
  """

  def test_hash_recursive(self):
    class G (Grammar):
      grammar = (REF('G'))
    G.grammar_resolve_refs({'G': G})
    try:
      hash(G)
    except RuntimeError:
      # We do things this way to hide the horribly spammy "max recursion"
      # traceback.
      self.fail()
