import zmq
import msgpack

from logging import getLogger as get_logger


_LOG = get_logger(__name__)
_HALT_MSG = {'operation': 'halt'}
_DEFAULT_TTL = 120


class CacheClient(object):

    def __init__(self, cfg):
        self._cfg = cfg
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(self._cfg.connection.cache_uri)

    def _send(self, msg):
        self._socket.send(msgpack.packb(msg))

    def _request(self, msg):
        try:
            self._send(msg)

            breply = self._socket.recv()
            return msgpack.unpackb(breply)
        except Exception as ex:
            _LOG.exception(ex)
        return None

    def halt(self):
        self._send(_HALT_MSG)

    def get(self, key):
        msg = {
            'operation': 'get',
            'key': key}

        reply = self._request(msg)
        status = reply.get('status') if reply else None

        if status and status == 'found':
            return msgpack.unpackb(reply['value'])
        return None

    def put(self, key, value, ttl=_DEFAULT_TTL):
        msg = {
            'operation': 'put',
            'key': key,
            'ttl': ttl,
            'value': msgpack.packb(value)}

        reply = self._request(msg)
        status = reply.get('status') if reply else None

        if status and status != 'ok':
            raise Exception(str(reply.get('error')))

    def delete(self, key):
        msg = {
            'operation': 'delete',
            'key': key
        }

        reply = self._request(msg)
        status = reply.get('status') if reply else None

        if status:
            if status not in ('deleted', 'not_found'):
                raise Exception(str(reply.get('error')))

            return status == 'deleted'
