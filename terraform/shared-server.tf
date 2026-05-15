# Reference shared stl-web-1 server from stl-infra. set-crafter does not
# create or own this server — it deploys onto it alongside other projects.
data "terraform_remote_state" "stl_infra" {
  backend = "s3"
  config = {
    bucket         = "stl-infra-tf-state"
    key            = "shared/servers/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "terraform-state-locks"
  }
}

locals {
  # Public IPv4/IPv6 — what DNS points at and what end users hit.
  server_ip   = data.terraform_remote_state.stl_infra.outputs.servers["stl-web-1"].ip
  server_ipv6 = try(
    data.terraform_remote_state.stl_infra.outputs.servers["stl-web-1"].ipv6,
    null,
  )

  # SSH is locked behind Tailscale on STL servers, so Ansible has to dial
  # the Tailscale address instead of the public IP. Hardcoded — the shared
  # remote state doesn't expose this yet.
  server_tailscale_ip = "100.126.15.39"

  servers = {
    "stl-web-1" = {
      ip   = local.server_tailscale_ip
      id   = data.terraform_remote_state.stl_infra.outputs.servers["stl-web-1"].id
      name = "stl-web-1"
    }
  }
}
