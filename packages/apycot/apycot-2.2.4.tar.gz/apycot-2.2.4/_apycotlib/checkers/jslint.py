import re
import os
import logging
from subprocess import call
from os.path import exists, dirname, join, abspath
from re import compile

from apycotlib import register, OutputParser, ParsedCommand, FAILURE
from apycotlib.checkers import AbstractFilteredFileChecker

# in source installation, jslint.js is in apycot/ext, we're currently in
# apycot/_apycotlib/checkers
JSLINT_PATH = join(dirname(dirname(dirname(abspath(__file__)))), 'ext', 'jslint.js')
if not exists(JSLINT_PATH):
    JSLINT_PATH = '/usr/share/apycot/ext/jslint.js'

class JsLintParser(OutputParser):
    """Simple Parser class interpretting

    Lint at line 8 character 1: 'CubicWeb' is not defined.
    CubicWeb.require('htmlhelpers.js');
    """
    non_zero_status_code = FAILURE

    RE_MSG = re.compile(r'^Lint at line (\d+) character (\d+):\s*(.*)$')
    #RE_NO_ISSUE = re.compile(r'^jslint: No problems found in ')

    JSLINT_MSG = (
        (logging.INFO,    "Unnecessary semicolon.",),
        (logging.INFO,    "Unnecessary escapement.",),
        (logging.INFO,    "The 'language' attribute is deprecated.",),
        (logging.INFO,    "Inner functions should be listed at the top of the outer function.",),
        (logging.INFO,    compile(r"Don't use extra leading zeros '.*?'\."),),
        (logging.INFO,    "Confusing plusses.",),
        (logging.INFO,    "Confusing minusses.",),
        (logging.INFO,    compile(r"A trailing decimal point can be confused with a dot '.*?'i\."),),
        (logging.INFO,    compile(r"A leading decimal point can be confused with a dot '\..*?'\."),),
        (logging.INFO,    compile(r"'.*?' is better written without quotes\."),),
        (logging.INFO,    compile(r"['.*?'] is better written in dot notation\."),),
        (logging.INFO,    "A dot following a number can be confused with a decimal point.",),
        (logging.WARNING, "Weird construction. Delete 'new'.",),
        (logging.WARNING, "Use the object literal notation {}.",),
        (logging.WARNING, "Use the isNaN function to compare with NaN.",),
        (logging.WARNING, "Use the array literal notation [].",),
        (logging.WARNING, compile(r"Use '.*?' to compare with '.*?'\."),),
        (logging.WARNING, compile(r"Unrecognized tag '<.*?>'\."),),
        (logging.WARNING, compile(r"Unrecognized attribute '<.*? .*?>'\."),),
        (logging.WARNING, compile(r"Unreachable '.*?' after '.*?'\."),),
        (logging.WARNING, "This 'switch' should be an 'if'.",),
        (logging.WARNING, "'new' should not be used as a statement\.",),
        (logging.WARNING, compile(r"Label '.*?' on .*? statement\."),),
        (logging.WARNING, compile(r"Label '.*?' looks like a javascript url\."),),
        (logging.WARNING, "JavaScript URL.",),
        (logging.WARNING, "Implied eval is evil. Pass a function instead of a string.",),
        (logging.WARNING, compile(r"Identifier .*? already declared as .*?\."),),
        (logging.WARNING, "HTML case error.",),
        (logging.WARNING, "Expected to see a statement and instead saw a block.",),
        (logging.WARNING, compile(r"Expected to see a '\(' or '=' or ':' or ',' or '\[' preceding a regular expression literal, and instead saw '.*?'\."),),
        (logging.WARNING, compile(r"Expected '.*?' to match '.*?' from line .*? and instead saw '.*?'\."),),
        (logging.WARNING, compile(r"Expected '.*?' to have an indentation at .*? instead at .*?\."),),
        (logging.WARNING, compile(r"Expected an operator and instead saw '.*?'\."),),
        (logging.WARNING, "Expected an identifier in an assignment and instead saw a function invocation.   ",),
        (logging.WARNING, compile(r"Expected an identifier and instead saw '.*?' (a reserved word)\."),),
        (logging.WARNING, compile(r"Expected an identifier and instead saw '.*?'\."),),
        (logging.WARNING, "Expected an assignment or function call and instead saw an expression.",),
        (logging.WARNING, "Expected a 'break' statement before 'default'.",),
        (logging.WARNING, "Expected a 'break' statement before 'case'.",),
        (logging.WARNING, compile(r"Expected '.*?' and instead saw '.*?'\."),),
        (logging.WARNING, "eval is evil.",),
        (logging.WARNING, "Each value should have its own case label.",),
        (logging.WARNING, compile(r"Do not use the .*? function as a constructor\."),),
        (logging.WARNING, "document.write can be a form of eval.",),
        (logging.WARNING, compile(r"Control character in string: .*?\."),),
        (logging.WARNING, "All 'debugger' statements should be removed.",),
        (logging.WARNING, "Adsafe restriction.",),
        (logging.WARNING, compile(r"Adsafe restricted word '.*?'\."),),
        (logging.WARNING, "A constructor name should start with an uppercase letter.",),
        (logging.WARNING, compile(r".*? (.*?% scanned)\."),),
        (logging.FATAL,   "What the hell is this?",),
        (logging.ERROR,   compile(r"Variable .*? was used before it was declared\."),),
        (logging.ERROR,   compile(r"Unmatched '.*?'\."),),
        (logging.ERROR,   compile(r"Unexpected use of '.*?'\."),),
        (logging.ERROR,   compile(r"Unexpected space after '.*?'\."),),
        (logging.ERROR,   "Unexpected early end of program.",),
        (logging.ERROR,   compile(r"Unexpected characters in '.*?'\."),),
        (logging.ERROR,   compile(r"Unexpected '.*?'\."),),
        (logging.ERROR,   compile(r"Undefined .*? '.*?'\."),),
        (logging.ERROR,   compile(r"Unclosed string\."),),
        (logging.ERROR,   "Unclosed comment.",),
        (logging.ERROR,   "Unbegun comment.",),
        (logging.ERROR,   "The Function constructor is eval.",),
        (logging.ERROR,   "Nested comment.",),
        (logging.ERROR,   compile(r"Missing space after '.*?'\."),),
        (logging.ERROR,   "Missing semicolon.",),
        (logging.ERROR,   "Missing radix parameter.",),
        (logging.ERROR,   "Missing quote.",),
        (logging.ERROR,   "Missing ':' on a case clause.",),
        (logging.ERROR,   "Missing 'new' prefix when invoking a constructor.",),
        (logging.ERROR,   "Missing name in function statement.",),
        (logging.ERROR,   "Missing '()' invoking a constructor.",),
        (logging.ERROR,   "Missing close quote on script attribute.",),
        (logging.ERROR,   compile(r"Missing boolean after '.*?'\."),),
        (logging.ERROR,   compile(r"Missing ':' after '.*?'\."),),
        (logging.ERROR,   compile(r"Missing '.*?'\."),),
        (logging.ERROR,   compile(r"Line breaking error '.*?'\."),),
        (logging.ERROR,   "Function statements are not invocable. Wrap the function expression in parens.   ",),
        (logging.ERROR,   "Extra comma.",),
        (logging.ERROR,   compile(r"Bad value '.*?'\."),),
        (logging.ERROR,   "Bad structure.",),
        (logging.ERROR,   "Bad regular expression.",),
        (logging.ERROR,   compile(r"Bad number '.*?'\."),),
        (logging.ERROR,   compile(r"Bad name '.*?'\."),),
        (logging.ERROR,   compile(r"Bad jslint option '.*?'\."),),
        (logging.ERROR,   "Bad invocation.",),
        (logging.ERROR,   compile(r"Bad extern identifier '.*?'\."),),
        (logging.ERROR,   "Bad escapement.",),
        (logging.ERROR,   compile(r".*? .*? declared in a block\."),),
        (logging.ERROR,   "Bad constructor.",),
        (logging.ERROR,   "Bad assignment.",),
        (logging.ERROR,   compile(r"Attribute '.*?' does not belong in '<.*?>'\."),),
        (logging.ERROR,   "Assignment in control part.",),
        (logging.ERROR,   compile(r"A '<.*?>' must be within '<.*?>'\."),),
    )

    @classmethod
    def get_msg_level(cls, msg, default=logging.ERROR):
        msg = msg.strip()
        for level, msg_pat in cls.JSLINT_MSG:
            if (hasattr(msg_pat, 'match') and msg_pat.match(msg)) or msg == msg_pat:
                return level
        else:
            return default

    def __init__(self, *args, **kwargs):
        super(JsLintParser, self).__init__(*args, **kwargs)
        # line, char_idx, msg
        self._ctx  = None

    def parse_line(self, line):
        if not line:
            self._ctx = None
            return
        match = self.RE_MSG.match(line)
        if match:
            self._ctx = match.groups()
        elif self._ctx is not None:
            filepath = self.path
            lineno = '%s:%s' % (self._ctx[0], self._ctx[1])
            msg  = self._ctx[2]
            level = self.get_msg_level(msg)
            self.writer.log(level, msg, path=filepath, line=lineno)
            self.set_status(FAILURE)
        else:
            self.unparsed.append(line)



if not call(['which', 'rhino'], stdout=file(os.devnull, 'w')):

    class JsLintChecker(AbstractFilteredFileChecker):
        """Js Lint checker for each *.js file"""

        id = 'jslint'
        need_preprocessor = 'build_js'
        checked_extensions = ('.js', )

        def check_file(self, path):
            command = ['rhino', JSLINT_PATH, path]
            return ParsedCommand(self.writer, command, parsercls=JsLintParser,
                                 path=path).run()

        def version_info(self):
            super(JsLintChecker, self).version_info()
            self.record_version_info('jslint', '2010-04-06')

    register('checker', JsLintChecker)


