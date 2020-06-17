import argparse


def create_file(args):

    with open("hosts", "w") as file:
        file.write("[webservers]\n")
        for line in args.servers:
            file.write(line + "\n")

        file.write("\n[webservers:vars]\n")
        file.write("ansible_python_interpreter=/usr/bin/python3\n")

    with open("group_vars/webservers", "w") as file:
        file.write("ansible_become_pass: " + args.sudo_password + "\n")
        file.write("ansible_user: " + args.username + "\n")
        file.write("ansible_password: " + args.password + "\n")


def main():
    # show arguments for the user
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group("required arguments")
    required.add_argument("-s", dest="servers",
                          help="Server Hostname/IP ; 192.168.1.1 superserver.lab.local ...",
                          required=True,
                          nargs='+')
    required.add_argument("-u", dest="username", help="Server Username", required=True)
    required.add_argument("-p", dest="password", help="Server Password", required=True)
    required.add_argument("-ps", dest="sudo_password", help="Server Sudo Password", required=True)

    args = parser.parse_args()

    create_file(args)


if __name__ == '__main__':
    main()
