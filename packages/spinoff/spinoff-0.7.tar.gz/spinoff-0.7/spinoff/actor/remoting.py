class NodeHub(object):
    def __init__(self, hub, guardian):
        self._hub = hub
        self._guardian = guardian

    def send_message(self, message, remote_ref):
        # remote_path, rcpt_nid = remote_ref.uri.path, remote_ref.uri.node
        # dbg(repr(message), "->", remote_path, "@", rcpt_nid)
        self._hub.send_message(remote_ref.uri.node, _Msg(remote_ref, message))

    def _on_receive(self, sender_nid, msg_bytes):
        local_path, message = IncomingMessageUnpickler(self, StringIO(msg_bytes)).load()
        cell = self._guardian.lookup_cell(Uri.parse(local_path))
        if not cell:
            if ('_watched', ANY) == message:
                watched_ref = Ref(cell=None, is_local=True, uri=Uri.parse(self.nid + local_path))
                _, watcher = message
                watcher << ('terminated', watched_ref)
            elif message in (('terminated', ANY), ('_watched', ANY), ('_unwatched', ANY)):
                pass
            else:
                self._remote_dead_letter(local_path, message, sender_nid)
        else:
            cell.receive(message)  # XXX: force_async=True perhaps?

    def _remote_dead_letter(self, path, msg, from_):
        ref = Ref(cell=None, uri=Uri.parse(self.nid + path), is_local=True)
        Events.log(RemoteDeadLetter(ref, msg, from_))


class _Msg(object):
    def __init__(self, ref, msg):
        self.ref, self.msg = ref, msg

    def serialize(self):
        return dumps((self.ref.uri.path, self.msg), protocol=2)

    def send_failed(self):
        Events.log(DeadLetter(self.ref, self.msg))
