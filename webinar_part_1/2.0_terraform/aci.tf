## VARIABLES DECLARED IN terraform.tvars
variable "ACI_URL" {}
variable "ACI_USER" {}
variable "ACI_PASS" {}


# VARIABLES
variable "filter_groups" {
  description = "Create EPGs with these names"
  default     = [
      {contract = "web", filter: "web", port = "http"},
      {contract = "db", filter: "db", port="1433"}
  ]
}

# ACI PROVIDER
provider "aci" {
    username    = var.ACI_USER
    password    = var.ACI_PASS
    url         = var.ACI_URL
    insecure    = true
}

# ACI TENANT
resource "aci_tenant" "tenant" {
    name        = "TENANT_TERRAFORM_DEMO"
    description = "CREATED WITH TF \\\\o/"
}

# ACI VRF
resource "aci_vrf" "vrf" {
    tenant_dn   = aci_tenant.tenant.id
    name        = "demo_VRF"
}

# ACI BRIDE-DOMAIN
resource "aci_bridge_domain" "bd_web" {
    tenant_dn          = aci_tenant.tenant.id
    relation_fv_rs_ctx = aci_vrf.vrf.name
    name               = "web"
}

resource "aci_bridge_domain" "bd_db" {
    tenant_dn          = aci_tenant.tenant.id
    relation_fv_rs_ctx = aci_vrf.vrf.name
    name               = "db"
}

# ACI SUBNET REFERENCING BD
resource "aci_subnet" "subnet_1" {
    bridge_domain_dn   = aci_bridge_domain.bd_web.id
    ip                 = "1.1.1.1/24"
}

resource "aci_subnet" "subnet_2" {
    bridge_domain_dn   = aci_bridge_domain.bd_db.id
    ip                 = "2.2.2.1/24"
}

# ACI APPLICATION-PROFILE
resource "aci_application_profile" "ap" {
    tenant_dn          = aci_tenant.tenant.id
    name               = "demo_AP"
}

# ACI CONTRACT
resource "aci_contract" "aci_contract" {
    count       = length(var.filter_groups)
    tenant_dn   = aci_tenant.tenant.id
    name        = lookup(var.filter_groups[count.index], "contract")
    scope       = "tenant"
}

# ACI CONTRACT SUBJECT REFERENCING CONTRACT AND FILTER
resource "aci_contract_subject" "aci_contract_subject" {
    count         = length(var.filter_groups)
    contract_dn   = aci_contract.aci_contract[count.index].id
    name          = lookup(var.filter_groups[count.index], "contract")
    relation_vz_rs_subj_filt_att = [aci_filter.aci_filter[count.index].name]
}

# ACI FILTER
resource "aci_filter" "aci_filter" {
    count     = length(var.filter_groups)
    tenant_dn = aci_tenant.tenant.id
    name      = lookup(var.filter_groups[count.index], "filter")
}

# ACI FILTER ENTRY
resource "aci_filter_entry" "filter_entry" {
    count       = length(var.filter_groups)
    name        = lookup(var.filter_groups[count.index], "filter")
    filter_dn   = aci_filter.aci_filter[count.index].id
    ether_t     = "ip"
    prot        = "tcp"
    d_from_port = lookup(var.filter_groups[count.index], "port")
    d_to_port   = lookup(var.filter_groups[count.index], "port")
}

# ACI ENDPOINT-GROUP NET-1
resource "aci_application_epg" "epg_web" {
    application_profile_dn = aci_application_profile.ap.id
    relation_fv_rs_bd      = aci_bridge_domain.bd_web.name
    name                   = "web"
    relation_fv_rs_prov    = ["web"]
    relation_fv_rs_cons    = ["db", "ping"]
    relation_fv_rs_dom_att = ["uni/vmmp-VMware/dom-ACI"]
}

# ACI ENDPOINT-GROUP NET-2
resource "aci_application_epg" "epg_db" {
    application_profile_dn = aci_application_profile.ap.id
    relation_fv_rs_bd      = aci_bridge_domain.bd_db.name
    name                   = "db"
    relation_fv_rs_prov    = ["db", "ping"]
    relation_fv_rs_cons    = []
    relation_fv_rs_dom_att = ["uni/vmmp-VMware/dom-ACI"]
    relation_fv_rs_graph_def = ["uni/tn-common/brc-ping/graphcont"]
}
