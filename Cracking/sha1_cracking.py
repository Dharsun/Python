import hashlib


def crack_sha1(wanted_hash, password_file):
    attempts = 1

    with open(password_file, "r", encoding="latin-1") as password_list:
        for password in password_list:
            password = password.strip("\n").encode("latin-1")
            password_hash = hashlib.sha1(password).hexdigest()
            #print("[{}] {} == {}".format(attempts, password.decode("latin-1"), password_hash))
            if password_hash == wanted_hash:
                print("Password hash found after {} attempts! '{}' hashes to '{}'".format(attempts, password.decode("latin-1"), password_hash))
                return password.decode("latin-1")
            attempts += 1

    print("Password hash not found")
    return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Invalid arguments")
        print(">> {} <sha1sum>".format(sys.argv[0]))
        sys.exit(1)

    wanted_hash = sys.argv[1]
    password_file = sys.argv[2]

    result = crack_sha1(wanted_hash, password_file)
    if result:
        print("Password: {}".format(result))
