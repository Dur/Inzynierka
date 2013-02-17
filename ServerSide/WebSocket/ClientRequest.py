from mod_pywebsocket import util
from WebSocket import ClientConnection

__author__ = 'dur'
class ClientRequest(object):
    """A wrapper class just to make it able to pass a socket object to
    functions that expect a mp_request object.
    """

    def __init__(self, socket):
        self._logger = util.get_class_logger(self)

        self._socket = socket
        self.connection = ClientConnection(socket)

    def _drain_received_data(self):
        """Drains unread data in the receive buffer."""

        drained_data = util.drain_received_data(self._socket)

        if drained_data:
            self._logger.debug(
                'Drained data following close frame: %r', drained_data)
