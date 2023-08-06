# coding: utf-8
from __future__ import print_function

from spinoff.actor.props import Props


class Actor(object):
    """Description here.

    __init__ should not attempt to access `self.ref` or `self.parent` as this are available only on an already
    initialized actor instance. If your initialization routine depends on either of those, use `pre_start` instead.

    """
    @classmethod
    def using(cls, *args, **kwargs):
        return Props(cls, *args, **kwargs)

    __cell = None  # make it really private so it's hard and unpleasant to access the cell
    args, kwargs = (), {}

    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

    receive = run = None

    def spawn(self, factory, name=None):
        return self.__cell.spawn_actor(factory, name)

    def get(self, *patterns):
        return self.__cell.get(*patterns)

    def flush(self):
        self.__cell.flush()

    # def escalate(self):
    #     self.__cell.escalate()

    @property
    def children(self):
        return self.__cell.children

    def watch(self, actor, *actors, **kwargs):
        return self.__cell.watch(actor, *actors, **kwargs)

    def unwatch(self, actor, *actors):
        self.__cell.unwatch(actor, *actors)

    @property
    def ref(self):
        return self.__cell.ref

    @property
    def root(self):
        return self.__cell.root

    @property
    def node(self):  # pragma: no cover
        """Returns a reference to the `Node` whose hierarchy this `Actor` is part of."""
        return self.root.node

    def _set_cell(self, cell):
        self.__cell = cell

    # TODO: this is a potential spot for optimisation
    def send(self, *args, **kwargs):
        """Alias for self.ref.send"""
        self.ref.send(*args, **kwargs)

    def __lshift__(self, message):  # pragma: no cover
        self.ref.send(message)
        return self

    def stop(self):
        self.ref.stop()

    def __eq__(self, other):
        return other is self or self.ref == other

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "<impl:%s>" % (self.ref.uri.path,)
