
from py4web import action, request, abort, redirect, URL, response
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated


import os
from py4web import action, Field, DAL
from py4web.utils.grid import Grid, GridClassStyleBulma
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from py4web.utils.grid import Column

from pydal.tools.tags import Tags
from .utils import Authorized

import queue




class MessageAnnouncer:

    def __init__(self):
        self.listeners = []

    def listen(self):
        self.listeners.append(queue.Queue(maxsize=5))
        return self.listeners[-1]

    def announce(self, msg):
        # We go in reverse order because we might have to delete an element, which will shift the
        # indices backward
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]


announcer = MessageAnnouncer()


def format_sse(data: str, event=None) -> str:
    """Formats a string and an event name in order to follow the event stream convention.

    >>> format_sse(data=json.dumps({'abc': 123}), event='Jackson 5')
    'event: Jackson 5\\ndata: {"abc": 123}\\n\\n'

    """
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg



@action('ping')
def ping():
    print("sono in ping")
    msg = format_sse(data='pong')
    announcer.announce(msg=msg)
    return {}, 200


@action('listen', method=["POST", "GET"])
def listen():
    print("sono in listen")

    def stream():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    #return response(stream(), mimetype='text/event-stream')
    #response.header = "mimetype='text/event-stream'"
    return stream()



# exposed as /examples/html_grid
@action("proto/proto")
@action.uses(session, db, T ,"proto/proto.html")
def proto() :
    
    
    return dict(T=T)
