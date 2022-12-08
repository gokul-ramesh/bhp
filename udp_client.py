import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("ip", required=True)
parser.add_argument("port", required=True)
parser.add_argument("data", required=True)
args = parser.parse_args()

target_host = args.ip
target_port = args.port
data = args.data

client = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
client.sendto(f"{data.encode}", (target_host, target_port))
received, addr = client.recvfrom(4096)

print(received.decode())
client.close()
