import sys


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
