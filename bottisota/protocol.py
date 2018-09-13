import re

MSG_CLK_FUN = "CLK?"
MSG_CLK_RET = "CLK="
MSG_DRV_FUN = "DRV?"
MSG_DRV_RET = "DRV="
MSG_POS_FUN = "POS?"
MSG_POS_RET = "POS="
MSG_SCN_FUN = "SCN?"
MSG_SCN_RET = "SCN="
MSG_MSL_FUN = "MSL?"
MSG_MSL_RET = "MSL="

ERR_OK = 0
ERR_UNKNOWN = 1
ERR_BADARG = 2
ERR_DESTROYED = 3

_PEER_ARENA = "ARENA"
_PEER_BOT = "BOT"

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

    def __init__(self, sender, receiver):
        lexicon = (
            (MSG_CLK_FUN, r"^$"),
            (MSG_CLK_RET, r"^([0-9]+) ([0-9]+)$", int, int),
            (MSG_DRV_FUN, r"^([0-9]+) ([0-9]+)$", int, int),
            (MSG_DRV_RET, r"^([0-9]+) ([0-9]+)$", int, int),
            (MSG_POS_FUN, r"^$"),
            (MSG_POS_RET, r"^([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)$", int, int, int, int, int),
            (MSG_SCN_FUN, r"^([0-9]+) ([0-9]+)$", int, int),
            (MSG_SCN_RET, r"^([0-9]+) ([0-9]+) ([0-9]+)$", int, int, int),
            (MSG_MSL_FUN, r"^([0-9]+) ([0-9]+)$", int, int),
            (MSG_MSL_RET, r"^([0-9]+)$", int),
        )

        grammar = (
            ("INIT", (_PEER_BOT,   MSG_CLK_FUN), "WAIT"),
            ("WAIT", (_PEER_ARENA, MSG_CLK_RET), "OPER"),
            ("OPER", (_PEER_BOT,   MSG_DRV_FUN), "DRIV"),
            ("DRIV", (_PEER_ARENA, MSG_DRV_RET), "OPER"),
            ("OPER", (_PEER_BOT,   MSG_POS_FUN), "POSI"),
            ("POSI", (_PEER_ARENA, MSG_POS_RET), "OPER"),
            ("OPER", (_PEER_BOT,   MSG_SCN_FUN), "SCAN"),
            ("SCAN", (_PEER_ARENA, MSG_SCN_RET), "OPER"),
            ("OPER", (_PEER_BOT,   MSG_MSL_FUN), "MISS"),
            ("MISS", (_PEER_ARENA, MSG_MSL_RET), "OPER"),
            ("OPER", (_PEER_BOT,   MSG_CLK_FUN), "WAIT"),
        )

        self.__lexer = Lexer(lexicon)
        self.__parser = Parser(grammar)

        self.__sender = sender
        self.__receiver = receiver

    def send(self, line):
        msg, arguments = self.__lexer.tokenize(line)
        self.__parser.push((self.__sender, msg))
        return msg, arguments

    def recv(self, line):
        msg, arguments = self.__lexer.tokenize(line)
        self.__parser.push((self.__receiver, msg))
        return msg, arguments

class BotStack(_Stack):

    def __init__(self):
        _Stack.__init__(self, _PEER_BOT, _PEER_ARENA)

class ArenaStack(_Stack):

    def __init__(self):
        _Stack.__init__(self, _PEER_ARENA, _PEER_BOT)
