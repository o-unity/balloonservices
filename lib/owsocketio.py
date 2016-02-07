from socketIO_client import SocketIO, LoggingNamespace, LoggingMixin
import time


def _yield_elapsed_time(seconds=None):
    start_time = time.time()
    if seconds is None:
        while True:
            yield _get_elapsed_time(start_time)
    while _get_elapsed_time(start_time) < seconds:
        yield _get_elapsed_time(start_time)


def _get_elapsed_time(start_time):
    return time.time() - start_time


class OWSocketIO(SocketIO):

    def _yield_warning_screen(self, seconds=None):
        last_warning = None
        for elapsed_time in _yield_elapsed_time(seconds):
            try:
                yield elapsed_time
            except Exception as warning:
                warning = str(warning)
                if last_warning != warning:
                    last_warning = warning
                    self._warn(warning)
                time.sleep(10)

    def _yield_elapsed_time(seconds=None):
        start_time = time.time()
        if seconds is None:
            while True:
                yield _get_elapsed_time(start_time)
        while _get_elapsed_time(start_time) < seconds:
            yield _get_elapsed_time(start_time)
