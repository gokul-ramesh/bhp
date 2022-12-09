import argparse
import socket
import shlex
import subprocess
import sys
import threading


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return 
    output = subprocess.check_output(shlex.split(cmd), stderr= subprocess.STDOUT)
    return output.decode()


class Netcat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
            
    def send(self):
        self.socket.connect((self.args.target,self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(1024)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 1024:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('Terminated.')
            self.socket.close()
            sys.exit()
    
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen()
        while True:
            client, _ = self.socket.accept()
            client_handler = threading.Thread(target=self.handle, args = (client,))
            client_handler.start()
    
    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'Shell $> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(128)
                    resp = execute(cmd_buffer.decode())
                    if resp:
                        client_socket.send(resp.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Server Killed')
                    self.socket.close()
                    sys.exit()
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
                
            with open(self.args.upload, 'wb') as file:
                file.write(file_buffer)
            
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
                    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Netcat Python' )
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='port')
    parser.add_argument('-t', '--target', help='target IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
        
    nc = Netcat(args, buffer.encode())
    nc.run()
