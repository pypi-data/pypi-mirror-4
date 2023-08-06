import logging
from Crypto import Random
from Crypto.PublicKey import RSA
import time
from tornado import ioloop

from pywizard.remote.transport import EventListener, EventClient

rng = Random.new().read
rsa_key_client = RSA.generate(1024, rng)
rsa_key_server = RSA.generate(1024, rng)

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)


def test_simple_transport():

    def reverse(code, data):
        return code + 3, data[::-1]

    listener = EventListener(
        handlerCallback=reverse,
        my_private_key=rsa_key_server,
        my_acceptable_keys=[rsa_key_client.publickey()])
    listener.listen()

    io_loop = ioloop.IOLoop.instance()

    result = {}

    def check_answer(code, data):
        result['code'] = code
        result['data'] = data
        listener.stop()
        io_loop.add_callback(io_loop.stop)

    client = EventClient(server_public_key=rsa_key_server.publickey(),
                         my_private_key=rsa_key_client, my_acceptable_keys=[])

    client.send(5, 'foo', check_answer)

    try:
        def kill_loop():
            listener.stop()
            io_loop.stop()
        io_loop.add_timeout(time.time() + 5, kill_loop)
        io_loop.start()

        assert result['code'] == 8
        assert result['data'] == 'oof'

    except KeyboardInterrupt:
        io_loop.stop()
        print "exited cleanly"


def test_transport_performance():

    def reverse(code, data):
        return code + 3, data[::-1]

    listener = EventListener(
        handlerCallback=reverse,
        my_private_key=rsa_key_server,
        my_acceptable_keys=[rsa_key_client.publickey()])
    listener.listen()

    io_loop = ioloop.IOLoop.instance()

    results = []
    iteration_cnt = 25

    def check_answer(code, data):
        results.append((code, data))

        if len(results) == iteration_cnt:
            listener.stop()
            io_loop.add_callback(io_loop.stop)

    for i in range(0, iteration_cnt):
        client = EventClient(server_public_key=rsa_key_server.publickey(),
                             my_private_key=rsa_key_client, my_acceptable_keys=[])

        client.send(5, 'foo', check_answer)

    try:
        def kill_loop():
            listener.stop()
            io_loop.stop()
        io_loop.add_timeout(time.time() + 3, kill_loop)
        io_loop.start()

        assert len(results) > (iteration_cnt - 5)

    except KeyboardInterrupt:
        io_loop.stop()
        print "exited cleanly"
