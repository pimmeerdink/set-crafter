variable "CLOUDFLARE_API_TOKEN" {
  type      = string
  sensitive = true
}

variable "AWS_REGION" {
  type    = string
  default = "eu-central-1"
}

variable "project_name" {
  type    = string
  default = "set-crafter"
}

variable "domain" {
  type    = string
  default = "set-crafter.socialtechnologylab.nl"
}

variable "targets" {
  type = any
}

variable "groups" {
  type    = any
  default = {}
}
