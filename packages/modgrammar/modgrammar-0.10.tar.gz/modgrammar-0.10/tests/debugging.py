# vi:et:ts=2:sw=2

import modgrammar
from modgrammar import *
from modgrammar import GrammarDefError, InternalError
from modgrammar.util import error_result
from modgrammar.debugging import *
from . import util

import sys
import traceback
import io

grammar_whitespace_mode = 'optional'

# These grammars are designed to involve all of the standard grammars which
# have custom grammar_parse functions (to make sure they hook into the debugger
# right), as well as demonstrating backtracking.

class DbgGrammar0 (Grammar):
  grammar = (REF('DbgGrammar1') - L('ABCDE'), NOT_FOLLOWED_BY('D'))

class DbgGrammar1 (Grammar):
  grammar = (L('ABC') | L('ABCDE') | L('ABCD'))

class DbgGrammar2 (Grammar):
  grammar_whitespace_mode = 'required'
  grammar = ('A', 'B')

expected_output_default = """
-- DbgGrammar0  ## Skipped whitespace ' ' at 0
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Matched L('ABC'):'ABC' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Matched DbgGrammar1:'ABC' at 1
-- DbgGrammar0:<EXCEPT>  ## Matched REF('DbgGrammar1'):'ABC' at 1
-- DbgGrammar0:<EXCEPT>['ABC']  ## Failed to match L('ABCDE') at 1
-- DbgGrammar0  ## Matched <EXCEPT>:'ABC' at 1
-- DbgGrammar0['ABC']:<NOT_FOLLOWED_BY>  ## Matched L('D'):'D' at 4
-- DbgGrammar0['ABC']  ## Failed to match <NOT_FOLLOWED_BY> at 4
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## No more matches for L('ABC') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Partial match L('ABCDE'):'ABCD' (need more input or EOF) at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Partial match DbgGrammar1:'ABCD' (need more input or EOF) at 1
-- DbgGrammar0:<EXCEPT>  ## Partial match REF('DbgGrammar1'):'ABCD' (need more input or EOF) at 1
-- DbgGrammar0  ## Partial match <EXCEPT>:'ABCD' (need more input or EOF) at 1
-- (toplevel)  ## Partial match DbgGrammar0:' ABCD' (need more input or EOF) at 0
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Matched L('ABCDE'):'ABCDE' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Matched DbgGrammar1:'ABCDE' at 1
-- DbgGrammar0:<EXCEPT>  ## Matched REF('DbgGrammar1'):'ABCDE' at 1
-- DbgGrammar0:<EXCEPT>['ABCDE']  ## Matched L('ABCDE'):'ABCDE' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## No more matches for L('ABCDE') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Matched L('ABCD'):'ABCD' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Matched DbgGrammar1:'ABCD' at 1
-- DbgGrammar0:<EXCEPT>  ## Matched REF('DbgGrammar1'):'ABCD' at 1
-- DbgGrammar0:<EXCEPT>['ABCD']  ## Failed to match L('ABCDE') at 1
-- DbgGrammar0  ## Matched <EXCEPT>:'ABCD' at 1
-- DbgGrammar0['ABCD']:<NOT_FOLLOWED_BY>  ## Failed to match L('D') at 5
-- DbgGrammar0['ABCD']  ## Matched <NOT_FOLLOWED_BY>:'' at 5
-- (toplevel)  ## Matched DbgGrammar0:' ABCD' at 0
""".strip()

expected_output_full = """
-- (toplevel)  ## Trying DbgGrammar0 at 0
-- DbgGrammar0  ## Skipped whitespace ' ' at 0
-- DbgGrammar0  ## Trying <EXCEPT> at 1
-- DbgGrammar0:<EXCEPT>  ## Trying REF('DbgGrammar1') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Trying DbgGrammar1 at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Trying <OR> at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Trying L('ABC') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Matched L('ABC'):'ABC' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Matched <OR>:'ABC' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Matched DbgGrammar1:'ABC' at 1
-- DbgGrammar0:<EXCEPT>  ## Matched REF('DbgGrammar1'):'ABC' at 1
-- DbgGrammar0:<EXCEPT>['ABC']  ## Trying L('ABCDE') at 1
-- DbgGrammar0:<EXCEPT>['ABC']  ## Failed to match L('ABCDE') at 1
-- DbgGrammar0  ## Matched <EXCEPT>:'ABC' at 1
-- DbgGrammar0['ABC']  ## Trying <NOT_FOLLOWED_BY> at 4
-- DbgGrammar0['ABC']:<NOT_FOLLOWED_BY>  ## Trying L('D') at 4
-- DbgGrammar0['ABC']:<NOT_FOLLOWED_BY>  ## Matched L('D'):'D' at 4
-- DbgGrammar0['ABC']  ## Failed to match <NOT_FOLLOWED_BY> at 4
-- DbgGrammar0  ## Retrying <EXCEPT> at 1
-- DbgGrammar0:<EXCEPT>  ## Retrying REF('DbgGrammar1') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Retrying DbgGrammar1 at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Retrying <OR> at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Retrying L('ABC') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## No more matches for L('ABC') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Trying L('ABCDE') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Partial match L('ABCDE'):'ABCD' (need more input or EOF) at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Partial match <OR>:'ABCD' (need more input or EOF) at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Partial match DbgGrammar1:'ABCD' (need more input or EOF) at 1
-- DbgGrammar0:<EXCEPT>  ## Partial match REF('DbgGrammar1'):'ABCD' (need more input or EOF) at 1
-- DbgGrammar0  ## Partial match <EXCEPT>:'ABCD' (need more input or EOF) at 1
-- (toplevel)  ## Partial match DbgGrammar0:' ABCD' (need more input or EOF) at 0
-- (toplevel)  ## Retrying DbgGrammar0 at 0
-- DbgGrammar0  ## Retrying <EXCEPT> at 1
-- DbgGrammar0:<EXCEPT>  ## Retrying REF('DbgGrammar1') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Retrying DbgGrammar1 at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Retrying <OR> at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Retrying L('ABCDE') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Matched L('ABCDE'):'ABCDE' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Matched <OR>:'ABCDE' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Matched DbgGrammar1:'ABCDE' at 1
-- DbgGrammar0:<EXCEPT>  ## Matched REF('DbgGrammar1'):'ABCDE' at 1
-- DbgGrammar0:<EXCEPT>['ABCDE']  ## Trying L('ABCDE') at 1
-- DbgGrammar0:<EXCEPT>['ABCDE']  ## Matched L('ABCDE'):'ABCDE' at 1
-- DbgGrammar0:<EXCEPT>  ## Retrying REF('DbgGrammar1') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Retrying DbgGrammar1 at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Retrying <OR> at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Retrying L('ABCDE') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## No more matches for L('ABCDE') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Trying L('ABCD') at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1:<OR>  ## Matched L('ABCD'):'ABCD' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1'):DbgGrammar1  ## Matched <OR>:'ABCD' at 1
-- DbgGrammar0:<EXCEPT>:REF('DbgGrammar1')  ## Matched DbgGrammar1:'ABCD' at 1
-- DbgGrammar0:<EXCEPT>  ## Matched REF('DbgGrammar1'):'ABCD' at 1
-- DbgGrammar0:<EXCEPT>['ABCD']  ## Trying L('ABCDE') at 1
-- DbgGrammar0:<EXCEPT>['ABCD']  ## Failed to match L('ABCDE') at 1
-- DbgGrammar0  ## Matched <EXCEPT>:'ABCD' at 1
-- DbgGrammar0['ABCD']  ## Trying <NOT_FOLLOWED_BY> at 5
-- DbgGrammar0['ABCD']:<NOT_FOLLOWED_BY>  ## Trying L('D') at 5
-- DbgGrammar0['ABCD']:<NOT_FOLLOWED_BY>  ## Failed to match L('D') at 5
-- DbgGrammar0['ABCD']  ## Matched <NOT_FOLLOWED_BY>:'' at 5
-- (toplevel)  ## Matched DbgGrammar0:' ABCD' at 0
""".strip()


class TestDebugging (util.TestCase):
  maxDiff = None

  def test_basic_debugging(self):
    outfile = io.StringIO()
    p = DbgGrammar0.parser(debug=outfile)
    p.parse_text(' ABCD')
    p.parse_text('E')
    output = outfile.getvalue().strip()
    self.assertEqual(expected_output_default.split('\n'), output.split('\n'))

  def test_full_debugging(self):
    outfile = io.StringIO()
    p = DbgGrammar0.parser(debug=outfile, debug_flags=DEBUG_ALL | DEBUG_FULL)
    p.parse_text(' ABCD')
    p.parse_text('E')
    output = outfile.getvalue().strip()
    self.assertEqual(expected_output_full.split('\n'), output.split('\n'))

  def test_ws_required(self):
    outfile = io.StringIO()
    p = DbgGrammar2.parser(debug=outfile, debug_flags=DEBUG_WHITESPACE)
    with self.assertRaises(ParseError):
      p.parse_text('AB')
    output = outfile.getvalue().strip()
    self.assertEqual("-- DbgGrammar2['A']  ## Required whitespace not found at 1", output)

  def test_default_logger(self):
    outfile = io.StringIO()
    logger = logging.getLogger('modgrammar')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(outfile)
    handler.setFormatter(logging.Formatter('-- %(message)s'))
    logger.addHandler(handler)
    p = DbgGrammar0.parser(debug=True)
    p.parse_text(' ABCD')
    p.parse_text('E')
    logger.removeHandler(handler)
    output = outfile.getvalue().strip()
    self.assertEqual(expected_output_default.split('\n'), output.split('\n'))

  def test_alternate_logger(self):
    mg_outfile = io.StringIO()
    mg_logger = logging.getLogger('modgrammar')
    mg_logger.setLevel(logging.DEBUG)
    mg_handler = logging.StreamHandler(mg_outfile)
    mg_handler.setFormatter(logging.Formatter('-- %(message)s'))
    mg_logger.addHandler(mg_handler)

    outfile = io.StringIO()
    logger = logging.getLogger('someotherlogger')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(outfile)
    handler.setFormatter(logging.Formatter('-- %(message)s'))
    logger.addHandler(handler)
    p = DbgGrammar0.parser(debug='someotherlogger')
    p.parse_text(' ABCD')
    p.parse_text('E')
    logger.removeHandler(handler)
    self.assertEqual(mg_outfile.getvalue(), '')
    output = outfile.getvalue().strip()
    self.assertEqual(expected_output_default.split('\n'), output.split('\n'))

  def test_custom_logger(self):
    mg_outfile = io.StringIO()
    mg_logger = logging.getLogger('modgrammar')
    mg_logger.setLevel(logging.DEBUG)
    mg_handler = logging.StreamHandler(mg_outfile)
    mg_handler.setFormatter(logging.Formatter('-- %(message)s'))
    mg_logger.addHandler(mg_handler)

    outfile = io.StringIO()
    logger = logging.Logger('test.debuglogger.custom', logging.DEBUG)
    handler = logging.StreamHandler(outfile)
    handler.setFormatter(logging.Formatter('-- %(message)s'))
    logger.addHandler(handler)
    p = DbgGrammar0.parser(debug=logger)
    p.parse_text(' ABCD')
    p.parse_text('E')
    logger.removeHandler(handler)
    self.assertEqual(mg_outfile.getvalue(), '')
    output = outfile.getvalue().strip()
    self.assertEqual(expected_output_default.split('\n'), output.split('\n'))

  def test_left_recursion(self):
    grammar = GRAMMAR(REF('G'), 'A')
    p = grammar.parser(sessiondata={'G': grammar}, debug=True)
    with self.assertRaises(GrammarDefError):
      p.parse_text('A')
    grammar.grammar_resolve_refs({'G': grammar})
    p = grammar.parser(debug=True)
    with self.assertRaises(GrammarDefError):
      p.parse_text('A')

###############################################################################

class BadGrammar_NoneOnEOF (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a None result even if eof=True (which is a no-no)"""
    yield (None, None)
    yield error_result(index, cls)

class BadGrammar_ResultType (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a result which is not a tuple (which is a no-no)"""
    yield 1
    yield error_result(index, cls)

class BadGrammar_ResultLen (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a result which is not a 2-tuple (which is a no-no)"""
    yield (1, cls(''), 2)
    yield error_result(index, cls)

class BadGrammar_OffsetType (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return an offset which is not an int, None, or False (which is a no-no)"""
    yield (1.0, cls(''))
    yield error_result(index, cls)

class BadGrammar_OffsetNeg (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a negative offset (which is a no-no)"""
    yield (-1, cls(''))
    yield error_result(index, cls)

class BadGrammar_OffsetTooBig (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return an impossibly-large offset (which is a no-no)"""
    yield (len(text.string)+1, cls(''))
    yield error_result(index, cls)

class BadGrammar_StopIteration (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will raise StopIteration before returning a failure result (which is a no-no)"""
    while False:
      yield True  # This never actually happens
    # It falls through to the end of the function and causes a StopIteration on
    # the first try

class BadGrammar_RetryAfterFail (Grammar):
  grammar = (L('X'))

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will continue to retry its subgrammar even after a failure result is returned (which is a no-no)"""
    g = cls.grammar[0]
    s = g.grammar_parse(text, index, session)
    if session.debugger:
      s = session.debugger.debug_wrapper(s, g, text, index)
    for offset, obj in s:
      pass
    # We shouldn't ever get here, because the debugger should catch us first
    # and raise InternalError.
    yield (1, cls(''))

class BadGrammar_FailBadObjType (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a failure result with an obj which isn't a tuple (which is a no-no)"""
    yield (False, None)

class BadGrammar_FailBadObjLen (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a failure result with an obj which isn't a 2-tuple (which is a no-no)"""
    yield (False, (index, set([cls]), 3))

class BadGrammar_FailBadErrPos (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a failure result with an error info tuple with an index which isn't an int (which is a no-no)"""
    yield (False, (None, set([cls])))

class BadGrammar_FailBadErrSet (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a failure result with an error info tuple with a second term which isn't a set (which is a no-no)"""
    yield (False, (index, [cls]))

class BadGrammar_FailEmptyErrSet (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a failure result with an error info tuple with an empty second term (which is a no-no)"""
    yield (False, (index, set()))

class BadGrammar_FailBadErrSetContents (Grammar):
  grammar = ()

  @classmethod
  def grammar_parse(cls, text, index, session):
    """This grammar will return a failure result with an error info tuple with a second term which contains a non-Grammar element (which is a no-no)"""
    yield (False, (index, set([cls, 1])))


class TestDebuggingChecks (util.TestCase):
  def test_none_on_eof(self):
    g = GRAMMAR(BadGrammar_NoneOnEOF, 'X')
    try:
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)
    except InternalError as e:
      if g.grammar[0].grammar_name not in e.args[0]:
        self.fail('InternalError message did not indicate specific grammar that failed')
    else:
      self.fail('Did not raise InternalError')

  def test_result_type(self):
    g = BadGrammar_ResultType
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_result_len(self):
    g = BadGrammar_ResultLen
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_offset_type(self):
    g = BadGrammar_OffsetType
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_offset_neg(self):
    g = BadGrammar_OffsetNeg
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_offset_too_big(self):
    g = BadGrammar_OffsetTooBig
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_stopiter(self):
    g = BadGrammar_StopIteration
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_retry_after_fail(self):
    g = BadGrammar_RetryAfterFail
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_failure_bad_obj_type(self):
    g = BadGrammar_FailBadObjType
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_failure_bad_obj_len(self):
    g = BadGrammar_FailBadObjLen
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_failure_bad_err_pos(self):
    g = BadGrammar_FailBadErrPos
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_failure_bad_err_set(self):
    g = BadGrammar_FailBadErrSet
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_failure_empty_err_set(self):
    g = BadGrammar_FailEmptyErrSet
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

  def test_failure_bad_err_set_contents(self):
    g = BadGrammar_FailBadErrSetContents
    with self.assertRaises(InternalError, catchall=True):
      g.parser(debug=True, debug_flags=DEBUG_NONE).parse_text('A', eof=True)

