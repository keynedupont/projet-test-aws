variable "project_name" {
  description = "Nom du projet"
  type        = string
}

variable "environment" {
  description = "Environnement (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID du VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "IDs des subnets privés"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "ID du security group ECS (pour autoriser l'accès)"
  type        = string
  default     = "" # Sera fourni par le module ECS
}

variable "vpc_cidr" {
  description = "CIDR block du VPC (fallback si security group ECS pas disponible)"
  type        = string
  default     = ""
}

variable "node_type" {
  description = "Type de nœud Redis"
  type        = string
  default     = "cache.t3.micro"
}

variable "common_tags" {
  description = "Tags communs"
  type        = map(string)
  default     = {}
}

