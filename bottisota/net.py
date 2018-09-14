import socket

ENCODING = "utf-8"

SOCKET_ADDRESS = "/tmp/bottisota.sock"

class Error(Exception):
    pass

class NoMessageError(Error):
    pass

class SyscallError(Error):

    def __init__(self, err):
        self.err = err

    def __str__(self):
        return "Syscall error %d" % self.err

def connect_socket(address=SOCKET_ADDRESS):
    sock = socket.socket(socket.AF_UNIX)
    try:
        sock.connect(address)
    except:
        sock.close()
        raise

    return sock

def disconnect_socket(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    finally:
        sock.close()

class Link:

    def __init__(self, sock, protocol_stack):
        self.__sock = sock
        self.__sockfile = sock.makefile("rw", encoding=ENCODING)
        self.__protocol_stack = protocol_stack

    def recv(self, blocking=True):
        try:
            self.__sock.setblocking(blocking)
            line = self.__sockfile.readline()

            if not line:
                raise NoMessageError()

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
            disconnect_socket(sock)

    def syscall(self, msg, *args):
        self.send(msg, *args)
        received_msg, received_values = self.recv()
        err = received_values[0]
        if err:
            raise SyscallError(err)
        return received_values[1:]
