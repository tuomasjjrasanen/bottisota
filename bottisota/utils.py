import re

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
