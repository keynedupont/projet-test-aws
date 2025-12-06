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

variable "public_subnet_ids" {
  description = "IDs des subnets publics"
  type        = list(string)
}

variable "ecr_app_repository_url" {
  description = "URL du repository ECR pour l'application"
  type        = string
}

variable "ecr_auth_repository_url" {
  description = "URL du repository ECR pour l'authentification"
  type        = string
}

variable "rds_endpoint" {
  description = "Endpoint RDS"
  type        = string
}

variable "rds_username" {
  description = "Nom d'utilisateur RDS"
  type        = string
}

variable "rds_password" {
  description = "Mot de passe RDS"
  type        = string
  sensitive   = true
}

variable "rds_database_name" {
  description = "Nom de la base de données"
  type        = string
}

variable "redis_endpoint" {
  description = "Endpoint Redis"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "ARN du rôle IAM pour les tâches ECS"
  type        = string
}

variable "ecs_exec_role_arn" {
  description = "ARN du rôle IAM pour l'exécution ECS"
  type        = string
}

variable "desired_count" {
  description = "Nombre de tâches ECS désirées"
  type        = number
  default     = 1
}

variable "cpu" {
  description = "CPU alloué par tâche (unités: 256 = 0.25 vCPU)"
  type        = number
  default     = 512
}

variable "memory" {
  description = "Mémoire allouée par tâche (MB)"
  type        = number
  default     = 1024
}

variable "alb_security_group_id" {
  description = "ID du security group ALB"
  type        = string
  default     = "" # Sera fourni par le module ALB
}

variable "app_target_group_arn" {
  description = "ARN du target group pour l'application"
  type        = string
  default     = "" # Sera fourni par le module ALB
}

variable "auth_target_group_arn" {
  description = "ARN du target group pour l'authentification"
  type        = string
  default     = "" # Sera fourni par le module ALB
}

variable "common_tags" {
  description = "Tags communs"
  type        = map(string)
  default     = {}
}

