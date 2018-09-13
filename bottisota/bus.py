import socket

import bottisota.protocol

ENCODING = "utf-8"

ADDRESS = "/tmp/bottisota.sock"

class Error(Exception):
    pass

class SyscallError(Error):

    def __init__(self, err):
        self.err = err

    def __str__(self):
        return "Syscall error %d" % self.err

def _connect(address=ADDRESS):
    sock = socket.socket(socket.AF_UNIX)
    try:
        sock.connect(address)
    except:
        sock.close()
        raise

    return sock

def _disconnect(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    finally:
        sock.close()

class _Connection:

    def __init__(self, sock, protocol_stack):
        self.__sock = sock
        self.__sockfile = sock.makefile("rw", encoding=ENCODING)
        self.__protocol_stack = protocol_stack

    def recv(self, blocking=True):
        try:
            self.__sock.setblocking(blocking)
            line = self.__sockfile.readline()

            if not line:
                return None

            return self.__protocol_stack.recv(line)
        finally:
            self.__sock.setblocking(True)

    def send(self, *args):
        line = "{}\n".format(" ".join([str(v) for v in args]))
        self.__protocol_stack.send(line)
        self.__sockfile.write(line)
        self.__sockfile.flush()

    def disconnect(self):
        sockfile = self.__sockfile
        sock = self.__sock

        self.__sockfile = None
        self.__sock = None

        try:
            sockfile.close()
        finally:
            _disconnect(sock)

    def syscall(self, syscall, *args):
        self.send(syscall, *args)
        received_syscall, received_values = self.recv()
        err = received_values[0]
        if err:
            raise SyscallError(err)
        return received_values[1:]

class BotConnection(_Connection):

    def __init__(self):
        _Connection.__init__(self, _connect(), bottisota.protocol.BotStack())

    def syscall_clk(self):
        tick, = self.syscall(bottisota.protocol.SYSCALL_CLK_FUN)
        return tick

    def syscall_drv(self, direction, speed):
        speed, = self.syscall(bottisota.protocol.SYSCALL_DRV_FUN, direction, speed)
        return speed

    def syscall_pos(self):
        return self.syscall(bottisota.protocol.SYSCALL_POS_FUN)

    def syscall_scn(self, direction, resolution):
        return self.syscall(bottisota.protocol.SYSCALL_SCN_FUN, direction, resolution)

    def syscall_msl(self, direction, distance):
        self.syscall(bottisota.protocol.SYSCALL_MSL_FUN, direction, distance)

class ArenaConnection(_Connection):

    def __init__(self, sock):
        _Connection.__init__(self, sock, bottisota.protocol.ArenaStack())
