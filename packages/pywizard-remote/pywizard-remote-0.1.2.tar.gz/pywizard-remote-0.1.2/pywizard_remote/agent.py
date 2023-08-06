from pywizard.remote.transport import EventListener


def reverse(code, data):
    return code + 3, data[::-1]

listener = EventListener(
    handlerCallback=reverse)
listener.listen()


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