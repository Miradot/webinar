import yaml
import argparse
from ansible_vault import Vault


def create_file(args):

    svc = open("netbox_tools/webhook_proxy_svc.py", "r")
    all_lines = svc.readlines()

    svc = open("netbox_tools/webhook_proxy_svc.py", "w")
    for index, content in enumerate(all_lines):
        if "'token'" in content:
            all_lines[index] = "    'token': (None, '{}'),\n".format(args.gitlab_token)

        if "gitlab_url =" in content:
            all_lines[index] = "gitlab_url = '{}'\n".format(args.gitlab_url)

        if "host_vars = " in content:
            all_lines[index] = "host_vars = '{}repository/files/ansible%2Fhost_vars%2F{}?ref=master'\n".format(
                args.gitlab_url.split("trigger")[0], args.nxos_devices[0])

    svc.writelines(all_lines)
    svc.close()

    inv = open("netbox_tools/inventory.py", "r")
    all_lines = inv.readlines()

    inv = open("netbox_tools/inventory.py", "w")
    for index, content in enumerate(all_lines):
        if "URL =" in content:
            all_lines[index] = "URL = '{}'\n".format(args.netbox_url)

        if "TOKEN =" in content:
            all_lines[index] = "TOKEN = '{}'\n".format(args.netbox_token)

    inv.writelines(all_lines)
    inv.close()

    config = dict()
    config["ansible_connection"] = "network_cli"
    config["ansible_network_os"] = "nxos"
    config["ansible_user"] = args.nxos_username
    config["ansible_password"] = "{{ vault_ansible_password }}"
    config["nxapi_port"] = args.nxos_port
    config["netbox_url"] = args.netbox_url

    with open("ansible/group_vars/all", "w") as file:
        yaml.dump(config, file)

    with open("ansible/hosts", "w") as file:
        for device in args.nxos_devices:
            file.write("\n[{}]\n".format(device))
            file.write("{}\n".format(device))

    data = dict({"vault_ansible_password": args.nxos_password, "netbox_token": args.netbox_token})
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

    required.add_argument("-nu", dest="netbox_url", help="Netbox URL ; http(s)://netbox.lab.local", required=True)
    required.add_argument("-nt", dest="netbox_token", help="Netbox Token ; 12345abcdef", required=True)
    required.add_argument("-gu", dest="gitlab_url",
                          help="Gitlab Pipeline Trigger Url ; http("
                               "s)://gitlab.lab.local/api/v4/projects/91/trigger/pipeline",
                          required=True)
    required.add_argument("-gt", dest="gitlab_token", help="Gitlab Pipeline Token ; 12345abcdef", required=True)

    args = parser.parse_args()

    create_file(args)


if __name__ == '__main__':
    main()
