terraform {
  required_version = ">= 1.0"

  required_providers {
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 4.0" }
    aws        = { source = "hashicorp/aws", version = "~> 5.0" }
  }

  # Shared AWS S3 bucket for all STL projects, keyed by project name.
  backend "s3" {
    bucket         = "stl-infra-tf-state"
    key            = "projects/set-crafter/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.AWS_REGION
}

provider "cloudflare" {
  api_token = var.CLOUDFLARE_API_TOKEN
}
