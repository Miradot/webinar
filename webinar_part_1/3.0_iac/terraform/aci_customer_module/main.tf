# ACI TENANT
resource "aci_tenant" "tenant" {
    name        = var.tenant_name
    description = "CREATED WITH TF \\\\o/"
}

# ACI VRF
resource "aci_vrf" "cisco_vrf" {
    tenant_dn   = aci_tenant.tenant.id
    name        = "${var.vrf_name}_VRF"
}

# ACI BRIDE-DOMAIN
resource "aci_bridge_domain" "bd" {
    tenant_dn          = aci_tenant.tenant.id
    relation_fv_rs_ctx = aci_vrf.cisco_vrf.name
    name               = "${var.bd_name}_BD"
}

# ACI SUBNET REFERENCING BD
resource "aci_subnet" "cisco_subnet" {
    bridge_domain_dn   = aci_bridge_domain.bd.id
    ip                 = "${var.network}/24"
    scope              = "public"
}

# ACI APPLICATION-PROFILE
resource "aci_application_profile" "ap" {
    tenant_dn          = aci_tenant.tenant.id
    name               = "${var.ap_name}_APP"
}

# ACI ENDPOINT-GROUP
resource "aci_application_epg" "epg" {
    application_profile_dn = aci_application_profile.ap.id
    relation_fv_rs_bd      = aci_bridge_domain.bd.name
    name                   = "${var.epg_name}_EPG"
}
