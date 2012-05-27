import inspect
import os
from contextlib import contextmanager

from attest import Tests, assert_hook, raises

import frames


@contextmanager
def non_native_frames():
    previous_native = frames.NATIVE
    try:
        frames.NATIVE = False
        yield
    finally:
        frames.NATIVE = previous_native


suite = Tests()


@suite.test
def is_new_style_class():
    assert issubclass(frames.Frame, object)

@suite.test
def is_a_frame():
    assert inspect.isframe(frames.current_frame())

@suite.test
def non_native_is_a_frame():
    with non_native_frames():
        is_a_frame()

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

# Some non-native alternatives for the current tests.

@suite.test
def non_native_have_read_only_shortcuts():
    with non_native_frames():
        have_read_only_shortcuts()

@suite.test
def non_native_have_read_only_shortcuts():
    with non_native_frames():
        have_read_only_shortcuts()

@suite.test
def non_native_current_frame_is_really_the_current_frame():
    with non_native_frames():
        current_frame_is_really_the_current_frame()

@suite.test
def non_native_behave_like_native_frames():
    # Not the best scenario to test it since not all implementations actually
    # support the `level` argument. But the ones that do, raise `ValueError`.

    with raises(ValueError):
        frames._getframe(999)

    with raises(ValueError):
        import sys

        sys._getframe(999)


if __name__ == "__main__":
    suite.run()
