"""
Tinman Test Application

"""
import datetime
import logging
import tinman

from tornado import web

from tinman import handlers
from tinman.handlers import redis

LOGGER = logging.getLogger(__name__)

CONFIG = {'Application': {'debug': True,
                          'xsrf_cookies': False},
          'HTTPServer': {'no_keep_alive': False,
                         'ports': [8000],
                         'xheaders': False},
          'Logging': {'loggers': {'tinman': {'propagate': True,
                                            'level': 'DEBUG'}},
                      'formatters': {'verbose': ('%(levelname) -10s %(asctime)s'
                                                 ' %(name) -30s %(funcName) '
                                                 '-25s: %(message)s')},
                      'filters': {'tinman': 'tinman'},
                      'handlers': {'console': {'formatter': 'verbose',
                                               'filters': ['tinman'],
                                               'debug_only': True,
                                               'class': 'logging.StreamHandler',
                                               'level': 'DEBUG'},
                                   'file': {'delay': False,
                                            'mode': 'a',
                                            'encoding': 'UTF-8',
                                            'formatter': 'verbose',
                                            'filters': ['tinman'],
                                            'class': 'logging.FileHandler',
                                            'filename': '/tmp/tinman.log'}}},
          'Routes': [("/", "tinman.test.DefaultHandler")]}


class DefaultHandler(handlers.redis.RedisRequestHandler,
                     handlers.session.SessionRequestHandler):

    @web.asynchronous
    def get(self, *args, **kwargs):

        self._session.username = 'gmr'
        self._redis_set('last_request', datetime.datetime.now().isoformat())

        # Send a JSON string for our test
        self.write({'message': 'Hello World',
                    'request': {'method': self.request.method,
                                'protocol': self.request.protocol,
                                'path': self.request.path,
                                'query': self.request.query,
                                'remote_ip': self.request.remote_ip,
                                'version': self.request.version},
                    'session': self._session.as_dict(),
                    'tinman': {'version':  tinman.__version__}})
        self.finish()
