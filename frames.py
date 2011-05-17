'''
High level execution frame utilities.
'''

__all__ = [
    'FrameError', 'FrameNotFound', 'FrameType', 'Frame',
    'current_frame', 'locate_frame'
]


import sys


if not hasattr(sys, '_getframe'):
    # _getframe may not be available on all of the Python distributions.
    raise ImportError(
        'sys._getframe is not supported on the current Python implementation.')


class Frame(object):
    '''
    Namespace to keep the frame related stuff.
    '''

    # Can become a more proper object.

    class Error(Exception):
        '''
        The base for everything frame related going wrong in the module.
        '''
    
    class NotFound(Error):
        '''
        Raised when no frame is found.
        '''

    Type = sys._getframe().__class__

    @classmethod
    def current_frame(cls):
        '''
        Gives the current execution frame.

        :returns: The current execution frame that is actually executing this.
        '''
    
        # ``import sys`` is important here, because the `sys` module is special 
        # and we will end up with the class frame instead of the `current` one.

        import sys

        return sys._getframe().f_back

    @classmethod
    def locate(cls, callback, root_frame=current_frame,
        include_root=False):

        '''
        Locates a frame by criteria.

        :param callback: One argumented function to check the frame against.
        :param root_frame: The root frame to start the search from. Can be a
            callback taking no arguments.
        :param include_root: `True` if the search should start from the
            `root_frame` or the one beneath it. Defaults to `False`.
        :raises RuntimeError: When no matching frame is found.
        :returns: The first frame which responds to the `callback`.
        '''

        def get_frame_from(frame_or_callable):
            if hasattr(frame_or_callable, '__call__'):
                return frame_or_callable()
            
            return frame_or_callable

        if include_root:
            curr_frame = get_frame_from(root_frame)
        else:
            curr_frame = get_frame_from(root_frame).f_back

        # The search will stop, because at some point the frame will be `None`.
        while curr_frame:
            is_found = callback(curr_frame)

            if is_found:
                return is_found

            curr_frame = curr_frame.f_back

        raise Frame.NotFound('No matching frame found')

# More standard, non classy Python interface.
FrameError = Frame.Error
FrameNotFound = Frame.NotFound
FrameType = Frame.Type
locate_frame = Frame.locate
current_frame = Frame.current_frame

