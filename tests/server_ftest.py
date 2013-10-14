import time
import mock
import unittest

from multiprocessing import Process

from pyzmqache import CacheClient, CacheServer
from pyzmqache.server import CacheItem, SimpleCache


class whenTestingCacheItem(unittest.TestCase):

    def setup(self):
        self.cache_item = CacheItem('value', 3000)

    def cache_item_ttl(self):
        self.assertEqual(self.cache_item.value, 'value')

    def cache_item_ttl(self):
        self.assertEqual(self.cache_item.expires_at, 3000)


class whenTestingSimpleCache(unittest.TestCase):

    def setUp(self):
        self.simpleCache = SimpleCache()

    def test_simple_cache_get_result_none_key(self):
        self.assertIsNone(self.simpleCache.get(None))

    def test_simple_cache_get_result_none_existent(self):
        self.assertIsNone(self.simpleCache.get('key1234'))

    def test_simple_cache_get_result_value(self):
        self.simpleCache.put('key', '12345', time.time())
        self.assertEqual(self.simpleCache.get('key'), '12345')

    def test_simple_cache_put_key_value(self):
        self.simpleCache.put('key', '12345', time.time())
        self.assertEqual(self.simpleCache.get('key'), '12345')


class WhenTestingCache(unittest.TestCase):

    def setUp(self):
        cfg = mock.MagicMock()
        cfg.connection.cache_uri = 'ipc:///tmp/zcache.fifo'

        server_instance = CacheServer()
        self.server_instance = server_instance

        def profile_server():
            server_instance
            cfg

            import cProfile
            cProfile.runctx('server_instance.start(cfg)', globals(), locals())

        # Uncomment to profile the server
        #self.server_process = Process(target=profile_server)

        self.server_process = Process(
            target=server_instance.start,
            args=(cfg, ))
        self.server_process.start()

        self.client = CacheClient(cfg)

    def tearDown(self):
        self.client.halt()
        self.server_process.join()

    def test_ttls(self):
        expected = {'msg_kind': 'test', 'value': 'magic'}

        now = time.time()
        self.client.put('test', expected, 2)

        value = self.client.get('test')
        self.assertEqual(expected, value)

        time.sleep(5)

        value = self.client.get('test')
        self.assertIsNone(value)

    def test_performance(self):
        expected = {'msg_kind': 'test', 'value': 'magic'}

        now = time.time()
        iterations = 0

        while iterations <= 1000:
            self.client.put('test', expected)

            value = self.client.get('test')
            self.assertEqual(expected, value)

            self.client.delete('test')

            value = self.client.get('test')
            self.assertIsNone(value)
            iterations += 1

        duration = time.time() - now
        calls = iterations * 4

        print('Ran {} times in {} seconds for {} calls per second.'.format(
            iterations,
            duration,
            calls / float(duration)))

if __name__ == '__main__':
    unittest.main()
