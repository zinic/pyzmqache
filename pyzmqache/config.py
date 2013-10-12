from pyzmqache.util.config import (load_config, ConfigurationPart,
                                   ConfigurationError)


_DEFAULTS = {
    'connection': {
        'cache_uri': 'ipc:///tmp/pyzmqache.fifo'
    }
}


def load_cache_config(location='/etc/pyzmqache/cache.conf'):
    return load_config('pyzmqache.config', location, _DEFAULTS)


class LoggingConfiguration(ConfigurationPart):
    """
    Class mapping for the Pyrox logging configuration section.
    ::
        # Logging related options.
        [logging]
    """
    @property
    def console(self):
        """
        Returns a boolean representing whether or not Pyrox should write to
        stdout for logging purposes. This value may be either True of False. If
        unset this value defaults to False.
        ::
            console = True
        """
        return self.get('console')

    @property
    def logfile(self):
        """
        Returns the log file the system should write logs to. When set, Pyrox
        will enable writing to the specified file for logging purposes If unset
        this value defaults to None.
        ::
            logfile = /var/log/pyrox/pyrox.log
        """
        return self.get('logfile')

    @property
    def verbosity(self):
        """
        Returns the type of log messages that should be logged. This value may
        be one of the following: DEBUG, INFO, WARNING, ERROR or CRITICAL. If
        unset this value defaults to WARNING.
        ::
            verbosity = DEBUG
        """
        return self.get('verbosity')


class ConnectionConfiguration(ConfigurationPart):
    """
    Class mapping for the connection configuration section.
    ::

        # Connection related options.
        [conncetion]
    """

    @property
    def cache_uri(self):
        """
        Returns a string representing the caching connection URI. This URI
        should be the same on both the client and the server.
        ::

            # Use a lower latency UNIX socket instead of a TCP socket if
            # connections will all be local to this machine (i.e. a pool of
            # multiprocess workers utilizing the same cache.
            cache_uri = ipc:///tmp/zcache.fifo

            # Use a TCP socket if connections to the cache if the cache
            # is not hosted on the local host or if UNIX sockets are not
            # appropriate for use.
            cache_uri = tcp://127.0.0.1:5000
        """
        return self.getint('cache_uri')
