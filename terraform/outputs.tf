output "server_ip"   { value = local.server_ip }
output "server_ipv6" { value = local.server_ipv6 }
output "server_name" { value = "stl-web-1" }

output "servers" {
  value = {
    "stl-web-1" = {
      ip   = local.server_ip
      ipv6 = local.server_ipv6
    }
  }
}
