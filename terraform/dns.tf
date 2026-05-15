data "cloudflare_zone" "main" {
  name = "socialtechnologylab.nl"
}

module "dns_web" {
  source      = "git::ssh://git@github.com/socialtechnologylab/stl-infra.git//modules/cloudflare-dns"
  zone_id     = data.cloudflare_zone.main.id
  name        = "set-crafter"
  ipv4        = local.server_ip
  ipv6        = local.server_ipv6
  create_aaaa = true
}

module "dns_api" {
  source      = "git::ssh://git@github.com/socialtechnologylab/stl-infra.git//modules/cloudflare-dns"
  zone_id     = data.cloudflare_zone.main.id
  name        = "api.set-crafter"
  ipv4        = local.server_ip
  ipv6        = local.server_ipv6
  create_aaaa = true
}
