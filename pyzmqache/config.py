from pyzmqache.util.config import (load_config, ConfigurationPart,
                                   ConfigurationError)


_DEFAULTS = {
    'network': {
        'cache_port': '5500'
    }
}


def _split_and_strip(values_str, split_on):
    if split_on in values_str:
        return (value.strip() for value in values_str.split(split_on))
    else:
        return values_str,


def _host_tuple(host_str):
    parts = host_str.split(':')

    if len(parts) == 1:
        return parts[0], 80
    elif len(parts) == 2:
        return parts[0], int(parts[1])
    else:
        raise ConfigurationError('Malformed host: {}'.format(host_str))


def load_cache_config(location='/etc/pyrox/zcache.conf'):
    return load_config('pyrox_stock.zcache.config', location, _DEFAULTS)


class NetworkConfiguration(ConfigurationPart):

    @property
    def cache_port(self):
        return self.getint('cache_port')
