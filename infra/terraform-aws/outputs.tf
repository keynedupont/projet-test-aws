# VPC
output "vpc_id" {
  description = "ID du VPC créé"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block du VPC"
  value       = module.vpc.vpc_cidr
}

output "private_subnet_ids" {
  description = "IDs des sous-réseaux privés"
  value       = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  description = "IDs des sous-réseaux publics"
  value       = module.vpc.public_subnet_ids
}

# RDS
output "rds_endpoint" {
  description = "Endpoint RDS (hostname)"
  value       = module.rds.rds_endpoint
  sensitive   = true
}

output "rds_database_name" {
  description = "Nom de la base de données"
  value       = module.rds.database_name
}

# ElastiCache Redis
output "redis_endpoint" {
  description = "Endpoint Redis"
  value       = module.elasticache.redis_endpoint
  sensitive   = true
}

# S3
output "s3_ml_data_bucket_name" {
  description = "Nom du bucket S3 pour les données ML"
  value       = module.s3.ml_data_bucket_name
}

# ECR
output "ecr_repository_app_url" {
  description = "URL du repository ECR pour l'application"
  value       = module.ecr.app_repository_url
}

output "ecr_repository_auth_url" {
  description = "URL du repository ECR pour l'authentification"
  value       = module.ecr.auth_repository_url
}

# ECS
output "ecs_cluster_name" {
  description = "Nom du cluster ECS"
  value       = module.ecs.cluster_name
}

output "ecs_service_app_name" {
  description = "Nom du service ECS pour l'application"
  value       = module.ecs.app_service_name
}

output "ecs_service_auth_name" {
  description = "Nom du service ECS pour l'authentification"
  value       = module.ecs.auth_service_name
}

# ALB
output "alb_dns_name" {
  description = "DNS name de l'Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "Zone ID de l'ALB"
  value       = module.alb.alb_zone_id
}

