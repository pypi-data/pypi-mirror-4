import copy
import functools

from stompest.protocol import StompSpec

_RESERVED_HEADERS = [StompSpec.MESSAGE_ID_HEADER, StompSpec.DESTINATION_HEADER, 'timestamp', 'expires', 'priority']

def filterReservedHeaders(headers):
    return dict((header, value) for (header, value) in headers.iteritems() if header not in _RESERVED_HEADERS)

def checkattr(attribute):
    def _checkattr(f):
        @functools.wraps(f)
        def __checkattr(self, *args, **kwargs):
            getattr(self, attribute)
            return f(self, *args, **kwargs)
        return __checkattr
    return _checkattr

def cloneFrame(frame, persistent=None):
    frame = copy.deepcopy(frame)
    headers = filterReservedHeaders(frame.headers)
    if persistent is not None:
        headers['persistent'] = str(bool(persistent)).lower()
    frame.headers = headers
    return frame
