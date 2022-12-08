import socket
import threading
import argparse


class tcpServer:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port

	def main(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind((self.ip, self.port))
		server.listen(5)
		print(f'[*] Listening on {self.ip}:{self.port}')

		while True:
			client, address = server.accept()
			print(f'[*] Accepted connection from {address[0]}:{address[1]}')
			client_handler = threading.Thread(target=handle_client, args=(client,))
			client_handler.start()


def handle_client(client_socket):
	with client_socket as sock:
		request = sock.recv(1024)
		print(f'[*] Received: {request.decode("utf-8")}')
		sock.send(b"ACK")


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("ip", "-i", required=True, help="IP where the server is to be hosted")
	parser.add_argument("port", "-p", required=True, help="Port for hosting the TCP Server")
	args = parser.parse_args()
	server = tcpServer(args.ip, args.port)
	server.main()
