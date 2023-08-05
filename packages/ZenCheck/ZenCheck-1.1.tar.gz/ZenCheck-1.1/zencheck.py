#!/usr/bin/env python
"""
A wrapper for various code/markup syntax checking tools.

Requires:
    * Python 2.4+
    * PyFlakes 0.3+
    * Pep8 0.3+
"""

import sys
from pyflakes import checker as pyflakeschecker
from pyflakes import messages as pyflakesmessages
import _ast
import pep8
import tokenize

pep8.process_options()


class Message(pyflakesmessages.Message):
    '''A pyflakes based Message class defined slightly more convenient.'''

    def __init__(self, filename, message, lineno=0, colno=0):
        self.filename = filename
        self.message = message
        self.lineno = lineno
        if self.lineno is None:
            self.lineno = -1
        self.colno = colno
        if self.colno is None:
            self.colno = -1

    def __str__(self):
        return '%s:%i:%i:%s' % (self.filename, self.lineno, self.colno,
                                self.message % self.message_args)

    def __repr__(self):
        return '%s("%s", "%s", %i, %i)' % (self.__class__.__name__,
                                           self.filename,
                                           self.message,
                                           self.lineno,
                                           self.colno)

    def __hash__(self):
        return hash((self.filename, self.lineno,
                     self.colno, self.message))

    def __cmp__(self, other):
        return cmp((self.filename, self.lineno, self.colno,
                    self.message),
                   (other.filename, other.lineno, other.colno,
                    other.message))

pyflakes_warnings = [pyflakesmessages.UnusedImport,
                     pyflakesmessages.ImportShadowedByLoopVar,
                     pyflakesmessages.RedefinedWhileUnused,
                     pyflakesmessages.ImportStarUsed,
                     pyflakesmessages.UnusedVariable]


def pyflakes_syntax_check(filename):
    '''Check the syntax of the given file using pyflakes and return
    an iterable of Message objects
    '''

    msgs = []

    try:
        with open(filename) as f:
            code = f.read()
        tree = compile(code, filename, "exec", _ast.PyCF_ONLY_AST)
        w = pyflakeschecker.Checker(tree, filename)
        for x in w.messages:
            prefix = 'Error: '
            if x.__class__ in pyflakes_warnings:
                prefix = 'Warning: '
            msgs.append(Message(filename,
                                prefix + x.message % x.message_args,
                                x.lineno))
    except IndentationError, err:
        msgs.append(Message(filename, 'Error: Bad indentation',
                            err.lineno))
    except SyntaxError, err:
        msgs.append(Message(filename, 'Error: Bad syntax',
                            err.lineno))

    return msgs


def pep8_syntax_check(filename):
    '''Check the syntax of the given file using the pep8 module and return
    an iterable of Message objects
    '''

    msgs = []

    class Pep8Checker(pep8.Checker):

        def report_error(self, line_number, offset, text, check):
            msgs.append(Message(filename, 'Warning: (pep8) ' + text,
                                line_number, offset))

    try:
        Pep8Checker(filename).check_all()
    except tokenize.TokenError, err:
        msgs.append(Message(filename, err.args[0],
                            err.args[1][0], err.args[1][1]))
    except IndentationError, err:
        msgs.append(Message(filename, 'Error: Bad indentation',
                            err.lineno))
    except SyntaxError, err:
        msgs.append(Message(filename, 'Error: Bad syntax',
                            err.lineno))

    return msgs


def syntax_check(filename):
    '''Check the syntax of the given file using all available checkers
    and return an iterable of Message objects
    '''

    msgs = pyflakes_syntax_check(filename)
    msgs += pep8_syntax_check(filename)

    s = set(msgs)  # remove duplicates
    msgs = list(s)
    msgs.sort()

    return msgs


def main(cmdargs=sys.argv[1:]):
    '''Meant to be run as main program'''

    ret = 0
    for filename in cmdargs:
        for x in syntax_check(filename):
            print x
    return ret


def test_suite():
    import unittest

    class TestZenCheck(unittest.TestCase):
        file_content = '''
print "foo"
print bar'''

        def setUp(self):
            import tempfile
            self.pyfile = tempfile.NamedTemporaryFile(suffix='.py')
            self.pyfile.write(self.file_content)
            self.pyfile.flush()

        def tearDown(self):
            self.pyfile.close()

        def test_pep8(self):
            msgs = pep8_syntax_check(self.pyfile.name)
            self.assertEqual(
                [x.message for x in msgs],
                ['Warning: (pep8) W292 no newline at end of file'])

        def test_pyflakes(self):
            msgs = pyflakes_syntax_check(self.pyfile.name)
            self.assertEqual([x.message for x in msgs],
                             ["Error: undefined name 'bar'"])

        def test_full_syntax(self):
            syntax_check(self.pyfile.name)

    class TestMessages(unittest.TestCase):

        def test_messages(self):
            m = Message('foo.py', 'testing', 3, colno=10)
            self.assertEqual(str(m), 'foo.py:3:10:testing')
            self.assertEqual(repr(m), 'Message("foo.py", "testing", 3, 10)')


    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestZenCheck),
        unittest.TestLoader().loadTestsFromTestCase(TestMessages),
        ])

if __name__ == '__main__':
    sys.exit(main())
