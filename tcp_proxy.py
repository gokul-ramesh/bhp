import argparse
import sys
import socket
import threading
import time


def receive_from(connection):   # Generic function to receive data from connection
    buffer = b""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception:
        pass
    return buffer


def hexdump(src, length=16, show=True):   # Generic function to print logs as hexadecimals and ASCII
    HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])
        printable = word.translate(HEX_FILTER)
        hexa = "".join([f"{ord(c):02X}" for c in word])
        hexwidth = length*3
        results.append(f"{i:04x} {hexa:<{hexwidth}} {printable}")
    if show:
        for line in results:
            print(line)
    else:
        return results


class Proxy:
    def __init__(self, local, remote, receive_first):   # Constructor
        self.local_host = local.split(":")[0]
        self.local_port = int(local.split(":")[1])
        self.remote_host = remote.split(":")[0]
        self.remote_port = int(remote.split(":")[1])
        self.receive_first = receive_first

    def proxy_handler(self, client_socket):   # Handles the connection between hosts
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((self.remote_host, self.remote_port))

        if self.receive_first:
            remote_buffer = receive_from(remote_socket)
            hexdump(remote_buffer)
            if remote_buffer:
                print(f"<== Sending {len(remote_buffer)} bytes to the localhost")
                client_socket.send(remote_buffer)
                print(f"<== Data sent to localhost")
        wait_cycle = 0   # Go through a few sleep cycles before closing the connection
        close_cycle = 10   # No of cycles before closing connection
        while True:
            local_buffer = receive_from(client_socket)
            if len(local_buffer):
                wait_cycle = 0
                line = f"==> Received {len(local_buffer)} bytes from localhost"
                print(line)
                hexdump(local_buffer)

                remote_socket.send(local_buffer)
                print("Data sent to remote host")

            remote_buffer = receive_from(remote_socket)
            if len(remote_buffer):
                wait_cycle = 0
                print(f"<== Received {len(remote_buffer)} bytes from remote")
                hexdump(remote_buffer)

                client_socket.send(remote_buffer)
                print("<== Data sent to localhost")

            if not len(local_buffer) or not len(remote_buffer):
                if close_cycle - wait_cycle == 3:
                    print(f"Connection about to be closed due to inactivity")
                if wait_cycle < close_cycle:
                    wait_cycle += 1
                    time.sleep(2)
                else:
                    client_socket.close()
                    remote_socket.close()
                    print("Connection closed")
                    break

    def server_loop(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind((self.local_host, self.local_port))
        except Exception as e:
            print(f"Failed to listen on port {self.local_port}, problem with binding due to {e}")
            sys.exit(0)
        print(f"Listening on {self.local_host}:{self.local_port}")
        server.listen(5)
        while True:
            client_socket, address = server.accept()
            print(f"Received connection from {address[0]}:{address[1]}")

            proxy_thread = threading.Thread(target=self.proxy_handler, args=(client_socket,))
            proxy_thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", "-l", required=True, help = "[localhost]:[localport]")
    parser.add_argument("--remote", "-r", required=True, help = "[remotehost]:[remoteport]")
    parser.add_argument("--receiveFirst", "-f", action="store_true", help = "[Receive first - boolean]")
    args = parser.parse_args()

    if args.local and args.remote:
        if args.receiveFirst:
            proxy = Proxy(args.local, args.remote, True)
        else:
            proxy = Proxy(args.local, args.remote, False)
        proxy.server_loop()
