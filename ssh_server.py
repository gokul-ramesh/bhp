import os
import paramiko
import socket
import sys
import threading


CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind: str, chanid: int):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username: str, password: str):
        if username == '$USER' and password == '$PASS':
            return paramiko.AUTH_SUCCESSFUL


if __name__ == "__main__":
    server = "127.0.0.1"
    port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server, port)
        sock.listen(100)
        print("Listening for connection...")
        client, address = sock.accept()
    except Exception as e:
        print(f"Listen Failed as {e}")
        sys.exit(0)
    else:
        print(f"Connected to {address[0]}:{address[1]}")

    session = paramiko.Transport(client)
    session.add_server_key(HOSTKEY)
    server = Server()
    session.start_server(server=server)

    chan = session.accept(20)
    if not chan:
        print("No Channel")
        sys.exit(1)

    print("Authenticated successfully!")
    print(chan.recv(1024))
    chan.send("Connected")
    try:
        while True:
            command = input("Enter command: ")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit')
                print('Exiting')
                session.close()
                break
    except KeyboardInterrupt:
        session.close()
