"""
http.server plus

add uploadfile
"""
import datetime
import html
import io
import os
import re
import shutil
import socket
import sys
import urllib
from http import HTTPStatus
from http.server import (
    BaseHTTPRequestHandler,
    CGIHTTPRequestHandler,
    SimpleHTTPRequestHandler,
    ThreadingHTTPServer,
)


def _get_best_family(*address):
    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, type, proto, canonname, sockaddr = next(iter(infos))
    return family, sockaddr


def run(
    HandlerClass=BaseHTTPRequestHandler,
    ServerClass=ThreadingHTTPServer,
    protocol="HTTP/1.0",
    port=8000,
    bind=None,
):
    """run the HTTP request handler class.

    This runs an HTTP server on port 8000 (or the port argument).

    """
    ServerClass.address_family, addr = _get_best_family(bind, port)
    HandlerClass.protocol_version = protocol
    with ServerClass(addr, HandlerClass) as httpd:
        host, port = httpd.socket.getsockname()[:2]
        url_host = f"[{host}]" if ":" in host else host
        print(f"Serving HTTP on {host} port {port} " f"(http://{url_host}:{port}/) ...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)


class SimpleHTTPRequestHandlerPlus(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k) -> None:
        super().__init__(*a, **k)

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(self.path, errors="surrogatepass")
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = "Directory listing for %s" % displaypath
        r.append(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
            '"http://www.w3.org/TR/html4/strict.dtd">'
        )
        r.append("<html>\n<head>")
        r.append(
            '<meta http-equiv="Content-Type" ' 'content="text/html; charset=%s">' % enc
        )
        r.append("<title>%s</title>\n</head>" % title)
        r.append("<body>\n<h1>%s</h1>" % title)
        r.append("<hr>\n<ul>")

        r.append("<hr>\n")
        r.append('<form ENCTYPE="multipart/form-data" method="post">')
        r.append('<input name="file" type="file"/>')
        r.append('<input type="submit" value="upload"/></form>\n')
        r.append("<hr>\n<ul>\n")

        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            r.append(
                '<li style="text-align:right"><a href="{}" style="float:left">{}</a><div style="float:right; padding-right:50%">{}&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;{}</div></li>'.format(
                    urllib.parse.quote(linkname, errors="surrogatepass"),
                    html.escape(displayname, quote=False),
                    datetime.datetime.fromtimestamp(os.path.getmtime(fullname)),
                    sys.getsizeof(fullname),
                )
            )
        r.append("</ul>\n<hr>\n</body>\n</html>\n")
        encoded = "\n".join(r).encode(enc, "surrogateescape")
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

    def do_POST(self):
        """Serve a POST request."""
        sign, info = self.deal_post_data()
        print(sign, info, "by: ", self.client_address)
        r = []
        r.append('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        r.append("<html>\n<title>Upload Result Page</title>\n")
        r.append("<body>\n<h2>Upload Result Page</h2>\n")
        r.append("<hr>\n")
        if sign:
            r.append("<strong>Success:</strong>")
        else:
            r.append("<strong>Failed:</strong>")
        r.append(info)
        r.append('<br><a href="%s">back</a>' % self.headers["referer"].encode("utf-8"))
        r.append("here</a>.</small></body>\n</html>\n")
        enc = sys.getfilesystemencoding()
        encoded = "\n".join(r).encode(enc, "surrogateescape")
        f = io.BytesIO()
        f.write(encoded)
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            shutil.copyfileobj(f, self.wfile)
            f.close()

    def deal_post_data(self):
        boundary = self.headers["Content-Type"].split("=")[1].encode("utf-8")
        remain_bytes = int(self.headers["content-length"])
        line = self.rfile.readline()
        remain_bytes -= len(line)
        if boundary not in line:
            return False, "Content NOT begin with boundary"
        line = self.rfile.readline()
        remain_bytes -= len(line)
        fn = re.findall(
            r'Content-Disposition.*name="file"; filename="(.*)"', line.decode("utf-8")
        )
        if not fn or (len(fn) == 1 and not fn[0]):
            return False, "Can't find out file name..."
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        while os.path.exists(fn):
            filename = os.path.split(fn)[-1]
            if "." in filename:
                h = filename.split(".")
                t = h[-1]
                h = "".join(h[:-1]) + "_"
                fn = ".".join([h, t])
            else:
                fn += "_"
        line = self.rfile.readline()
        remain_bytes -= len(line)
        line = self.rfile.readline()
        remain_bytes -= len(line)
        try:
            out = open(fn, "wb")
        except IOError:
            return False, "Can't create file to write, do you have permission to write?"

        pre_line = self.rfile.readline()
        remain_bytes -= len(pre_line)
        while remain_bytes > 0:
            line = self.rfile.readline()
            remain_bytes -= len(line)
            if boundary in line:
                pre_line = pre_line[0:-1]
                if pre_line.endswith(b"\r"):
                    pre_line = pre_line[0:-1]
                out.write(pre_line)
                out.close()
                return True, "File '%s' upload success!" % fn
            else:
                out.write(pre_line)
                pre_line = line
        return False, "Unexpect Ends of data."


def main():
    import argparse
    import contextlib

    parser = argparse.ArgumentParser()
    parser.add_argument("--cgi", action="store_true", help="run as CGI server")
    parser.add_argument(
        "--bind",
        "-b",
        metavar="ADDRESS",
        help="specify alternate bind address " "(default: all interfaces)",
    )
    parser.add_argument(
        "--directory",
        "-d",
        default=os.getcwd(),
        help="specify alternate directory " "(default: current directory)",
    )
    parser.add_argument(
        "port",
        action="store",
        default=8000,
        type=int,
        nargs="?",
        help="specify alternate port (default: 8000)",
    )
    args = parser.parse_args()
    if args.cgi:
        handler_class = CGIHTTPRequestHandler
    else:
        handler_class = SimpleHTTPRequestHandlerPlus

    # ensure dual-stack is not disabled; ref #38907
    class DualStackServer(ThreadingHTTPServer):
        def server_bind(self):
            # suppress exception when protocol is IPv4
            with contextlib.suppress(Exception):
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            return super().server_bind()

        def finish_request(self, request, client_address):
            self.RequestHandlerClass(
                request, client_address, self, directory=args.directory
            )

    run(
        HandlerClass=handler_class,
        ServerClass=DualStackServer,
        port=args.port,
        bind=args.bind,
    )


if __name__ == "__main__":
    main()
