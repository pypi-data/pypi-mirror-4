# vi:et:ts=2:sw=2

from modgrammar import *
from . import util

#TODO:
# * corner cases for parse_text
# * parse_lines
# * parse_string

grammar_whitespace_mode = 'optional'

class TestParseOpts (util.TestCase):
  def test_matchtype_or(self):
    grammar = OR('aa', 'aaaa', 'a', 'aaa')
    o = grammar.parser().parse_text('aaaa')
    self.assertEqual(o.string, 'aa')  # Default should be 'first'
    o = grammar.parser().parse_text('aaaa', matchtype='first')
    self.assertEqual(o.string, 'aa')
    o = grammar.parser().parse_text('aaaa', matchtype='last')
    self.assertEqual(o.string, 'aaa')
    o = grammar.parser().parse_text('aaaa', matchtype='longest')
    self.assertEqual(o.string, 'aaaa')
    o = grammar.parser().parse_text('aaaa', matchtype='shortest')
    self.assertEqual(o.string, 'a')
    o = grammar.parser().parse_text('aaaa', matchtype='all')
    self.assertEqual([x.string for x in o], ['aa', 'aaaa', 'a', 'aaa'])
    o = grammar.parser().parse_text('aaaa', matchtype='complete')
    self.assertEqual(o.string, 'aaaa')

  def test_matchtype_rep_greedy(self):
    grammar = REPEAT('a', min=1, max=4)
    o = grammar.parser().parse_text('aaaa')
    self.assertEqual(o.string, 'aaaa')  # Default should be 'first'
    o = grammar.parser().parse_text('aaaa', matchtype='first')
    self.assertEqual(o.string, 'aaaa')
    o = grammar.parser().parse_text('aaaa', matchtype='last')
    self.assertEqual(o.string, 'a')
    o = grammar.parser().parse_text('aaaa', matchtype='longest')
    self.assertEqual(o.string, 'aaaa')
    o = grammar.parser().parse_text('aaaa', matchtype='shortest')
    self.assertEqual(o.string, 'a')
    o = grammar.parser().parse_text('aaaa', matchtype='all')
    self.assertEqual([x.string for x in o], ['aaaa', 'aaa', 'aa', 'a'])
    o = grammar.parser().parse_text('aaaa', matchtype='complete')
    self.assertEqual(o.string, 'aaaa')

  def test_matchtype_rep_nongreedy(self):
    grammar = REPEAT('a', min=1, max=4, greedy=False)
    o = grammar.parser().parse_text('aaaa')
    self.assertEqual(o.string, 'a')  # Default should be 'first'
    o = grammar.parser().parse_text('aaaa', matchtype='first')
    self.assertEqual(o.string, 'a')
    o = grammar.parser().parse_text('aaaa', matchtype='last')
    self.assertEqual(o.string, 'aaaa')
    o = grammar.parser().parse_text('aaaa', matchtype='longest')
    self.assertEqual(o.string, 'aaaa')
    o = grammar.parser().parse_text('aaaa', matchtype='shortest')
    self.assertEqual(o.string, 'a')
    o = grammar.parser().parse_text('aaaa', matchtype='all')
    self.assertEqual([x.string for x in o], ['a', 'aa', 'aaa', 'aaaa'])
    o = grammar.parser().parse_text('aaaa', matchtype='complete')
    self.assertEqual(o.string, 'aaaa')

  def test_multi(self):
    grammar = L('a')
    p = grammar.parser()
    o = p.parse_text('aa')
    self.assertEqual(o.string, 'a')
    self.assertEqual(p.remainder(), 'a')
    p.reset()
    o = p.parse_text('aaa', multi=True)
    self.assertIsInstance(o, list)
    self.assertEqual([x.string for x in o], ['a', 'a', 'a'])
    p.reset()
    with self.assertRaises(ParseError):
      o = p.parse_text('aab', multi=True)
