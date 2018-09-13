import logging
from logging.handlers import SocketHandler
import os
import struct
from flask import request, has_request_context


LOG_SEND_HOST = os.getenv('LOG_SEND_HOST')
LOG_SEND_PORT = os.getenv('LOG_SEND_PORT') and int(os.getenv('LOG_SEND_PORT'))
DATABASE_URL = os.environ['DATABASE_URL']  # example: "postgresql+pg8000://user:password@host/blog"
SALT = 'sc&#of78'


class StreamSocketHandler(SocketHandler):

    def __init__(self, host, port=None, *, producer=None):
        """
        Initializes the handler with a specific host address and port.

        When the attribute *closeOnError* is set to True - if a socket error
        occurs, the socket is silently closed and then reopened on the next
        logging call.
        """
        super().__init__(host, port)
        self.producer = producer or __package__.split('.')[0]

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

        record.requestId = request.headers.get("X-Request-Id", '') if has_request_context() else ''
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
        'stream_socket': {
            'level': 'INFO',
            '()': StreamSocketHandler,
            'formatter': 'default',
            'host': LOG_SEND_HOST,
            'port': LOG_SEND_PORT,
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
        'handlers': ['stream_socket' if LOG_SEND_HOST else 'console']
    }
}
