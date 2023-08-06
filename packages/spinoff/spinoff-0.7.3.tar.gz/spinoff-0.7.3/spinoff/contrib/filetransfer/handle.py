import os
from cStringIO import StringIO

from gevent.event import Event

from spinoff.actor.context import get_context
from spinoff.contrib.filetransfer import constants
from spinoff.contrib.filetransfer.request import Request


class Handle(object):
    """A distributed file handle that represents a physical file sitting somewhere on the network, possibly the same
    machine.

    """
    closed = False
    request = None

    def __init__(self, file_id, server, abstract_path, size):
        self.file_id = file_id
        self.server = server
        self.abstract_path = abstract_path
        self.size = size
        self.buf = []
        self.request = get_context().spawn(Request.using(self.file_id, self.server, self.size))

    def read(self, size=None):
        """Asynchronously reads `size` number of bytes.

        If `size` is not specified, returns the content of the entire file.

        """
        return self._read(size=size)

    def read_into(self, file):
        with open(file, 'wb') as f:
            self._read(into=f)

    def _read(self, size=None, into=None):
        if self.closed:
            raise Exception("Can't read from a File that's been closed")
        assert self.opened
        ret = None
        if not into:
            into = ret = StringIO()
        while size is None or size > 0:
            if size is not None:
                chunk_size = min(constants.DEFAULT_CHUNK_SIZE, size)
                size -= chunk_size
            else:
                chunk_size = constants.DEFAULT_CHUNK_SIZE
            chunk, more_coming = self.request.ask(('next', chunk_size))
            into.write(chunk)  # we're using small chunks, so it's OK to block (if into is a file)
            if not more_coming:
                break
        if hasattr(into, 'flush'):
            into.flush()
        return ret.getvalue() if ret else None

    def close(self):
        if not self.closed:
            self.closed = True
            if self.request:
                self.request.stop()
                self.request = None

    def __del__(self):
        self.close()

    def __getstate__(self):
        raise Exception("file handles cannot be pickled")

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def __repr__(self):
        return "<open file '%s' @ %r>" % (self.abstract_path, self.server)
