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

variable "public_subnet_ids" {
  description = "IDs des subnets publics"
  type        = list(string)
}

variable "ecs_app_service_name" {
  description = "Nom du service ECS pour l'application (pour référence)"
  type        = string
}

variable "ecs_auth_service_name" {
  description = "Nom du service ECS pour l'authentification (pour référence)"
  type        = string
}

variable "common_tags" {
  description = "Tags communs"
  type        = map(string)
  default     = {}
}

