import yaml
import argparse
from ansible_vault import Vault


def create_file(args):

    config = dict()
    config["ansible_connection"] = "network_cli"
    config["ansible_network_os"] = "nxos"
    config["ansible_user"] = args.nxos_username
    config["ansible_password"] = "{{ vault_ansible_password }}"
    config["nxapi_port"] = args.nxos_port

    with open("ansible/group_vars/all", "w") as file:
        yaml.dump(config, file)

    with open("ansible/hosts", "w") as file:
        for device in args.nxos_devices:
            file.write("\n[{}]\n".format(device))
            file.write("{}\n".format(device))

    data = dict({"vault_ansible_password": args.nxos_password})
    vault = Vault(args.ansible_vault_password)
    vault.dump(data, open("ansible/group_vars/vault", "wb"))


def main():
    # show arguments for the user
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group("required arguments")

    required.add_argument("-d", dest="nxos_devices",
                          help="NXOS Hostname or IP ; nxos1.lab.local 192.168.1.1 ...",
                          required=True,
                          nargs='+')
    required.add_argument("-np", dest="nxos_port", help="NXAPI Port ; 80", required=True)
    required.add_argument("-u", dest="nxos_username", help="NXOS Username", required=True)
    required.add_argument("-p", dest="nxos_password", help="NXOS Password", required=True)
    required.add_argument("-pv", dest="ansible_vault_password", help="Ansible Vault Password", required=True)

    args = parser.parse_args()

    create_file(args)


if __name__ == '__main__':
    main()
