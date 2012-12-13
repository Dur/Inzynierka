__author__ = 'dur'
import socket


class _TLSSocket(object):
    """Wrapper for a TLS connection."""

    def __init__(self, raw_socket):
        self._ssl = socket.ssl(raw_socket)

    def send(self, bytes):
        return self._ssl.write(bytes)

    def recv(self, size=-1):
        return self._ssl.read(size)

    def close(self):
        # Nothing to do.
        pass
