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

    def _send(self, msg):
        try:
            self._socket.send(msgpack.packb(msg))

            breply = self._socket.recv()
            return msgpack.unpackb(breply)
        except Exception as ex:
            _LOG.exception(ex)
        return None

    def get(self, key):
        msg = dict()

        msg['operation'] = 'get'
        msg['key'] = key

        reply = self._send(msg)
        status = reply.get('status') if reply else None

        return reply['value'] if status and status == 'found' else None

    def put(self, key, value, ttl=None):
        msg = dict()

        msg['operation'] = 'put'
        msg['key'] = key
        msg['value'] = value

        if ttl:
            msg['ttl'] = ttl

        reply = self._send(msg)
        status = reply.get('status') if reply else None

        if status and status != 'ok':
            raise Exception(str(reply.get('error')))

    def delete(self, key):
        msg = dict()

        msg['operation'] = 'delete'
        msg['key'] = key

        reply = self._send(msg)
        status = reply.get('status') if reply else None

        if status:
            if status not in ('deleted', 'not_found'):
                raise Exception(str(reply.get('error')))

            return status == 'deleted'
