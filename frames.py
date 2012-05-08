__all__ = [
    'FrameError', 'FrameNotFound', 'FrameType', 'Frame',
    'current_frame', 'locate_frame'
]


import sys


if not hasattr(sys, '_getframe'):
    # _getframe may not be available on all of the Python distributions.
    raise ImportError(
        'sys._getframe is not supported on the current Python implementation.')


# Make classes new-style by default.
__metaclass__ = type


class Frame:
    '''
    Wrapper object for the internal frames.
    '''

    class Error(Exception):
        '''
        The base for everything frame related going wrong in the module.
        '''

    class NotFound(Error, LookupError):
        '''
        Raised when no frame is found.
        '''

    Type = sys._getframe().__class__

    @staticmethod
    def current_frame(raw=False):
        '''
        Gives the current execution frame.

        :returns: The current execution frame that is actually executing this.
        '''
    
        # `import sys` is important here, because the `sys` module is special 
        # and we will end up with the class frame instead of the `current` one.

        import sys

        frame = sys._getframe().f_back

        if not raw:
            frame = Frame(frame)

        return frame

    @staticmethod
    def locate(callback, root_frame=None, include_root=False, raw=False):
        '''
        Locates a frame by criteria.

        :param callback:
            One argumented function to check the frame against. The frame we
            are curretly on, is given as that argument.
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

        # The search will stop, because at some point the frame will be `None`.
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

        #: Shortcut for `f_back`
        self.back = frame.f_back

        #: Shortcut for `f_code`
        self.code = frame.f_code

        #: Shortcut for `f_globals`
        self.globals = frame.f_globals

        #: Shortcut for `f_locals`.
        self.locals = frame.f_locals

    @property
    def lineno(self):
        '''
        Dynamic shortcut for `f_lineno`.

        :returns: The line of the code at the current frame.
        '''

        return self.frame.f_lineno - 1

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
FrameError = Frame.Error
FrameNotFound = Frame.NotFound
FrameType = Frame.Type
locate_frame = Frame.locate
current_frame = Frame.current_frame
