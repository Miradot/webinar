import argparse
from ansible_vault import Vault


def create_file(args):

    with open("terraform/terraform.tfvars", "w") as file:
        file.write("ACI_URL = " + '\"{}\"'.format(args.aci_url) + "\n")
        file.write("ACI_USER = " + '\"{}\"'.format(args.aci_username) + "\n")
        file.write("VC_IP = " + '\"{}\"'.format(args.vcenter_ip) + "\n")
        file.write("VC_USER = " + '\"{}\"'.format(args.vcenter_username) + "\n")
        file.write("VC_DATACENTER = " + '\"{}\"'.format(args.vcenter_dc) + "\n")
        file.write("VC_DATASTORE = " + '\"{}\"'.format(args.vcenter_ds) + "\n")
        file.write("VC_COMPUTE_CLUSTER = " + '\"{}\"'.format(args.vcenter_cc) + "\n")

    with open("ansible_bak/hosts", "w") as file:
        file.write("[web]\n")
        file.write(args.web + "\n\n")
        file.write("[db]\n")
        file.write(args.db + "\n\n")
#        file.write("[dns]\n")
#        file.write(args.dns + "\n")

    with open("ansible_bak/group_vars/all", "w") as file:
        file.write("ansible_become_pass: '{{ vault_ansible_become_pass }}'\n")
        file.write("ansible_user: " + args.username + "\n")

    data = dict({"vault_ansible_become_pass": args.sudo_password})
    vault = Vault(args.ansible_vault_password)
    vault.dump(data, open("ansible_bak/group_vars/vault", "wb"))


def main():
    # show arguments for the user
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    required.add_argument("-a", dest="aci_url", help="ACI URL ; http(s)://192.168.1.1/", required=True)
    required.add_argument("-au", dest="aci_username", help="ACI Username", required=True)
    required.add_argument("-v", dest="vcenter_ip", help="vCenter IP ; 192.168.1.1", required=True)
    required.add_argument("-vu", dest="vcenter_username", help="vCenter Username", required=True)
    required.add_argument("-vdc", dest="vcenter_dc", help="vCenter Datacenter ; dc1", required=True)
    required.add_argument("-vds", dest="vcenter_ds", help="vCenter Datastore ; esxi2-DS-SSD", required=True)
    required.add_argument("-vcc", dest="vcenter_cc", help="vCenter Compute Cluster ; cluster1", required=True)
    required.add_argument("-u", dest="username", help="Server Username", required=True)
    required.add_argument("-ps", dest="sudo_password", help="Server Sudo Password", required=True)
    required.add_argument("-pv", dest="ansible_vault_password", help="Ansible Vault Password", required=True)

    optional.add_argument("-ws", dest="web", help="web hostname or ip default: 10.140.140.100", default="10.140.140.100")
    optional.add_argument("-ds", dest="db", help="db hostname or ip default: 10.141.141.100", default="10.141.141.100")
    #optional.add_argument("-dns", dest="dns", help="dns hostname or ip default: 10.145.145.102", default="10.145.145.102")

    #equired.add_argument("-o", dest="o_url", help="openshift url", required=True)
    #required.add_argument("-ot", dest="o_token", help="openshift token", required=True)

    args = parser.parse_args()

    create_file(args)


if __name__ == '__main__':
    main()
