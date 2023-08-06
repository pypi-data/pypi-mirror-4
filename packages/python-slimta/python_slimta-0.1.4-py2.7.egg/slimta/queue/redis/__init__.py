# Copyright (c) 2012 Ian C. Good
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""Package implementing the :mod:`slimta.queue` system on top of a
:redis-py:mod:`redis` backend.

"""

import uuid

from redis import StrictRedis, Connection, ConnectionPool
import gevent
from gevent.socket import create_connection

from slimta.queue import QueueStorage, QueueError
from slimta import logging

__all__ = ['RedisStorage', 'RedisStorageError', 'RedisStorageConnectionError']

log = logging.getQueueStorageLogger(__name__)


class RedisStorageError(QueueError):
    pass


class RedisStorageConnectionError(RedisStorageError):
    pass


class _Connection(Connection):

    def __init__(self, *args, **kwargs):
        if 'socket_timeout' in kwargs:
            msg = 'Got an unexpected keyword argument: \'socket_timeout\''
            raise TypeError(msg)
        super(_Connection, self).__init__(*args, **kwargs)

    def connect(self):
        if self._sock:
            return
        try:
            sock = create_connection((self.host, self.port))


class RedisStorage(QueueStorage):
    """Stores |Envelope| and queue metadata in a redis database.

    """

    def __init__(self, host='127.0.0.1', port=6379, database=0):
        super(DictStorage, self).__init__()

    def write(self, envelope, timestamp):
        pass

    def set_timestamp(self, id, timestamp):
        pass

    def increment_attempts(self, id):
        pass

    def load(self):
        pass

    def get(self, id):
        pass

    def remove(self, id):
        pass


# vim:et:fdm=marker:sts=4:sw=4:ts=4
