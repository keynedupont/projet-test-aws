# Modules Terraform pour l'infrastructure AWS
# Chaque module gère une partie de l'infrastructure
# Ordre important pour résoudre les dépendances

# 1. VPC - Réseau virtuel (base de tout)
module "vpc" {
  source = "./modules/vpc"

  project_name     = var.project_name
  environment      = var.environment
  vpc_cidr         = var.vpc_cidr
  availability_zones = var.availability_zones
  common_tags      = var.common_tags
}

# 2. IAM - Rôles et permissions (nécessaire pour ECS)
module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  environment  = var.environment
  common_tags  = var.common_tags
}

# 3. ECR - Repositories Docker (nécessaire pour ECS)
module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
  environment  = var.environment
  common_tags = var.common_tags
}

# 4. S3 - Stockage pour données ML (indépendant)
module "s3" {
  source = "./modules/s3"

  project_name           = var.project_name
  environment            = var.environment
  ml_data_bucket_name    = var.s3_ml_data_bucket_name
  common_tags            = var.common_tags
}

# 5. ALB - Application Load Balancer (crée les target groups nécessaires pour ECS)
module "alb" {
  source = "./modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  # Les noms de services ECS ne sont pas critiques pour la création de l'ALB
  ecs_app_service_name = "${var.project_name}-app-service"
  ecs_auth_service_name = "${var.project_name}-auth-service"
  common_tags       = var.common_tags
}

# 6. ECS - Cluster et services pour conteneurs (utilise les target groups ALB)
module "ecs" {
  source = "./modules/ecs"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
  ecr_app_repository_url = module.ecr.app_repository_url
  ecr_auth_repository_url = module.ecr.auth_repository_url
  rds_endpoint       = module.rds.rds_endpoint
  rds_username       = var.rds_username
  rds_password       = var.rds_password
  rds_database_name  = var.rds_database_name
  redis_endpoint     = module.elasticache.redis_endpoint
  ecs_task_role_arn  = module.iam.ecs_task_role_arn
  ecs_exec_role_arn  = module.iam.ecs_exec_role_arn
  alb_security_group_id = module.alb.alb_security_group_id
  app_target_group_arn = module.alb.app_target_group_arn
  auth_target_group_arn = module.alb.auth_target_group_arn
  desired_count      = var.ecs_desired_count
  cpu                = var.ecs_cpu
  memory             = var.ecs_memory
  common_tags        = var.common_tags

  depends_on = [module.alb]
}

# 7. RDS - Base de données PostgreSQL (créé avant ECS, utilise VPC CIDR comme fallback)
module "rds" {
  source = "./modules/rds"

  project_name         = var.project_name
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  vpc_cidr             = module.vpc.vpc_cidr
  private_subnet_ids   = module.vpc.private_subnet_ids
  ecs_security_group_id = "" # Sera mis à jour après création d'ECS (optionnel)
  instance_class       = var.rds_instance_class
  allocated_storage    = var.rds_allocated_storage
  database_name        = var.rds_database_name
  username             = var.rds_username
  password             = var.rds_password
  common_tags          = var.common_tags
}

# 8. ElastiCache - Redis pour cache (créé avant ECS, utilise VPC CIDR comme fallback)
module "elasticache" {
  source = "./modules/elasticache"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  vpc_cidr           = module.vpc.vpc_cidr
  private_subnet_ids = module.vpc.private_subnet_ids
  ecs_security_group_id = "" # Sera mis à jour après création d'ECS (optionnel)
  node_type          = var.redis_node_type
  common_tags        = var.common_tags
}

