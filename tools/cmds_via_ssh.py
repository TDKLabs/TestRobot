import sys
import paramiko 

host = sys.argv[1]
user = sys.argv[2]
pw = sys.argv[3]

# command to run on remote host
command = sys.argv[4]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=pw)

stdin, stdout, stderr = ssh.exec_command(command)
stdin.close()

print stdout.read()
ssh.close()