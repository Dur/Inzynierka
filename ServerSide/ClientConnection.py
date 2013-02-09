__author__ = 'dur'
class ClientConnection(object):
    """A wrapper for socket object to provide the mp_conn interface.
    mod_pywebsocket library is designed to be working on Apache mod_python's
    mp_conn object.
    """

    def __init__(self, socket):
        self._socket = socket

    def write(self, data):
        self._socket.sendall(data)

    def read(self, n):
        return self._socket.recv(n)

    def get_remote_addr(self):
        return self._socket.getpeername()
    remote_addr = property(get_remote_addr)
