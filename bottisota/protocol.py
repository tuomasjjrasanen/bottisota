import re

MSG_CLK = "CLK"
MSG_DRV = "DRV"
MSG_POS = "POS"
MSG_SCN = "SCN"
MSG_MSL = "MSL"

ERR_OK = 0
ERR_UNKNOWN = 1
ERR_BADARG = 2
ERR_DESTROYED = 3

_TX = '>'
_RX = '<'

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

    def tokenize(self, peer, line):
        keyword, sep, valuestr = line.strip().partition(" ")
        if not keyword:
            raise LexerError("invalid line, keyword is missing: '%s'" % line)

        try:
            pattern, group_types = self.__lexicon_map[(peer, keyword)]
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

    def __init__(self, tx, rx):
        lexicon = (
            ((_TX, MSG_CLK), r"^$"),
            ((_RX, MSG_CLK), r"^([0-9]+) ([0-9]+)$", int, int),
            ((_TX, MSG_DRV), r"^([0-9]+) ([0-9]+)$", int, int),
            ((_RX, MSG_DRV), r"^([0-9]+) ([0-9]+)$", int, int),
            ((_TX, MSG_POS), r"^$"),
            ((_RX, MSG_POS), r"^([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)$", int, int, int, int, int),
            ((_TX, MSG_SCN), r"^([0-9]+) ([0-9]+)$", int, int),
            ((_RX, MSG_SCN), r"^([0-9]+) ([0-9]+) ([0-9]+)$", int, int, int),
            ((_TX, MSG_MSL), r"^([0-9]+) ([0-9]+)$", int, int),
            ((_RX, MSG_MSL), r"^([0-9]+)$", int),
        )

        grammar = (
            ("INIT", (_TX, MSG_CLK), "WAIT"),
            ("WAIT", (_RX, MSG_CLK), "OPER"),
            ("OPER", (_TX, MSG_DRV), "DRIV"),
            ("DRIV", (_RX, MSG_DRV), "OPER"),
            ("OPER", (_TX, MSG_POS), "POSI"),
            ("POSI", (_RX, MSG_POS), "OPER"),
            ("OPER", (_TX, MSG_SCN), "SCAN"),
            ("SCAN", (_RX, MSG_SCN), "OPER"),
            ("OPER", (_TX, MSG_MSL), "MISS"),
            ("MISS", (_RX, MSG_MSL), "OPER"),
            ("OPER", (_TX, MSG_CLK), "WAIT"),
        )

        self.__lexer = Lexer(lexicon)
        self.__parser = Parser(grammar)

        self.__tx = tx
        self.__rx = rx

    def __comm(self, line, txrx):
        msg, arguments = self.__lexer.tokenize(txrx, line)
        self.__parser.push((txrx, msg))
        return msg, arguments

    def send(self, line):
        return self.__comm(line, self.__tx)

    def recv(self, line):
        return self.__comm(line, self.__rx)

class BotStack(_Stack):

    def __init__(self):
        _Stack.__init__(self, _TX, _RX)

class ServerStack(_Stack):

    def __init__(self):
        _Stack.__init__(self, _RX, _TX)
