variable "aws_region" {
  description = "Région AWS pour déployer les ressources"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Nom du projet (utilisé pour nommer les ressources)"
  type        = string
  default     = "projet"
}

variable "environment" {
  description = "Environnement (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "L'environnement doit être dev, staging ou prod."
  }
}

# VPC
variable "vpc_cidr" {
  description = "CIDR block pour le VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Zones de disponibilité à utiliser"
  type        = list(string)
  default     = ["eu-north-1a", "eu-north-1b"]
}

# RDS
variable "rds_instance_class" {
  description = "Type d'instance RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  description = "Stockage alloué pour RDS (GB)"
  type        = number
  default     = 20
}

variable "rds_database_name" {
  description = "Nom de la base de données"
  type        = string
  default     = "my_ml_project"
}

variable "rds_username" {
  description = "Nom d'utilisateur RDS"
  type        = string
  default     = "app"
}

variable "rds_password" {
  description = "Mot de passe RDS (⚠️ À définir via terraform.tfvars ou variable d'environnement)"
  type        = string
  sensitive   = true
}

# ElastiCache Redis
variable "redis_node_type" {
  description = "Type de nœud Redis"
  type        = string
  default     = "cache.t3.micro"
}

# ECS
variable "ecs_desired_count" {
  description = "Nombre de tâches ECS désirées"
  type        = number
  default     = 1
}

variable "ecs_cpu" {
  description = "CPU alloué par tâche ECS (unités: 256 = 0.25 vCPU)"
  type        = number
  default     = 512
}

variable "ecs_memory" {
  description = "Mémoire allouée par tâche ECS (MB)"
  type        = number
  default     = 1024
}

# S3
variable "s3_ml_data_bucket_name" {
  description = "Nom du bucket S3 pour les données ML"
  type        = string
  default     = "projet-ml-data"
}

# Tags communs
variable "common_tags" {
  description = "Tags communs à appliquer à toutes les ressources"
  type        = map(string)
  default     = {}
}

