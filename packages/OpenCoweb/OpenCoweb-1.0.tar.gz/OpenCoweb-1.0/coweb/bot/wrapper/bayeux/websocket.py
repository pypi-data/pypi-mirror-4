'''
Copyright (c) The Dojo Foundation 2011. All Rights Reserved.
Copyright (c) IBM Corporation 2008, 2011. All Rights Reserved.
'''
# std lib
import os
import uuid
import logging
import random
import asynchat
import asyncore
import urllib.parse
import struct
import socket
import hashlib
import base64
import array

log = logging.getLogger('websocket.client')

'''
WebSocketClient partially implements WebSockes version 13 (RFC 6455)

What works:
 * Sending frames form client to server supports non-fragmented messages.
   See helper functions generate_ws_frame, etc below.

Partially works:
 * Client only accepts non-fragmented messages (FIN=1). See
   _on_start_frame/_on_end_frame.
'''

# max defined by spec
MAXINT = 4294967295
# schemes defined by spec
SCHEMES = ['ws', 'wss']

# make urlparse websocket protocol aware
urllib.parse.uses_netloc.extend(SCHEMES)
urllib.parse.uses_query.extend(SCHEMES)
urllib.parse.uses_fragment.extend(SCHEMES)

def generate_frame_key():
    return os.urandom(4)

def apply_mask(data, key):
    k  = [i for i in key]
    r = array.array("B", data)
    for i in range(len(data)):
        r[i] ^= k[i % 4]
    return r.tostring()

_OP_CONTINUATION = 0x0
_OP_TEXT = 0x1
_OP_BINARY = 0x2
_OP_CLOSE = 0x8
_OP_PING = 0x9
_OP_PONG = 0xa
# See http://tools.ietf.org/html/rfc6455#section-5.2
def generate_ws_frame(fin, rsv1, rsv2, rsv3, op, mask, data):
    # data is "normal" string
    # TODO handle _OP_BINARY
    data = data.encode('utf-8')
    if mask:
        key = generate_frame_key()
        data = apply_mask(data, key)
    length = len(data)
    dta = struct.pack("!B", fin<<7 | rsv1<<6 | rsv2<<5 | rsv3<<4 | op)
    if 0 <= length and length <= 125:
        dta += struct.pack("!B", mask<<7 | length)
    elif length <= (1 << 16):
        dta += struct.pack("!B", mask<<7 | 126)
        dta += struct.pack("!H", length)
    else:
        dta += struct.pack("!B", mask<<7 | 127)
        dta += struct.pack("!Q", length)
    if mask:
        dta += key
    return dta + data

class WebSocketURL(object):
    '''Represents parts of a WebSocket URL.'''
    def __init__(self, host, port, resource, secure):
        self.host = host
        self.port = port
        self.resource = resource
        self.secure = secure

    def __str__(self):
        url = 'wss' if self.secure else 'ws'
        url += '://' + self.host
        if (not self.secure and self.port != 80) or \
        (self.secure and self.port != 443):
            url += ':' + str(self.port)
        return url + self.resource

class WebSocketClient(asynchat.async_chat):
    '''Asynchat-based bot wrapper talking Bayeux over WebSocket.'''
    def __init__(self, uri):
        asynchat.async_chat.__init__(self)
        # validate the uri
        self._url = self._validate_uri(uri)
        # response header fields
        self._fields = {}
        # origin for later comparison
        self._origin = socket.gethostname()

        # current state
        self._handler = self._on_request_line

        # start by listening for header response
        self.set_terminator(b'\x0a')
        # connect to server
        self._inBuffer = []
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (self._url.host, self._url.port)
        self.connect(addr)

    def _validate_uri(self, uri):
        '''Parse and validate the connection URL.'''
        uri = urllib.parse.urlparse(uri)

        # 3.1 3: validate scheme
        if uri.scheme not in SCHEMES:
            raise ValueError('invalid uri scheme')
        # 3.1 4: validate no fragment
        if uri.fragment:
            raise ValueError('fragment not allowed')
        # 3.1 5: determine secure
        secure = (uri.scheme == 'wss')
        # 3.1 6: lowercase host
        host = uri.netloc.lower()
        # 3.1 7-8: default ports
        args = uri.netloc.split(':')
        if len(args) == 1:
            port = 80 if secure else 443
        else:
            host = args[0]
            port = int(args[1])
        # 3.1 9-10: resource name
        resource = uri.path or '/'
        # 3.1 11: append query
        if uri.query:
            resource += '?' + uri.query

        # build web socket url object
        return WebSocketURL(host, port, resource, secure)

    def handle_close(self):
        '''Called when the server closes the connection.'''
        self.close()
        try:
            self.on_ws_close()
        except Exception:
            logging.exception('on_ws_close')

    # We used to use http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76
    # Instead, we want a newer version.
    def handle_connect(self):
        '''Called when the client connects to the server.'''
        # @todo: 4.1 4: tls handshake if secure

        hostport = self._url.host.lower()
        if (not self._url.secure and self._url.port != 80) or \
                (self._url.secure and self._url.port != 443):
            hostport += ':' + str(self._url.port)

        self.push(('GET %s HTTP/1.1\r\n' % self._url.resource).encode('utf-8'))
        fields = []
        fields.append('Host: ' + hostport)
        fields.append('Upgrade: WebSocket')
        fields.append('Connection: Upgrade')
        fields.append('Sec-WebSocket-Version: 13')
        key, self._accept_key = self._get_keys()

        fields.append('Sec-WebSocket-Key: '+key)
        fields.append('Origin: '+self._origin)
        random.shuffle(fields)
        self.push('\r\n'.join(fields).encode('utf-8'))
        self.push(b'\r\n\r\n')

    def _get_keys(self):
        ''' Return a randomly generated Sec-WebSocket-Key and the expected
            Sec-WebSocket-Accept key the server should send us. '''
        key = b'1234567890123456'
        key = base64.b64encode(key).decode('utf-8')
        skey = (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode('utf-8')
        skey = base64.b64encode(hashlib.sha1(skey).digest()).decode('utf-8')
        return key, skey

    def handle_error(self):
        raise

    def collect_incoming_data(self, data):
        # Data is arbitrary byte data. Might or might not be a unicode string.
        # We let the handlers themselves decide if the data should be converted
        # to a unicode string.
        '''Called when data is received.'''
        self._inBuffer.append(data)

    def found_terminator(self):
        '''Called when a complete "chunk" is received.'''
        self._handler(b''.join(self._inBuffer))
        self._inBuffer = []

    def _on_request_line(self, field):
        # We really want the unicode string, not byte array.
        field = field.decode('utf-8')
        '''Called to handle the request line from the server.'''
        # 4.1 28: validate field with terminator
        field += '\x0a'
        if len(field) < 7 or field[-2:] != '\r\n' or field.count(' ') < 2:
            # abort connect
            self.close()
            raise ValueError('invalid request line')
        # 4.1 29: get code
        start = field.find(' ')
        end = field.find(' ', start+1)
        code = field[start+1:end]
        # 4.1 30: validate code
        # 4.1 31: abort if not 101
        # @todo: maybe handle 407 one day for proxy auth
        # @todo: check for bytes in range 0x30 to 0x39
        if code != '101':
            pass
            self.close()
            raise ValueError('response code: ' + code)

        # process header fields next
        self._handler = self._on_header_field
        # read a header field
        self.set_terminator(b'\r\n')

    def _on_header_field(self, field):
        # We really want the unicode string, not byte array.
        field = field.decode('utf-8')
        '''Called to handle a header line from the server.'''
        # 4.1 34-40: process headers, watching for malformed with \n
        if not field:
            # skip to processing headers
            self._on_process_fields()
            return
        # make sure no stray \r or \n
        if field.find('\r') > -1 or field.find('\n') > -1:
            # abort, invalid header
            self.close()
            raise ValueError('invalid header: ' + field)
        # store field, let exceptions disconnect us
        # @todo: have to close on exception?
        name, value = field.split(':', 1)
        name = name.strip().lower()
        value = value.strip()
        # store field for later processing
        # @todo: this takes last name encountered if dupes, spec says allow
        #   one and only one
        self._fields[name] = value

    def _on_process_fields(self):
        '''Called to process received header fields.'''
        # 4.1 41: check required fields
        required = {
            'upgrade' : 'websocket',
            'connection' : 'upgrade',
            'sec-websocket-accept' : self._accept_key
            }
        # @todo: add sec-websocket-protocol header if protocol was set
        for rname, rvalue in iter(required.items()):
            try:
                value = self._fields[rname]
            except KeyError:
                # missing required
                self.close()
                raise ValueError('missing required header: ' + rname)
            # connection to be compared in lower case, oi
            if rname == 'connection':
                value = value.lower()
            if value != rvalue:
                # wrong value
                self.close()
                raise ValueError('wrong header value: ' + value)
        self._handler = self._on_start_frame
        self.set_terminator(2)
        # invoke bot websocket open method
        try:
            self.on_ws_open()
        except Exception:
            logging.exception('on_ws_open')
        return

    def _on_start_frame(self, dta):
        '''Called when receiving the start of a frame.'''
        # Receiving a frame proceeds as follows:
        # 1. Receive 2 bytes. The second byte has payload length info:
        #    a) If this byte has the entire payload length, goto step 2.
        #    b) Else, read any aditional bytes to determine payload length.
        # 2. Read payload data. We're done.
        b1 = dta[0]
        b2 = dta[1]
        self._frame_len = b2

        op = b1 & 0x0f
        self._frame_op = op
        # What kind of message frame?
        if _OP_CONTINUATION == op:
            self.close()
            raise Exception("WS: we don't support continuation frames")
        elif _OP_BINARY == op:
            self.close()
            raise Exception("WS: we don't support binary frames")

        if b1 & 0x80 != 0x80:
            self.close()
            # TODO might need to support fragmented messages
            raise Exception("WS: FIN==0, we don't support fragmented messages")

        # Servers must NOT mask frames, so we assume byte 2 has MSB == 0.
        if b2 < 126:
            self._handler = self._on_end_frame
            self.set_terminator(b2)
        elif b2 == 126:
            self._handler = self._on_start_frame_more
            self.set_terminator(2)
        else:
            self._handler = self._on_start_frame_more
            self.set_terminator(8)
        # look for end of frame

    def _on_start_frame_more(self, dta):
        # This is called when we must read more bytes to determine payload
        # length.
        if 8 == len(dta):
            self._frame_len = struct.unpack("!Q", dta)[0]
        if 2 == len(dta):
            self._frame_len = struct.unpack("!H", dta)[0]
        self._handler = self._on_end_frame
        self.set_terminator(self._frame_len)

    def _on_end_frame(self, data):
        '''Called when receiving the end of a frame.'''

        op = self._frame_op
        if _OP_TEXT == op:
            try:
                self.on_ws_message(data.decode('utf-8'))
            except Exception:
                logging.exception('on_ws_message')
        elif _OP_PING == op:
            self._send_pong()
        elif _OP_PONG == op:
            print(" PONG ")
            pass # Nothing to do.
        elif _OP_CLOSE == op:
            self.close()
            return

        # look for start of next frame
        self._handler = self._on_start_frame
        self.set_terminator(2)

    def _send_ping(self):
        dta = generate_ws_frame(1, 0, 0, 0, _OP_PING, 1, '')
        self.push(dta)

    def _send_pong(self):
        dta = generate_ws_frame(1, 0, 0, 0, _OP_PONG, 1, '')
        self.push(dta)

    def send_ws(self, data):
        '''Sends data as a websocket frame.'''
        # Always send in one frame, text data.
        dta = generate_ws_frame(1, 0, 0, 0, _OP_TEXT, 1, data)
        self.push(dta)

    def on_ws_open(self):
        '''Callback for WebSocket open.'''
        pass

    def on_ws_message(self, data):
        '''Callback for WebSocket message.'''
        pass

    def on_ws_close(self):
        '''Callback for WebSocket close.'''
        pass

