output "server_ip"   { value = local.server_ip }
output "server_ipv6" { value = local.server_ipv6 }
output "server_name" { value = "stl-web-1" }

# stl-infra's inventory generator reads .servers[name].ip as the ansible_host.
# Use the Tailscale IP here so Ansible can actually reach SSH.
output "servers" {
  value = {
    "stl-web-1" = {
      ip   = local.server_tailscale_ip
      ipv6 = local.server_ipv6
    }
  }
}
