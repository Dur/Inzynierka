import base64
import os
import re
from mod_pywebsocket.extensions import DeflateFrameExtensionProcessor
from WebSocket.ClientHandshakeError import  _build_method_line, _format_host_header, _origin_header, _receive_bytes, _validate_mandatory_header, _get_mandatory_header
from mod_pywebsocket import common
from mod_pywebsocket import util
from WebSocket.ClientHandshakeError import ClientHandshakeError
from WebSocket.ClientHandshakeBase import ClientHandshakeBase


_UPGRADE_HEADER = 'Upgrade: websocket\r\n'
_CONNECTION_HEADER = 'Connection: Upgrade\r\n'

_PROTOCOL_VERSION_HYBI13 = 'hybi13'
_PROTOCOL_VERSION_HYBI08 = 'hybi08'

class ClientHandshakeProcessor(ClientHandshakeBase):
    """WebSocket opening handshake processor for
    draft-ietf-hybi-thewebsocketprotocol-06 and later.
    """

    def __init__(self, socket, options):
        super(ClientHandshakeProcessor, self).__init__()

        self._socket = socket
        self._options = options

        self._logger = util.get_class_logger(self)

    def handshake(self):
        """Performs opening handshake on the specified socket.

        Raises:
            ClientHandshakeError: handshake failed.
        """

        request_line = _build_method_line(self._options.get('resource'))
        self._logger.debug('Client\'s opening handshake Request-Line: %r',
            request_line)
        self._socket.sendall(request_line)

        fields = []
        fields.append(_format_host_header(
            self._options.get('server_host'),
            int(self._options.get('server_port')),
            self._options.get('use_tls')=='True'))
        fields.append(_UPGRADE_HEADER)
        fields.append(_CONNECTION_HEADER)
        if self._options.get('origin') is not None:
            if self._options.get('protocol_version') == _PROTOCOL_VERSION_HYBI08:
                fields.append(_origin_header(
                    common.SEC_WEBSOCKET_ORIGIN_HEADER,
                    self._options.get('origin')))
            else:
                fields.append(_origin_header(common.ORIGIN_HEADER,
                    self._options.get('origin')))

        original_key = os.urandom(16)
        self._key = base64.b64encode(original_key)
        self._logger.debug(
            '%s: %r (%s)',
            common.SEC_WEBSOCKET_KEY_HEADER,
            self._key,
            util.hexify(original_key))
        fields.append(
            '%s: %s\r\n' % (common.SEC_WEBSOCKET_KEY_HEADER, self._key))

        if int(self._options.get('version_header')) > 0:
            fields.append('%s: %d\r\n' % (common.SEC_WEBSOCKET_VERSION_HEADER,
                                          int(self._options.get('version_header'))))
        else:
            fields.append('%s: %d\r\n' % (common.SEC_WEBSOCKET_VERSION_HEADER,
                                          common.VERSION_HYBI_LATEST))

        extensions_to_request = []

        if self._options.get('deflate_stream') == 'True':
            extensions_to_request.append(
                common.ExtensionParameter(
                    common.DEFLATE_STREAM_EXTENSION))

        if self._options.get('deflate_frame') == 'True':
            extensions_to_request.append(
                common.ExtensionParameter(common.DEFLATE_FRAME_EXTENSION))

        if len(extensions_to_request) != 0:
            fields.append(
                '%s: %s\r\n' %
                (common.SEC_WEBSOCKET_EXTENSIONS_HEADER,
                 common.format_extensions(extensions_to_request)))

        for field in fields:
            self._socket.sendall(field)

        self._socket.sendall('\r\n')

        self._logger.debug('Sent client\'s opening handshake headers: %r',
            fields)
        self._logger.debug('Start reading Status-Line')

        status_line = ''
        while True:
            ch = _receive_bytes(self._socket, 1)
            status_line += ch
            if ch == '\n':
                break

        m = re.match('HTTP/\\d+\.\\d+ (\\d\\d\\d) .*\r\n', status_line)
        if m is None:
            raise ClientHandshakeError(
                'Wrong status line format: %r' % status_line)
        status_code = m.group(1)
        if status_code != '101':
            self._logger.debug('Unexpected status code %s with following '
                               'headers: %r', status_code, self._read_fields())
            raise ClientHandshakeError(
                'Expected HTTP status code 101 but found %r' % status_code)

        self._logger.debug('Received valid Status-Line')
        self._logger.debug('Start reading headers until we see an empty line')

        fields = self._read_fields()

        ch = _receive_bytes(self._socket, 1)
        if ch != '\n':  # 0x0A
            raise ClientHandshakeError(
                'Expected LF but found %r while reading value %r for header '
                'name %r' % (ch, "test", "test"))

        self._logger.debug('Received an empty line')
        self._logger.debug('Server\'s opening handshake headers: %r', fields)

        _validate_mandatory_header(
            fields,
            common.UPGRADE_HEADER,
            common.WEBSOCKET_UPGRADE_TYPE,
            False)

        _validate_mandatory_header(
            fields,
            common.CONNECTION_HEADER,
            common.UPGRADE_CONNECTION_TYPE,
            False)

        accept = _get_mandatory_header(
            fields, common.SEC_WEBSOCKET_ACCEPT_HEADER)

        # Validate
        try:
            binary_accept = base64.b64decode(accept)
        except TypeError, e:
            raise HandshakeError(
                'Illegal value for header %s: %r' %
                (common.SEC_WEBSOCKET_ACCEPT_HEADER, accept))

        if len(binary_accept) != 20:
            raise ClientHandshakeError(
                'Decoded value of %s is not 20-byte long' %
                common.SEC_WEBSOCKET_ACCEPT_HEADER)

        self._logger.debug(
            'Response for challenge : %r (%s)',
            accept, util.hexify(binary_accept))

        binary_expected_accept = util.sha1_hash(
            self._key + common.WEBSOCKET_ACCEPT_UUID).digest()
        expected_accept = base64.b64encode(binary_expected_accept)

        self._logger.debug(
            'Expected response for challenge: %r (%s)',
            expected_accept, util.hexify(binary_expected_accept))

        if accept != expected_accept:
            raise ClientHandshakeError(
                'Invalid %s header: %r (expected: %s)' %
                (common.SEC_WEBSOCKET_ACCEPT_HEADER, accept, expected_accept))

        deflate_stream_accepted = False
        deflate_frame_accepted = False

        extensions_header = fields.get(
            common.SEC_WEBSOCKET_EXTENSIONS_HEADER.lower())
        accepted_extensions = []
        if extensions_header is not None and len(extensions_header) != 0:
            accepted_extensions = common.parse_extensions(extensions_header[0])
            # TODO(bashi): Support the new style perframe compression extension.
        for extension in accepted_extensions:
            extension_name = extension.name()
            if (extension_name == common.DEFLATE_STREAM_EXTENSION and
                len(extension.get_parameter_names()) == 0 and
                self._options.get('deflate_stream')=='True'):
                deflate_stream_accepted = True
                continue

            if (extension_name == common.DEFLATE_FRAME_EXTENSION and
                self._options.get('deflate_frame')=='True'):
                deflate_frame_accepted = True
                processor = DeflateFrameExtensionProcessor(extension)
                unused_extension_response = processor.get_extension_response()
                self._options['deflate_frame'] = processor
                continue

            raise ClientHandshakeError(
                'Unexpected extension %r' % extension_name)

        if (self._options.get('deflate_stream') == 'True' and not deflate_stream_accepted):
            raise ClientHandshakeError(
                'Requested %s, but the server rejected it' %
                common.DEFLATE_STREAM_EXTENSION)

        if (self._options.get('deflate_frame') == 'True' and not deflate_frame_accepted):
            raise ClientHandshakeError(
                'Requested %s, but the server rejected it' %
                common.DEFLATE_FRAME_EXTENSION)