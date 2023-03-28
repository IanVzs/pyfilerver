"""
测试是否可以运行
"""
import signal
import platform
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pyfilerver
from pyfilerver import run


def set_timeout(timeout):
    def wrap(func):
        def time_out_handle(signum, frame):
            raise RuntimeError

        def to_do(*args, **kwargs):
            if platform.system() == "Windows":
                # Windows not signal.SIGALRM so pass
                return None
            try:
                signal.signal(signal.SIGALRM, time_out_handle)  # 设置信号和回调函数
                signal.alarm(timeout)  # 设置 timeout
                r = func(*args, **kwargs)
                signal.alarm(0)  # 正常处理则关闭
                return r
            except RuntimeError:
                pass

        return to_do

    return wrap


@set_timeout(1)
def test(
    HandlerClass=BaseHTTPRequestHandler,
    ServerClass=ThreadingHTTPServer,
    protocol="HTTP/1.0",
    port=8000,
    bind=None,
):
    """test the HTTP request handler class.

    This runs an HTTP server on port 8000 (or the port argument).

    """
    run()
