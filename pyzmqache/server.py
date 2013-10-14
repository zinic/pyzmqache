import zmq
import time
import msgpack
import threading

from pyzmqache.log import get_logger


_LOG = get_logger(__name__)
_DEFAULT_CACHE_TTL = 120


class CacheItem(object):

    def __init__(self, value, expires_at):
        self.expires_at = expires_at
        self.value = value


class SimpleCache(object):

    def __init__(self):
        self._lock = threading.RLock()
        self._cache = dict()

    def stop(self):
        self._cache_sweeper.cancel()

    def sweep(self):
        remove_keys = list()
        with self._lock:
            now = time.time()

            for key, value in self._cache.iteritems():
                if now > value.expires_at:
                    remove_keys.append(key)
            for remove_key in remove_keys:
                del self._cache[remove_key]

    def get(self, key):
        item = None
        with self._lock:
            item = self._cache.get(key)
        return item.value if item else None

    def put(self, key, value, ttl):
        with self._lock:
            now = time.time()
            self._cache[key] = CacheItem(value, now + ttl)

    def delete(self, key):
        deleted = False
        with self._lock:
            deleted = self._cache.pop(key, None) is not None
        return deleted


class CacheServer(object):

    def __init__(self):
        self._cache = SimpleCache()
        self._is_running = False
        self._context = None
        self._socket = None

        # Start the TTL sweeper
        self._cache_sweeper = threading.Thread(target=self._sweep_cache)

    def _sweep_cache(self):
        """
        Timer method for sweeping the cache of TTL expired items.
        """
        while self._is_running:
            self._cache.sweep()
            time.sleep(1)

    def start(self, cfg):
        # Mark that the server is running
        self._is_running = True

        # Start the cache TTl sweeper
        self._cache_sweeper.start()

        # Bind ZMQ
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(cfg.connection.cache_uri)

        # Continue running until told otherwise
        while self._is_running:
            try:
                bmsg = self._socket.recv()
                self._handle_msg(msgpack.unpackb(bmsg))
            except Exception as ex:
                _LOG.exception(ex)
                break

    def stop(self):
        self._is_running = False
        self._context.destroy()

    def _handle_msg(self, msg):
        operation = msg['operation']

        reply = {'status': 'error'}

        if operation == 'get':
            self._on_get(reply, msg['key'])
        elif operation == 'put':
            self._on_put(
                reply,
                msg['key'],
                msg['value'],
                msg.get('ttl', _DEFAULT_CACHE_TTL))
        elif operation == 'delete':
            self._on_delete(reply, msg['key'])

        if operation == 'halt':
            self.stop()
        else:
            self._socket.send(msgpack.packb(reply))

    def _on_get(self, reply, key):
        cached_obj = self._cache.get(key)

        if cached_obj:
            reply['status'] = 'found'
            reply['value'] = cached_obj
        else:
            reply['value'] = None

    def _on_put(self, reply, key, value, ttl):
        self._cache.put(key, value, ttl)
        reply['status'] = 'ok'

    def _on_delete(self, reply, key):
        if self._cache.delete(key):
            reply['status'] = 'deleted'
        else:
            reply['status'] = 'not_found'
