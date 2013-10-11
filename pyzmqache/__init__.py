from .client import CacheClient
from .server import CacheServer
from .config import load_cache_config


def create_client(conf_location=None):
    cfg = load_cache_config(conf_location)
    return CacheClient(cfg)


def create_server(conf_location=None):
    cfg = load_cache_config(conf_location)
    return CacheServer(cfg)
