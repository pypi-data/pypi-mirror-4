
import errno
import functools
from logging import debug
import logging
import socket
import struct
from tornado import ioloop, iostream
from pywizard.remote.crypt import load_auth_key, load_acceptable_keys, key_checksum, encrypt, sign, verify, decrypt, gen_key_index

# Package format:
# <uchar:encryption_type><uint:checksum><uint:signature_len><uint:data_len><bin:signature>@data@

# encryption types:
ENC_ENCRYPTED_REQUEST = 0  # encrypted request, encrypted by server's public key, signed by clients's private key,
# priveleges are checked aginst server authorized keys
ENC_ENCRYPTED_RESPONSE = 1  # encrypted response, encrypted by client's public key, signed by server's private key
# priveleges are checked by public key of a server

# checksum:
# checksum is checksum for public key faster search

# date format:
# @data@ = <uint:operation_code><bin:operation_data>

# convention for package type in docs:
# package(x,y){z}
# x - encryption type
# y - operation code
# z - textual description of data


# Negotiation:
# 1. Client connects to server and sends package(0,0){client domain name}
# 2. Server checks signature against every key in authorized_keys (checksum is used for quick search of key used)
# 3. If signature is valid, server responses with package(1,0){server public key}

# Note: encryption type 0 may be used only with operation_type 0

class EventHandler(object):

    header = None
    stream = None
    handlerCallback = None

    my_private_key = None
    my_acceptable_keys = None
    other_public_key = None
    name = None

    _data = None
    _header_parsed = False

    _expected_data_len = None

    def __init__(self, name, stream, my_private_key, my_acceptable_keys, handlerCallback, other_public_key=None):
        super(EventHandler, self).__init__()
        self.name = name
        self.stream = stream
        self.my_private_key = my_private_key
        self.my_acceptable_keys = my_acceptable_keys
        self.handlerCallback = handlerCallback
        self.other_public_key = other_public_key

        self.log(debug, 'Handler created')

    def log(self, level, message):
        level('[%s] %s' % (self.name, message))

    def start(self):
        self._data = ''
        self.stream.read_until_close(self.on_data_end, self.on_data)
        self.log(debug, 'Handler initiating conversation.')

    def on_data_end(self, data):
        self.log(debug, 'End of stream.')
        if len(self._data) < self._expected_data_len:
            self.log(debug, 'Wrong len of package. Can not parse.')
        self.stop()

    def on_data(self, data):
        self._data += data

        self.log(debug, 'New portion of data received: %d bytes' % len(data))

        if not self._header_parsed:
            if len(self._data) > 0:
                self.on_package_header(self._data[0:13])

        if len(self._data) == self._expected_data_len:
            self.on_package_data(self._data[13:])

        self.log(debug, 'Expected len is %d. Current len is: %d' % (self._expected_data_len, len(self._data)))

    def on_package_header(self, header_bytes):
        self.log(debug, 'Parsing header')
        self.header = struct.unpack('>BIII', header_bytes)
        encryption_type, checksum, signature_len, data_len = self.header

        self.log(debug, 'Header: %s' % str(self.header))

        self._expected_data_len = signature_len + data_len + 13
        self._header_parsed = True

    def on_package_data(self, data_bytes):
        self.log(debug, 'Parsing body.')

        encryption_type, checksum, signature_len, data_len = self.header
        signature, data = (data_bytes[0:signature_len], data_bytes[signature_len:signature_len + data_len])

        if encryption_type == ENC_ENCRYPTED_REQUEST:
            self.log(debug, 'Checking key for request (server mode).')
            public_keys = self.find_keys_by_checksum(checksum)
            if not public_keys:
                return self.not_authorized('The key with given checksum is not found')

            key_found = self.find_valid_key_by_signature_check(data, signature, public_keys)
            if not key_found:
                return self.not_authorized('Signature is not valid')
            else:
                self.other_public_key = key_found
        else:
            self.log(debug, 'Checking key for response (client mode).')
            if not verify(self.other_public_key, data, signature):
                return self.not_authorized('Signature is not valid')

        operation_code, operation_data = (struct.unpack('>I', data[0:4])[0], data[4:])
        operation_data = decrypt(self.my_private_key, operation_data)

        return self.process_package(encryption_type, operation_code, operation_data)

    def not_authorized(self, message):
        self.log(debug, 'Error: not authorized.')
        self.send_package(502, "not authorized: %s" % message)
        self.stop()
        self.log(debug, 'Stream closed.')

    def send_package(self, encryption_type, operation_code, data):

        self.log(debug, 'composing package(%d){%s} length %d bytes' % (operation_code, data, len(data)))

        """
        Use this message to send outcomming packages

        :param data:
        :return:
        """
        data = encrypt(self.other_public_key, data)

        data = struct.pack('>I', operation_code) + data

        checksum = key_checksum(self.my_private_key.publickey())
        signature = sign(self.my_private_key, data)

        package = struct.pack('>BIII', encryption_type, checksum, len(signature), len(data)) + signature + data
        self.stream.write(package)

        self.log(debug, 'package sent with length of %d bytes' % len(package))

    def find_keys_by_checksum(self, checksum):
        if not checksum in self.my_acceptable_keys:
            return None
        return self.my_acceptable_keys[checksum]

    def find_valid_key_by_signature_check(self, data, signature, public_keys):
        for key in public_keys:
            if verify(key, data, signature):
                return key
        return None

    def process_package(self, encryption_type, operation_code, operation_data):

        if encryption_type == ENC_ENCRYPTED_REQUEST:
            self.log(debug, 'Processing request %s with len of data: %s' % (operation_code, operation_data))

            self.log(debug, 'Executing handler callback')
            (ret_code, ret_data) = self.handlerCallback(operation_code, operation_data)

            self.log(debug, 'Sending response package(%d){%s}' % (ret_code, ret_data))
            self.send_package(ENC_ENCRYPTED_RESPONSE, ret_code, ret_data)

        else:
            self.log(debug, 'Processing response %s with len of data: %s' % (operation_code, operation_data))

            self.log(debug, 'Executing handler callback')
            self.handlerCallback(operation_code, operation_data)
            self.stop()

    def stop(self):
        self.log(debug, 'Stop. Stream closed')
        if not self.stream.closed():
            self.stream.close()


class EventClient(object):

    host = None
    port = None

    server_public_key = None
    on_ready = None

    def __init__(self, server_public_key, my_private_key,
                 my_acceptable_keys=None, host='127.0.0.1', port=8288):

        super(EventClient, self).__init__()

        self.host = host
        self.port = port

        self.my_private_key = my_private_key or load_auth_key()

        if my_acceptable_keys is None:
            my_acceptable_keys = load_acceptable_keys()
        self.my_acceptable_keys = gen_key_index(my_acceptable_keys)

        self.server_public_key = server_public_key

    def send(self, operation_code, data, on_ready=None):

        def on_connection_ready():
            handler = EventHandler(
                name='client',
                stream=stream,
                my_private_key=self.my_private_key,
                my_acceptable_keys=self.my_acceptable_keys,
                handlerCallback=on_ready,
                other_public_key=self.server_public_key
            )
            handler.send_package(ENC_ENCRYPTED_REQUEST, operation_code, data)
            handler.start()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = iostream.IOStream(s)
        stream.connect((self.host, self.port), on_connection_ready)


class EventListener(object):

    handlers = None
    handlerCallback = None

    my_private_key = None
    my_acceptable_keys = None
    socket = None

    def __init__(self, handlerCallback, my_private_key=None, my_acceptable_keys=None):
        super(EventListener, self).__init__()
        self.my_private_key = my_private_key or load_auth_key()
        self.my_acceptable_keys = gen_key_index(my_acceptable_keys or load_acceptable_keys())
        self.handlerCallback = handlerCallback

    def listen(self, port=8288, host='127.0.0.1'):

        logging.debug('Starting server on %s:%s', host, port)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind((host, port))
        sock.listen(5000)

        self.socket = sock

        self.handlers = []

        io_loop = ioloop.IOLoop.instance()
        callback = functools.partial(self.connection_ready, sock)
        io_loop.add_handler(sock.fileno(), callback, io_loop.READ)

    def stop(self):
        self.socket.close()

    def connection_ready(self, sock, fd, events):
        while True:
            try:
                connection, address = sock.accept()

                logging.debug('Accepted connection from %s', address)

            except socket.error, e:
                if e[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                return
            connection.setblocking(0)
            stream = iostream.IOStream(connection)

            handler = EventHandler(
                name='%s:%s' % tuple(address),
                stream=stream,
                my_private_key=self.my_private_key,
                my_acceptable_keys=self.my_acceptable_keys,
                handlerCallback=self.handlerCallback
            )

            self.handlers.append(handler)

            handler.start()
