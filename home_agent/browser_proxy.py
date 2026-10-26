"""HTTPS CONNECT proxy that connects to verified public IPs, preventing DNS rebinding."""

import select
import socket
import socketserver
import threading
import time
from collections import deque
from urllib.parse import urlsplit

from .browser_policy import public_url, public_addresses


class Tunnel(socketserver.StreamRequestHandler):
    def handle(self):
        remote = None
        try:
            self.connection.settimeout(12)
            line = self.rfile.readline(4097).decode("ascii")
            if len(line) > 4096:
                raise ValueError()
            method, target, version = line.strip().split()
            total = 0
            while True:
                header = self.rfile.readline(4097)
                total += len(header)
                if total > 16000:
                    raise ValueError()
                if header in (b"\r\n", b"\n", b""):
                    break
            if method != "CONNECT":
                raise ValueError()
            parsed = urlsplit(public_url("https://" + target + "/"))
            addresses = public_addresses(parsed.hostname)
            # The actual TCP connection uses this verified IP, never a second hostname lookup.
            for address in addresses:
                try:
                    remote = socket.create_connection((address, 443), timeout=10)
                    break
                except OSError:
                    continue
            if remote is None:
                raise OSError()
            self.connection.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            deadline, transferred = time.monotonic() + 45, 0
            while time.monotonic() < deadline and transferred < 8_000_000:
                ready, _, _ = select.select([self.connection, remote], [], [], 1)
                for source in ready:
                    content = source.recv(65536)
                    if not content:
                        return
                    transferred += len(content)
                    (remote if source is self.connection else self.connection).sendall(
                        content
                    )
        except Exception:
            self.server.denials.append("Public HTTPS connection blocked or unavailable")
            try:
                self.connection.sendall(
                    b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                )
            except OSError:
                pass
        finally:
            if remote:
                remote.close()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class PublicProxy:
    def __enter__(self):
        self.server = Server(("127.0.0.1", 0), Tunnel)
        self.server.denials = deque(maxlen=20)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
