import re

SYSCALL_CLK_FUN = "CLK?"
SYSCALL_CLK_RET = "CLK="
SYSCALL_DRV_FUN = "DRV?"
SYSCALL_DRV_RET = "DRV="
SYSCALL_POS_FUN = "POS?"
SYSCALL_POS_RET = "POS="
SYSCALL_SCN_FUN = "SCN?"
SYSCALL_SCN_RET = "SCN="
SYSCALL_MSL_FUN = "MSL?"
SYSCALL_MSL_RET = "MSL="

ERR_OK = 0
ERR_UNKNOWN = 1
ERR_BADARG = 2

_CALLER_ARENA = "ARENA"
_CALLER_BOT = "BOT"

class Error(Exception):
    pass

class LexerError(Error):
    pass

class LexiconError(Error):
    pass

class GrammarError(Error):
    pass

class ParserError(Error):
    pass

def _compile_lexicon(lexicon):
    lexicon_map = {}

    for item in lexicon:
        lexeme, regexp = item[:2]
        if lexeme in lexicon_map:
            raise LexiconError("lexicon has a duplicate lexeme", lexeme)
        lexicon_map[lexeme] = (re.compile(regexp), item[2:])

    return lexicon_map

class Lexer(object):

    def __init__(self, lexicon):
        self.__lexicon_map = _compile_lexicon(lexicon)

    def tokenize(self, line):
        keyword, sep, valuestr = line.strip().partition(" ")
        if not keyword:
            raise LexerError("invalid line, keyword is missing: '%s'" % line)

        try:
            pattern, group_types = self.__lexicon_map[keyword]
        except KeyError:
            raise LexerError("unknown keyword: '%s'" % keyword)

        match = pattern.match(valuestr)
        if not match:
            raise LexerError("invalid value", valuestr)

        values = []
        groups = [g for g in match.groups() if g is not None]
        for group_type, group in zip(group_types, groups ):
            values.append(group_type(group))

        return keyword, values

def _compile_grammar(grammar):
    state_transitions = {}

    for state, symbol, next_state in grammar:
        key = (state, symbol)
        if key in state_transitions:
            raise GrammarError("grammar has a duplicate rule", key)
        state_transitions[key] = next_state

    return state_transitions

class Parser(object):

    def __init__(self, grammar):
        self.__initial_state, _, _ = grammar[0]
        self.__state_transitions = _compile_grammar(grammar)
        self.__state = self.__initial_state

    def push(self, symbol):
        retval = None

        key = (self.__state, symbol)
        try:
            next_state = self.__state_transitions[key]
        except KeyError:
            raise ParserError("invalid symbol '%s' in state '%s'" % (symbol, self.__state))

        self.__state = next_state

class _Stack:

    def __init__(self, send_caller, recv_caller):
        lexicon = (
            (SYSCALL_CLK_FUN, r"^$"),
            (SYSCALL_CLK_RET, r"^([0-9]+) ([0-9]+)$", int, int),
            (SYSCALL_DRV_FUN, r"^([0-9]+) ([0-9]+)$", int, int),
            (SYSCALL_DRV_RET, r"^([0-9]+) ([0-9]+)$", int, int),
            (SYSCALL_POS_FUN, r"^$"),
            (SYSCALL_POS_RET, r"^([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)$", int, int, int, int, int),
            (SYSCALL_SCN_FUN, r"^([0-9]+) ([0-9]+)$", int, int),
            (SYSCALL_SCN_RET, r"^([0-9]+) ([0-9]+) ([0-9]+)$", int, int, int),
            (SYSCALL_MSL_FUN, r"^([0-9]+) ([0-9]+)$", int, int),
            (SYSCALL_MSL_RET, r"^([0-9]+)$", int),
        )

        grammar = (
            ("INIT", (_CALLER_BOT, SYSCALL_CLK_FUN), "WAIT"),
            ("WAIT", (_CALLER_ARENA, SYSCALL_CLK_RET), "OPER"),
            ("OPER", (_CALLER_BOT, SYSCALL_DRV_FUN), "DRIV"),
            ("DRIV", (_CALLER_ARENA, SYSCALL_DRV_RET), "OPER"),
            ("OPER", (_CALLER_BOT, SYSCALL_POS_FUN), "POSI"),
            ("POSI", (_CALLER_ARENA, SYSCALL_POS_RET), "OPER"),
            ("OPER", (_CALLER_BOT, SYSCALL_SCN_FUN), "SCAN"),
            ("SCAN", (_CALLER_ARENA, SYSCALL_SCN_RET), "OPER"),
            ("OPER", (_CALLER_BOT, SYSCALL_MSL_FUN), "MISS"),
            ("MISS", (_CALLER_ARENA, SYSCALL_MSL_RET), "OPER"),
            ("OPER", (_CALLER_BOT, SYSCALL_CLK_FUN), "WAIT"),
        )

        self.__lexer = Lexer(lexicon)
        self.__parser = Parser(grammar)

        self.__send_caller = send_caller
        self.__recv_caller = recv_caller

    def send(self, line):
        syscall, arguments = self.__lexer.tokenize(line)
        self.__parser.push((self.__send_caller, syscall))
        return syscall, arguments

    def recv(self, line):
        syscall, arguments = self.__lexer.tokenize(line)
        self.__parser.push((self.__recv_caller, syscall))
        return syscall, arguments

class BotStack(_Stack):

    def __init__(self):
        _Stack.__init__(self, _CALLER_BOT, _CALLER_ARENA)

class ArenaStack(_Stack):

    def __init__(self):
        _Stack.__init__(self, _CALLER_ARENA, _CALLER_BOT)
