import random
import tempfile

from gevent.queue import Queue
from nose.tools import eq_

from spinoff.actor import Actor
from spinoff.actor.node import Node
from spinoff.contrib.filetransfer.filetransfer import FileRef
from spinoff.util.python import deferred_cleanup
from spinoff.util.logging import dbg
from spinoff.util.testing.actor import wrap_globals


@deferred_cleanup
def test_with_no_remoting(defer):
    random_data = str(random.randint(0, 10000000000))

    node = Node('localhost:20001', enable_remoting=False)
    defer(node.stop)

    f_src = tempfile.NamedTemporaryFile()
    f_src.write(random_data)
    f_src.flush()

    ref = FileRef.publish(f_src.name, node)

    f_dst = tempfile.NamedTemporaryFile(mode='r')
    ref.fetch(path=f_dst.name, context=node)
    with open(f_dst.name) as f_dst_:
        eq_(random_data, f_dst_.read())

    f_dst_repeat = tempfile.NamedTemporaryFile(mode='r')
    ref.fetch(path=f_dst_repeat.name, context=node)
    with open(f_dst_repeat.name) as f_dst_repeat_:
        eq_(random_data, f_dst_repeat_.read())


@deferred_cleanup
def test_with_no_remoting_inside_actors(defer):
    random_data = str(random.randint(0, 10000000000))

    f_src = tempfile.NamedTemporaryFile()
    f_src.write(random_data)
    f_src.flush()

    node = Node('localhost:20001', enable_remoting=False)
    defer(node.stop)

    received_data = Queue()

    class FileSrc(Actor):
        def run(self, dst):
            ref = FileRef.publish(f_src.name, self.node)
            dst << ref
            dst << ref

    class FileDst(Actor):
        def receive(self, ref):
            f_dst = tempfile.NamedTemporaryFile(mode='r')
            ref.fetch(path=f_dst.name, context=node)
            with open(f_dst.name) as f_dst_:
                received_data.put(f_dst_.read())

    # f_dst_repeat = tempfile.NamedTemporaryFile(mode='r')
    # ref.fetch(path=f_dst_repeat.name, context=node)
    # with open(f_dst_repeat.name) as f_dst_repeat_:
    #     eq_(random_data, f_dst_repeat_.read())

    dst = node.spawn(FileDst)
    node.spawn(FileSrc.using(dst))

    eq_(received_data.get(), random_data)
    eq_(received_data.get(), random_data)


wrap_globals(globals())
