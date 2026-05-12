import socket

HOST = "127.0.0.1"


class Host:
    def __init__(self, host, port) -> None:
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
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self) -> socket.socket:
        self.s.connect((self.host, self.port))
        print(f"CLIENT: Connected to {self.host}:{self.port}")
        return self.s

    def close(self) -> None:
        self.s.close()
        print("CLIENT: Closed connection")


def get_data(conn: socket.socket) -> str:
    return conn.recv(1024).decode()


def send_data(conn: socket.socket, data: str) -> None:
    conn.sendall(data.encode())

# Host code
if __name__ == "__main__":
    port = input("Port: ")
    host = Host(HOST, int(port))
    host_conn = host.run()
    while True:
        data = get_data(host_conn)
        if data:
            print(f"HOST RECEIVED: {data}")
