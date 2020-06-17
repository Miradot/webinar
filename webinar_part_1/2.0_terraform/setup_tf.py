import argparse


def create_file(args):

    with open("terraform.tfvars", "w") as file:
        file.write("ACI_URL = " + '\"{}\"'.format(args.aci_url) + "\n")
        file.write("ACI_USER = " + '\"{}\"'.format(args.aci_username) + "\n")
        file.write("ACI_PASS = " + '\"{}\"'.format(args.aci_password) + "\n")
        file.write("VC_IP = " + '\"{}\"'.format(args.vcenter_ip) + "\n")
        file.write("VC_USER = " + '\"{}\"'.format(args.vcenter_username) + "\n")
        file.write("VC_PASS = " + '\"{}\"'.format(args.vcenter_password) + "\n")
        file.write("VC_DATACENTER = " + '\"{}\"'.format(args.vcenter_dc) + "\n")
        file.write("VC_DATASTORE = " + '\"{}\"'.format(args.vcenter_ds) + "\n")
        file.write("VC_COMPUTE_CLUSTER = " + '\"{}\"'.format(args.vcenter_cc) + "\n")


def main():
    # show arguments for the user
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group("required arguments")

    required.add_argument("-a", dest="aci_url", help="ACI URL ; http(s)://192.168.1.1/", required=True)
    required.add_argument("-au", dest="aci_username", help="ACI Username", required=True)
    required.add_argument("-ap", dest="aci_password", help="ACI Password", required=True)
    required.add_argument("-v", dest="vcenter_ip", help="vCenter IP ; 192.168.1.1", required=True)
    required.add_argument("-vu", dest="vcenter_username", help="vCenter Username", required=True)
    required.add_argument("-vp", dest="vcenter_password", help="vCenter Password", required=True)
    required.add_argument("-vdc", dest="vcenter_dc", help="vCenter Datacenter ; dc1", required=True)
    required.add_argument("-vds", dest="vcenter_ds", help="vCenter Datastore ; esxi2-DS-SSD", required=True)
    required.add_argument("-vcc", dest="vcenter_cc", help="vCenter Compute Cluster ; cluster1", required=True)

    args = parser.parse_args()

    create_file(args)


if __name__ == '__main__':
    main()
