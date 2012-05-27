'''
  __                                             
 / _|_ __ __ _ _ __ ___   ___  ___   _ __  _   _ 
| |_| '__/ _` | '_ ` _ \ / _ \/ __| | '_ \| | | |
|  _| | | (_| | | | | | |  __/\__ \_| |_) | |_| |
|_| |_|  \__,_|_| |_| |_|\___||___(_) .__/ \__, |
                                  |_|       |__/ 
'''

__all__ = [
    'FrameNotFound', 'FrameType', 'Frame', 'current_frame', 'locate_frame'
]


import sys


NATIVE = hasattr(sys, '_getframe')


def _getframe(level=0):
    '''
    A reimplementation of `sys._getframe`.

    `sys._getframe` is a private function, and isn't guaranteed to exist in all
    versions and implementations of Python.

    This function is about 2 times slower than the native implementation. It
    relies on the asumption that the traceback objects have `tb_frame`
    attributues holding proper frame objects.

    :param level:
        The number of levels deep in the stack to return the frame from.
        Defaults to `0`.
    :returns:
        A frame object `levels` deep from the top of the stack.
    '''

    if level < 0:
        level = 0

    try:
        raise
    except:
        # `sys.exc_info` returns `(type, value, traceback)`.
        _, _, traceback = sys.exc_info()
        frame = traceback.tb_frame

        # Account for our exception, this will stop at `-1`.
        while ~level:
            frame = frame.f_back

            if frame is None:
                break

            level -= 1
    finally:
        sys.exc_clear()

    # Act as close to `sys._getframe` as possible.
    if frame is None:
        raise ValueError('call stack is not deep enough')

    return frame


# Make classes new-style by default.
__metaclass__ = type


class Frame:
    '''
    Wrapper object for the internal frames.
    '''

    class NotFound(LookupError):
        '''
        Raised when no frame is found.
        '''

    Type = sys._getframe().__class__

    @staticmethod
    def current_frame(raw=False):
        '''
        Gives the current execution frame.

        :returns:
            The current execution frame that is actually executing this.
        '''

        # `import sys` is important here, because the `sys` module is special
        # and we will end up with the class frame instead of the `current` one.

        if NATIVE:
            import sys

            frame = sys._getframe()
        else:
            frame = _getframe()

        frame = frame.f_back

        if not raw:
            frame = Frame(frame)

        return frame

    @staticmethod
    def locate(callback, root_frame=None, include_root=False, raw=False):
        '''
        Locates a frame by criteria.

        :param callback:
            One argument function to check the frame against. The frame we are
            curretly on, is given as that argument.
        :param root_frame:
            The root frame to start the search from. Can be a callback taking
            no arguments.
        :param include_root:
            `True` if the search should start from the `root_frame` or the one
            beneath it. Defaults to `False`.
        :param raw:
            whether to use raw frames or wrap them in our own object. Defaults to
            `False`.
        :raises RuntimeError:
            When no matching frame is found.
        :returns:
            The first frame which responds to the `callback`.
        '''

        def get_from(maybe_callable):
            if callable(maybe_callable):
                return maybe_callable()

            return maybe_callable

        # Creates new frames, whether raw or not.
        new = lambda frame: frame if raw else Frame(frame)

        current_frame = get_from(root_frame or Frame.current_frame(raw=True))
        current_frame = new(current_frame)

        if not include_root:
            current_frame = new(current_frame.f_back)

        # The search will stop, because at some point the frame will be falsy.
        while current_frame:
            found = callback(current_frame)

            if found:
                return current_frame

            current_frame = new(current_frame.f_back)

        raise Frame.NotFound('No matching frame found')

    def __init__(self, frame):
        '''
        Wraps the raw frame object.

        :param frame:
            The frame object to wrap.
        '''

        self.frame = frame

        if not frame:
            return

        # Read-only attributes go below.

        #: Shortcut for `f_back`
        self.back = frame.f_back

        #: Shortcut for `f_builtins`
        self.builtins = frame.f_builtins

        #: Shortcut for `f_code`
        self.code = frame.f_code

        #: Shortcut for `f_globals`
        self.globals = frame.f_globals

        #: Shortcut for `f_locals`.
        self.locals = frame.f_locals

        #: Shortcut for `f_restricted`.
        self.restricted = frame.f_restricted

    # Special attributes are defined as properties.

    @property
    def exc_traceback(self):
        '''
        Shortcut for `f_exc_traceback`.

        :returns:
            The frame exception traceback, if any.
        '''

        return self.frame.f_exc_traceback

    @property
    def exc_type(self):
        '''
        Shortcut for `f_exc_type`.

        :returns:
            The frame exception class, if any.
        '''

        return self.frame.f_exc_type

    @property
    def exc_value(self):
        '''
        Shortcut for `f_exc_value`.

        :returns:
            The frame exception instance, if any.
        '''

        return self.frame.f_exc_value

    @property
    def last_instruction(self):
        '''
        Shortcut for `f_lasti`

        :returns:
            The last frame instruction.
        '''

        return self.frame.f_lasti

    @property
    def lineno(self):
        '''
        Shortcut for `f_lineno`.

        :returns:
            The line of the code at the current frame.
        '''

        return self.frame.f_lineno - 1

    @property
    def trace(self):
        '''
        Shortcut for `f_trace`.

        :returns:
            The trace function, if any.
        '''

        return self.frame.f_trace

    @property
    def __class__(self):
        # Make us look like a regular frame in front of `isinstance`.

        return Frame.Type

    def __getattr__(self, name):
        # Proxy some methods back to the raw frame object.

        if not hasattr(self.frame, name):
            raise AttributeError(name)

        return getattr(self.frame, name)

    def __bool__(self):
        return True if self.frame else False

    __nonzero__ = __bool__


# More standard, non classy Python interface.
FrameNotFound = Frame.NotFound
FrameType = Frame.Type
locate_frame = Frame.locate
current_frame = Frame.current_frame
