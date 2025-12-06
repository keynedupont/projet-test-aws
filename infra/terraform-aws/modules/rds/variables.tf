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

variable "instance_class" {
  description = "Type d'instance RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Stockage alloué (GB)"
  type        = number
  default     = 20
}

variable "database_name" {
  description = "Nom de la base de données"
  type        = string
}

variable "username" {
  description = "Nom d'utilisateur RDS"
  type        = string
}

variable "password" {
  description = "Mot de passe RDS"
  type        = string
  sensitive   = true
}

variable "common_tags" {
  description = "Tags communs"
  type        = map(string)
  default     = {}
}

