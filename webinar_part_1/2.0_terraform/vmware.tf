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
        ipv4_address = "1.1.1.100"
        ipv4_netmask = "24"
      }
      ipv4_gateway = "1.1.1.1"
    }
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
        ipv4_address = "2.2.2.100"
        ipv4_netmask = "24"
      }
      ipv4_gateway = "2.2.2.1"
    }
  }
}