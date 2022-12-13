import paramiko

def ssh_cmd(ip, port, user, password, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, user, password)

    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print("Output:")
        for line in output:
            print(line.strip())


if __name__ == "__main__":
    import getpass
    user = input("Username: ")
    password= getpass.getpass()

    ip = input("IP: ")
    port = input("Port: ")
    cmd = input("Command to be executed: ")
    ssh_cmd(ip, port, user, password, cmd)
