# -*- coding: utf-8 -*-
# vi:et:ts=2:sw=2

import unittest
from modgrammar import *
from . import util

grammar_whitespace_mode = 'explicit'

###############################################################################
# Make sure that Modgrammar can correctly handle non-iso-8859-1 text in both
# grammars and inputs.
###############################################################################

class TestUnicodeInput (util.TestCase):
  def test_unicode_input(self):
    grammar = G('\u30d5', REPEAT('\u30eb' | WORD('\u30d0'), max=2))
    text = 'フバル'
    p = grammar.parser()
    o = p.parse_text(text)
    self.assertEqual(p.remainder(), '')
    self.assertEqual(o.string, text)
    self.assertIsInstance(o[0], Literal)
    self.assertEqual(len(o[0].string), 1)
    self.assertIsInstance(o[1][0], Word)
    self.assertEqual(len(o[1][0].string), 1)
    self.assertIsInstance(o[1][1], Literal)
    self.assertEqual(len(o[1][1].string), 1)

  def test_word_ranges(self):
    # This should match (up to two of) any hirigana characters
    grammar = WORD('ぁ-ゟ', max=2)
    p = grammar.parser()
    o = p.parse_text('ふばる')
    self.assertEqual(p.remainder(), 'る')
    o = p.parse_text('ふバる', reset=True)
    self.assertEqual(p.remainder(), 'バる')

  def test_any_except(self):
    # This should match anything _except_ hirigana characters
    grammar = ANY_EXCEPT('ぁ-ゟ')
    p = grammar.parser()
    o = p.parse_text('フバル', eof=True)
    self.assertEqual(p.remainder(), '')
    with self.assertRaises(ParseError):
      o = p.parse_text('ふ', reset=True)
    o = p.parse_text('バる', reset=True)
    self.assertEqual(p.remainder(), 'る')

  def test_word_escape_w(self):
    # This should match any "word characters" (regardless of language)
    grammar = WORD(r'\w', escapes=True)
    p = grammar.parser()
    # We can't possibly test everything, but test a selection of a few
    # non-ASCII word characters from different alphabets...
    o = p.parse_text('AÂβБあア아ئאঅಅກณ', eof=True)
    self.assertEqual(p.remainder(), '')

  def test_word_escape_d(self):
    # This should match any "decimal digit characters" (regardless of language)
    grammar = WORD(r'\d', escapes=True)
    p = grammar.parser()
    # The following are all of the characters marked in Unicode as "Number,Decimal Digit" (with the following exception).
    # NOTE: (as of Python 3.2) Python does not appear to recognize the
    #       following characters when using "\d" in regular expressions:
    #         * Sora Sompeng digits (U+110F0 - U+110F9)
    #         * Chakma digits (U+11136 - U+1113F)
    #         * Sharada digits (U+111D0 - U+111D9)
    #         * Takri digits (U+116C0 - U+116C9)
    o = p.parse_text('0123456789٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹߀߁߂߃߄߅߆߇߈߉०१२३४५६७८९০১২৩৪৫৬৭৮৯੦੧੨੩੪੫੬੭੮੯૦૧૨૩૪૫૬૭૮૯୦୧୨୩୪୫୬୭୮୯௦௧௨௩௪௫௬௭௮௯౦౧౨౩౪౫౬౭౮౯೦೧೨೩೪೫೬೭೮೯൦൧൨൩൪൫൬൭൮൯๐๑๒๓๔๕๖๗๘๙໐໑໒໓໔໕໖໗໘໙༠༡༢༣༤༥༦༧༨༩၀၁၂၃၄၅၆၇၈၉႐႑႒႓႔႕႖႗႘႙០១២៣៤៥៦៧៨៩᠐᠑᠒᠓᠔᠕᠖᠗᠘᠙᥆᥇᥈᥉᥊᥋᥌᥍᥎᥏᧐᧑᧒᧓᧔᧕᧖᧗᧘᧙᪀᪁᪂᪃᪄᪅᪆᪇᪈᪉᪐᪑᪒᪓᪔᪕᪖᪗᪘᪙᭐᭑᭒᭓᭔᭕᭖᭗᭘᭙᮰᮱᮲᮳᮴᮵᮶᮷᮸᮹᱀᱁᱂᱃᱄᱅᱆᱇᱈᱉᱐᱑᱒᱓᱔᱕᱖᱗᱘᱙꘠꘡꘢꘣꘤꘥꘦꘧꘨꘩꣐꣑꣒꣓꣔꣕꣖꣗꣘꣙꤀꤁꤂꤃꤄꤅꤆꤇꤈꤉꧐꧑꧒꧓꧔꧕꧖꧗꧘꧙꩐꩑꩒꩓꩔꩕꩖꩗꩘꩙꯰꯱꯲꯳꯴꯵꯶꯷꯸꯹０１２３４５６７８９𐒠𐒡𐒢𐒣𐒤𐒥𐒦𐒧𐒨𐒩𑁦𑁧𑁨𑁩𑁪𑁫𑁬𑁭𑁮𑁯𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿', eof=True)
    self.assertEqual(p.remainder(), '')

  def test_word_escape_s(self):
    # This should match any "whitespace characters" (regardless of language)
    grammar = WORD(r'\s', escapes=True)
    p = grammar.parser()
    # The following are all of the characters marked in Unicode as "whitespace"
    o = p.parse_text('\u0009\u000a\u000b\u000c\u000d\u0020\u0085\u00a0\u1680\u180e\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000', eof=True)
    self.assertEqual(p.remainder(), '')

###############################################################################
# Make sure that the default whitespace definitions correctly match all
# standard unicode whitespace characters (not just the basic ASCII ones)
###############################################################################

class TestUnicodeWS (util.TestCase):
  def test_WS_DEFAULT(self):
    grammar = G('A', 'B', whitespace=WS_DEFAULT, whitespace_mode='optional')
    o = grammar.parser().parse_text('A\u0009\u000a\u000b\u000c\u000d\u0020\u0085\u00a0\u1680\u180e\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000B')

  def test_WS_NOEOL(self):
    grammar = G('A', 'B', whitespace=WS_NOEOL, whitespace_mode='optional')
    o = grammar.parser().parse_text('A\u0009\u0020\u00a0\u1680\u180e\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u202f\u205f\u3000B')

  def test_WS_NOEOL_eolchars(self):
    grammar = G('A', 'B', whitespace=WS_NOEOL, whitespace_mode='optional')
    with self.assertRaises(ParseError):
      o = grammar.parser().parse_text('A\u000aB')
    with self.assertRaises(ParseError):
      o = grammar.parser().parse_text('A\u000bB')
    with self.assertRaises(ParseError):
      o = grammar.parser().parse_text('A\u000cB')
    with self.assertRaises(ParseError):
      o = grammar.parser().parse_text('A\u000dB')
    with self.assertRaises(ParseError):
      o = grammar.parser().parse_text('A\u0085B')
    with self.assertRaises(ParseError):
      o = grammar.parser().parse_text('A\u2028B')
    with self.assertRaises(ParseError):
      o = grammar.parser().parse_text('A\u2029B')

  def testEOL(self):
    grammar = G(REPEAT(EOL), 'A')  # Note: grammar_whitespace_mode = 'explicit'
    p = grammar.parser()
    # Make sure EOL matches all the possible EOL sequences properly
    o = p.parse_text('\u000a\u000b\u000c\u000d\u0085\u2028\u2029\r\n\n\rA')
    self.assertEqual(p.remainder(), '')
    self.assertEqual(len(o[0].elements), 9)
    # Check to make sure the parser counts lines the same way EOL does
    self.assertEqual(p.line, 9)
    # Check to make sure ParseErrors report lines the same way EOL does
    p.reset()
    try:
      o = p.parse_text('\u000a\u000b\u000c\u000d\u0085\u2028\u2029\r\n\n\rB')
    except ParseError as e:
      self.assertEqual(e.line, 9)

