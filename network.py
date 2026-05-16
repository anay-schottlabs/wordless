import socket
import struct
from typing import Optional

# default bind address for hosting on this machine
# this is also known as localhost
# in the app, typing "localhost" when connecting to a host will use this address
HOST = "127.0.0.1"

# cap on the amount of data that can be sent/received
_MAX_MESSAGE_BYTES = 16 * 1024 * 1024

# for assignment purposes for the programming class:
# note that in previous commits, I wrote the fundamental network logic in this file
# for the last week of the project, I've decided to try two way communication
# thus, I'm using AI to help me rewrite the code
# this is to make it more robust and efficient
# I haven't written much network code before, and therefore am using AI to try it out
# my original source code can be found in older versions of the project

def _recv_exact(conn: socket.socket, nbytes: int) -> Optional[bytes]:
    """pull nbytes off the socket or None if peer died."""
    parts = []
    left = nbytes
    while left > 0:
        chunk = conn.recv(left)
        if not chunk:
            return None
        parts.append(chunk)
        left -= len(chunk)
    return b"".join(parts)


def send_data(conn: socket.socket, data: str) -> None:
    """send one UTF-8 message (works both directions on same conn)."""
    raw = data.encode("utf-8")
    conn.sendall(struct.pack("!I", len(raw)) + raw)


def get_data(conn: socket.socket) -> str:
    """block until one full message arrives; empty string means conn closed or bad frame."""
    hdr = _recv_exact(conn, 4)
    if hdr is None:
        return ""
    (length,) = struct.unpack("!I", hdr)
    if length > _MAX_MESSAGE_BYTES:
        return ""
    if length == 0:
        return ""
    body = _recv_exact(conn, length)
    if body is None:
        return ""
    try:
        return body.decode("utf-8")
    except UnicodeDecodeError:
        return ""


class Host:
    """listens once and hands back the accepted socket for chat with client."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self) -> socket.socket:
        self.s.bind((self.host, self.port))
        self.s.listen()
        print(f"HOST: Listening on {self.host}:{self.port}")
        conn, _ = self.s.accept()
        return conn

    def close(self) -> None:
        self.s.close()
        print("HOST: Closed connection")


class Client:
    """connects outward; same send_data/get_data as host side."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self) -> socket.socket:
        self.s.connect((self.host, self.port))
        print(f"CLIENT: Connected to {self.host}:{self.port}")
        return self.s

    def close(self) -> None:
        try:
            self.s.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.s.close()
        print("CLIENT: Closed connection")


if __name__ == "__main__":
    port = input("Port: ")
    host = Host(HOST, int(port))
    host_conn = host.run()
    while True:
        data = get_data(host_conn)
        if data:
            print(f"HOST RECEIVED: {data}")
