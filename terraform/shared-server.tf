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
  server_ip   = data.terraform_remote_state.stl_infra.outputs.servers["stl-web-1"].ip
  server_ipv6 = try(
    data.terraform_remote_state.stl_infra.outputs.servers["stl-web-1"].ipv6,
    null,
  )

  servers = {
    "stl-web-1" = {
      ip   = local.server_ip
      id   = data.terraform_remote_state.stl_infra.outputs.servers["stl-web-1"].id
      name = "stl-web-1"
    }
  }
}
