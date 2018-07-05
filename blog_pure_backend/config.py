import logging
from logging.handlers import SocketHandler
import os
import struct
import socket
import sys
# noinspection PyProtectedMember
from flask import _app_ctx_stack
from flask import request


LOG_COLLECTOR_HOST = os.getenv('LOG_COLLECTOR_HOST')
DATABASE_URL = os.environ['DATABASE_URL']  # example: "postgresql+pg8000://user:password@host/blog"
SALT = 'sc&#of78'


class UnixDomainSocketHandler(SocketHandler):

    def __init__(self, host, timeout=1):
        """
        Initializes the handler with a specific host address and port.
        When the attribute *closeOnError* is set to True - if a socket error
        occurs, the socket is silently closed and then reopened on the next
        logging call.
        """
        logging.Handler.__init__(self)
        self.host = host
        self.address = host
        self.sock = None
        self.closeOnError = False
        self.retryTime = None
        self.timeout = timeout
        self.producer = __package__.split('.')[0]
        #
        # Exponential backoff parameters.
        #
        self.retryStart = 1.0
        self.retryMax = 30.0
        self.retryFactor = 2.0

    def makeSocket(self, **kwargs):
        """
        A factory method which allows subclasses to define the precise
        type of socket they want.
        """
        result = socket.socket(socket.AF_UNIX)
        result.settimeout(self.timeout)
        try:
            result.connect(self.address)
        except OSError:
            result.close()  # Issue 19182
            raise
        return result

    def serialization(self, record):
        producer = self.producer.encode()
        text = self.format(record).encode()
        return struct.pack('!B', len(producer)) + producer + struct.pack('!L', len(text)) + text

    def emit(self, record):
        """
        Emit a record.
        Serialize the record and writes it to the socket in binary format.
        If there is an error with the socket, silently drop the packet.
        If there was a problem with the socket, re-establishes the
        socket.
        """
        # noinspection PyBroadException
        try:
            self.send(self.serialization(record))
        except Exception:
            self.handleError(record)


class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """

    def filter(self, record):

        record.requestId = request.headers.get("X-Request-Id", '')
        return True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(requestId)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'filters': {
        'contextual': {
            '()': ContextFilter
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['contextual']
        },
        'unix_domain_socket': {
            'level': 'INFO',
            '()': UnixDomainSocketHandler,
            'formatter': 'default',
            'host': LOG_COLLECTOR_HOST,
            'filters': ['contextual']
        }
    },
    'loggers': {
        'werkzeug': {
            'level': 'DEBUG',
        },
        # sqlalchemy.engine:
        # controls SQL echoing. set to logging.INFO for SQL query output, logging.DEBUG for query + result set output.
        # sqlalchemy.dialects:
        # controls custom logging for SQL dialects. See the documentation of individual dialects for details.
        # sqlalchemy.pool:
        # controls connection pool logging. set to logging.INFO or lower to log connection pool checkouts/checkins.
        # sqlalchemy.orm:
        # controls logging of various ORM functions. set to logging.INFO for information on mapper configurations.
        'sqlalchemy.engine': {
            'level': 'WARNING',
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['unix_domain_socket' if LOG_COLLECTOR_HOST else 'console']
    }
}
