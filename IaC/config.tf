# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Configuration for Remote State, Terraform Version, and Provider

# Terraform version
terraform {
  required_version = "~> 1.7"

  # Provider AWS
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend used for remote state
  backend "s3" {
    encrypt = true
    # This bucket must be created manually
    bucket  = "mllab-l1-terraform-<aws-id>"
    key     = "mllab-l1.tfstate"
    region  = "us-east-2"
  }
}

# Provider region
provider "aws" {
  region = "us-east-2"
}