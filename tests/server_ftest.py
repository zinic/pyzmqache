import time
import mock
import unittest

from multiprocessing import Process

from pyzmqache import CacheClient, CacheServer


class WhenTestingCache(unittest.TestCase):

    def setUp(self):
        cfg = mock.MagicMock()
        cfg.network.cache_port = 5000

        server_instance = CacheServer(cfg)

        self.server_process = Process(target=server_instance.start)
        self.server_process.start()

        self.client = CacheClient(cfg)

    def tearDown(self):
        self.server_process.terminate()

    def test_performance(self):
        expected = { 'msg_kind': 'test', 'value': 'magic' }

        now = time.time()
        iterations = 0

        while iterations <= 100000:
            self.client.put('test', expected)

            value = self.client.get('test')
            #self.assertEqual(expected, value)

            self.client.delete('test')

            value = self.client.get('test')
            #self.assertIsNone(value)
            iterations += 1

        duration = time.time() - now
        calls = iterations * 4

        print('Ran {} times in {} seconds for {} calls per second.'.format(
            iterations,
            duration,
            calls / float(duration)))

if __name__ == '__main__':
    unittest.main()
