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

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))
client.send(f"{data.encode}")

response = client.recv(4096)
print(response.decode())
client.close()