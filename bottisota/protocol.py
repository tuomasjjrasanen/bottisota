import bottisota.utils

SYSCALL_CLK_FUN = "CLK?"
SYSCALL_CLK_RET = "CLK="
SYSCALL_DRV_FUN = "DRV?"
SYSCALL_DRV_RET = "DRV="
SYSCALL_POS_FUN = "POS?"
SYSCALL_POS_RET = "POS="
SYSCALL_SCN_FUN = "SCN?"
SYSCALL_SCN_RET = "SCN="

ERR_OK = 0
ERR_UNKNOWN = 1
ERR_BADARG = 2

_CALLER_ARENA = "ARENA"
_CALLER_BOT = "BOT"

_SYSCALL_ARG_FORMATS = {
    SYSCALL_CLK_FUN: "",
    SYSCALL_CLK_RET: " {} {}",
    SYSCALL_DRV_FUN: " {} {}",
    SYSCALL_DRV_RET: " {}",
    SYSCALL_POS_FUN: "",
    SYSCALL_POS_RET: " {} {} {} {} {}",
    SYSCALL_SCN_FUN: " {} {}",
    SYSCALL_SCN_RET: " {} {}",
}

def format_syscall(syscall, *args):
    return "{}{}\n".format(syscall, _SYSCALL_ARG_FORMATS[syscall].format(*args))

class _Stack:

    def __init__(self, send_caller, recv_caller):
        lexicon = (
            (SYSCALL_CLK_FUN, r"^$"),
            (SYSCALL_CLK_RET, r"^([0-9]+) ([0-9]+)$", int, int),
            (SYSCALL_DRV_FUN, r"^([0-9]+) ([0-9]+)$", int, int),
            (SYSCALL_DRV_RET, r"^([0-9]+)$", int),
            (SYSCALL_POS_FUN, r"^$"),
            (SYSCALL_POS_RET, r"^([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)$", int, int, int, int, int),
            (SYSCALL_SCN_FUN, r"^([0-9]+) ([0-9]+)$", int, int),
            (SYSCALL_SCN_RET, r"^([0-9]+) ([0-9]+)$", int, int)
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
            ("OPER", (_CALLER_BOT, SYSCALL_CLK_FUN), "WAIT"),
        )

        self.__lexer = bottisota.utils.Lexer(lexicon)
        self.__parser = bottisota.utils.Parser(grammar)

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
