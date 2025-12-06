terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend S3 pour le state (optionnel - à configurer après création du bucket S3)
  # backend "s3" {
  #   bucket         = "projet-terraform-state"
  #   key            = "terraform.tfstate"
  #   region        = var.aws_region
  #   encrypt        = true
  #   dynamodb_table = "projet-terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

