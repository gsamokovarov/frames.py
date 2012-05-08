import inspect
import os

from frames import Frame, FrameError, FrameNotFound, locate_frame, current_frame

from attest import Tests, assert_hook, raises


frames = Tests()


@frames.test
def is_new_style_class():
    assert issubclass(Frame, object)

@frames.test
def is_a_frame():
    assert inspect.isframe(current_frame())

@frames.test
def have_shortcuts():
    frame = Frame.current_frame()

    assert frame.back == frame.f_back
    assert frame.code == frame.f_code
    assert frame.globals == frame.f_globals
    assert frame.lineno == frame.f_lineno - 1
    assert frame.locals == frame.f_locals

@frames.test
def current_frame_is_really_the_current_frame():
    apples = 'yep'

    assert 'apples' in current_frame().f_locals

@frames.test
def raises_lookup_error_when_frames_are_not_found():
    with raises(LookupError):
        locate_frame(lambda f: os.urandom(24) in f.locals)


if __name__ == "__main__":
    frames.run()
