variable "VC_IP" {}
variable "VC_COMPUTE_CLUSTER" {}
variable "VC_DATASTORE" {}
variable "VC_DATACENTER" {}
variable "VC_USER" {}
variable "VC_PASS" {}

provider "vsphere" {
  user           = var.VC_USER
  password       = var.VC_PASS
  vsphere_server = var.VC_IP

  # If you have a self-signed cert
  allow_unverified_ssl = true
}

data "vsphere_datacenter" "dc" {
  name = var.VC_DATACENTER
}

data "vsphere_datastore" "datastore" {
  name          = var.VC_DATASTORE
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_compute_cluster" "cluster" {
  name          = var.VC_COMPUTE_CLUSTER
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network_web" {
  name          = "${aci_tenant.tenant.name}|${aci_application_profile.ap.name}|${aci_application_epg.epg_web.name}"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network_db" {
  name          = "${aci_tenant.tenant.name}|${aci_application_profile.ap.name}|${aci_application_epg.epg_db.name}"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_virtual_machine" "template" {
  name = "ubuntu_template"
  datacenter_id = data.vsphere_datacenter.dc.id
}

resource "vsphere_virtual_machine" "vm_web" {
  name             = "DEMOVM_web"
  resource_pool_id = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id

  num_cpus = 2
  memory   = 2048
  guest_id = data.vsphere_virtual_machine.template.guest_id

  network_interface {
    network_id = data.vsphere_network.network_web.id
  }

  disk {
    label = "disk0"
    size  = 16
  }
  clone {
    template_uuid = data.vsphere_virtual_machine.template.id

    customize {
      dns_server_list = ["8.8.8.8"]

      linux_options {
        domain = "miradot.local"
        host_name = "web"
      }
      network_interface {
        ipv4_address = "10.140.140.100"
        ipv4_netmask = "24"
      }
      ipv4_gateway = "10.140.140.1"
    }
  }
  provisioner "remote-exec" {
    inline = [
      "mkdir .ssh",
      "chmod 700 .ssh"
    ]
    connection {
      user = "miradot"
      password = var.ACI_PASS
      host = vsphere_virtual_machine.vm_web.clone[0].customize[0].network_interface[0].ipv4_address
    }
  }
  provisioner "file" {
    source = "../ansible_bak/authorized_keys"
    destination = ".ssh/authorized_keys"
    connection {
      user = "miradot"
      password = var.ACI_PASS
      host = vsphere_virtual_machine.vm_web.clone[0].customize[0].network_interface[0].ipv4_address
    }
  }
    provisioner "remote-exec" {
    inline = [
      "chmod 700 .ssh/authorized_keys"
    ]
    connection {
      user = "miradot"
      password = var.ACI_PASS
      host = vsphere_virtual_machine.vm_web.clone[0].customize[0].network_interface[0].ipv4_address
    }
  }
  provisioner "local-exec" {
    command = "ansible-playbook ../ansible_bak/web.yml -i ../ansible_bak/hosts --private-key='../ansible_bak/id_rsa' --vault-password-file .vault_password.txt"
  }
}

resource "vsphere_virtual_machine" "vm_db" {
  name             = "DEMOVM_db"
  resource_pool_id = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id

  num_cpus = 2
  memory   = 2048
  guest_id = data.vsphere_virtual_machine.template.guest_id

  network_interface {
    network_id = data.vsphere_network.network_db.id
  }

  disk {
    label = "disk0"
    size  = 16
  }
  clone {
    template_uuid = data.vsphere_virtual_machine.template.id

    customize {
      dns_server_list = ["8.8.8.8"]

      linux_options {
        domain = "miradot.local"
        host_name = "db"
      }
      network_interface {
        ipv4_address = "10.141.141.100"
        ipv4_netmask = "24"
      }
      ipv4_gateway = "10.141.141.1"
    }
  }
  provisioner "remote-exec" {
    inline = [
      "mkdir .ssh",
      "chmod 700 .ssh"
    ]
    connection {
      user = "miradot"
      password = var.ACI_PASS
      host = vsphere_virtual_machine.vm_db.clone[0].customize[0].network_interface[0].ipv4_address
    }
  }
  provisioner "file" {
    source = "../ansible_bak/authorized_keys"
    destination = ".ssh/authorized_keys"
    connection {
      user = "miradot"
      password = var.ACI_PASS
      host = vsphere_virtual_machine.vm_db.clone[0].customize[0].network_interface[0].ipv4_address
    }
  }
    provisioner "remote-exec" {
    inline = [
      "chmod 700 .ssh/authorized_keys"
    ]
    connection {
      user = "miradot"
      password = var.ACI_PASS
      host = vsphere_virtual_machine.vm_db.clone[0].customize[0].network_interface[0].ipv4_address
    }
  }
  provisioner "local-exec" {
    command = "ansible-playbook ../ansible_bak/db.yml -i ../ansible_bak/hosts --private-key='../ansible_bak/id_rsa' --vault-password-file .vault_password.txt"
  }
}