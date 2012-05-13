import inspect
import os

from attest import Tests, assert_hook, raises

import frames


suite = Tests()


@suite.test
def is_new_style_class():
    assert issubclass(frames.Frame, object)

@suite.test
def is_a_frame():
    assert inspect.isframe(frames.current_frame())

@suite.test
def have_read_only_shortcuts():
    frame = frames.current_frame()

    assert frame.back == frame.f_back
    assert frame.code == frame.f_code
    assert frame.globals == frame.f_globals
    assert frame.locals == frame.f_locals
    assert frame.restricted == frame.f_restricted

@suite.test
def have_special_shortcuts():
    frame = frames.current_frame()

    assert frame.lineno == frame.f_lineno - 1
    assert frame.last_instruction != frame.last_instruction
    assert frame.trace is None

    try:
        @apply
        def test_errors():
            try:
                raise
            finally:
                assert frame.exc_type is not None
                assert frame.exc_value is not None
                assert frame.exc_traceback is not None
    except:
        assert frame.exc_type is None
        assert frame.exc_value is None
        assert frame.exc_traceback is None

@suite.test
def current_frame_is_really_the_current_frame():
    apples = 'yep'

    assert 'apples' in frames.current_frame().f_locals

@suite.test
def raises_lookup_error_when_frames_are_not_found():
    with raises(LookupError):
        frames.locate_frame(lambda f: os.urandom(24) in f.locals)


if __name__ == "__main__":
    suite.run()
