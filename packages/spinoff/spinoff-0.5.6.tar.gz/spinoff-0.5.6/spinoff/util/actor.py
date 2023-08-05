from __future__ import print_function

import functools
import gc
import inspect
import sys

from nose.twistedtools import deferred
from twisted.internet.defer import inlineCallbacks, DebugInfo, setDebugging, returnValue

from spinoff.actor import Actor, Node
from spinoff.actor.events import Events
from spinoff.actor.remoting import HubWithNoRemoting
from spinoff.util.async import _process_idle_calls, _idle_calls
from spinoff.util.testing import ErrorCollector, Unclean
from spinoff.util.logging import dbg


def TestNode():
    return Node(hub=HubWithNoRemoting())


def wrap_globals(globals):
    """Ensures that errors in actors during tests don't go unnoticed."""

    def wrap(fn):
        if inspect.isgeneratorfunction(fn):
            fn = inlineCallbacks(fn)

        @functools.wraps(fn)
        @deferred(timeout=fn.timeout if hasattr(fn, 'timeout') else 1.0)
        @inlineCallbacks
        def ret():
            # dbg("\n============================================\n")

            import spinoff.actor._actor
            spinoff.actor._actor.TESTING = True

            Actor.reset_flags(debug=True)

            # TODO: once the above TODO (fresh Node for each test fn) is complete, consider making Events non-global by
            # having each Node have its own Events instance.
            Events.reset()

            # def finalmente(_):
            #     if _idle_calls:
            #         # dbg("TESTWRAP: processing all remaining scheduled calls...")
            #         _process_idle_calls()
            #         # dbg("TESTWRAP: ...scheduled calls done.")

            #     if '__pypy__' not in sys.builtin_module_names:
            #         gc.collect()
            #         for trash in gc.garbage[:]:
            #             if isinstance(trash, DebugInfo):
            #                 # dbg("DEBUGINFO: __del__")
            #                 if trash.failResult is not None:
            #                     exc = Unclean(repr(trash.failResult.value) + '\n' + str(trash._getDebugTracebacks()))
            #                     trash.__dict__.clear()
            #                     raise exc
            #                 gc.garbage.remove(trash)

            #         assert not gc.garbage, "Memory leak detected"

            #     return _

            # coll = ErrorCollector()
            # coll.__enter__()
            # return (
            #     fn()
            #     .addBoth(lambda _: (Node.stop_all(), _)[-1])
            #     .addBoth(lambda _: (coll.__exit__(None, None, None), _)[-1])
            #     .addBoth(finalmente)
            # )

            try:
                with ErrorCollector():
                    yield fn()
            finally:
                    # dbg("TESTWRAP: ------------------------- cleaning up after %s" % (fn.__name__,))

                    yield Node.stop_all()

                    if _idle_calls:
                        # dbg("TESTWRAP: processing all remaining scheduled calls...")
                        _process_idle_calls()
                        # dbg("TESTWRAP: ...scheduled calls done.")

                    if '__pypy__' not in sys.builtin_module_names:
                        gc.collect()
                        for trash in gc.garbage[:]:
                            if isinstance(trash, DebugInfo):
                                # dbg("DEBUGINFO: __del__")
                                if trash.failResult is not None:
                                    exc = Unclean(repr(trash.failResult.value) + '\n' + str(trash._getDebugTracebacks()))
                                    trash.__dict__.clear()
                                    raise exc
                                gc.garbage.remove(trash)

                        assert not gc.garbage, "Memory leak detected"

                        # if gc.garbage:
                        #     dbg("GARGABE: detected after %s:" % (fn.__name__,), len(gc.garbage))
                        #     import objgraph as ob
                        #     import os

                        #     def dump_chain(g_):
                        #         def calling_test(x):
                        #             if not isframework(x):
                        #                 return None
                        #         import spinoff
                        #         isframework = lambda x: type(x).__module__.startswith(spinoff.__name__)
                        #         ob.show_backrefs([g_], filename='backrefs.png', max_depth=100, highlight=isframework)

                        #     for gen in gc.garbage:
                        #         dump_chain(gen)
                        #         dbg("   TESTWRAP: mem-debuggin", gen)
                        #         import pdb; pdb.set_trace()
                        #         os.remove('backrefs.png')

                        # to avoid the above assertion from being included as part of any tracebacks from the test
                        # function--the last line of a context managed block is included in tracebacks originating
                        # from context managers.

        return ret

    for name, value in globals.items():
        if name.startswith('test_') and callable(value):
            globals[name] = wrap(value)
