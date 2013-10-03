import zmq
import msgpack

from logging import getLogger as get_logger


_LOG = get_logger(__name__)


class CacheClient(object):

    def __init__(self, cfg):
        self._cfg = cfg
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        #self._socket.connect('tcp://127.0.0.1:{}'.format(
        #    self._cfg.network.cache_port))
        self._socket.connect('ipc:///tmp/zcache.fifo')

    def get(self, key):
        msg = dict()

        msg['operation'] = 'get'
        msg['key'] = key

        try:
            self._socket.send(msgpack.packb(msg))

            breply = self._socket.recv()
            reply = msgpack.unpackb(breply)

            if reply['status'] == 'found':
                return reply['value']
        except Exception as ex:
            _LOG.exception(ex)
        return None

    def put(self, key, value):
        msg = dict()

        msg['operation'] = 'put'
        msg['key'] = key
        msg['value'] = value

        try:
            self._socket.send(msgpack.packb(msg))

            breply = self._socket.recv()
            reply = msgpack.unpackb(breply)

            if reply['status'] != 'ok':
                raise Exception(reply['error'])
        except Exception as ex:
            _LOG.exception(ex)

    def delete(self, key):
        msg = dict()

        msg['operation'] = 'del'
        msg['key'] = key

        try:
            self._socket.send(msgpack.packb(msg))

            breply = self._socket.recv()
            reply = msgpack.unpackb(breply)

            if reply['status'] == 'ok':
                return False
            elif reply['status'] == 'deleted':
                return True
            else:
                raise Exception(reply['error'])
        except Exception as ex:
            _LOG.exception(ex)
