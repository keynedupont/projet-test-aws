# ElastiCache - Redis
# Cache Redis managé pour améliorer les performances

# Security Group pour Redis
resource "aws_security_group" "redis" {
  name        = "${var.project_name}-redis-sg"
  description = "Security group pour ElastiCache Redis"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ecs_security_group_id != "" ? [1] : []
    content {
      description     = "Redis depuis ECS"
      from_port       = 6379
      to_port         = 6379
      protocol        = "tcp"
      security_groups = [var.ecs_security_group_id]
    }
  }

  # Fallback : autoriser depuis les subnets privés si security group ECS pas encore créé
  dynamic "ingress" {
    for_each = var.ecs_security_group_id == "" ? [1] : []
    content {
      description = "Redis depuis subnets privés"
      from_port   = 6379
      to_port     = 6379
      protocol    = "tcp"
      cidr_blocks = [var.vpc_cidr]
    }
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis-sg"
    }
  )
}

# Subnet Group pour ElastiCache
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-redis-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis-subnet-group"
    }
  )
}

# Parameter Group pour Redis (configuration)
resource "aws_elasticache_parameter_group" "main" {
  name   = "${var.project_name}-redis-params"
  family = "redis7"

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis-params"
    }
  )
}

# Cluster Redis
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.project_name}-redis"
  description                = "Redis cluster pour ${var.project_name}"

  engine               = "redis"
  engine_version        = "7.0"
  node_type            = var.node_type
  port                 = 6379
  parameter_group_name = aws_elasticache_parameter_group.main.name

  num_cache_clusters = var.environment == "prod" ? 2 : 1

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled  = false # Désactivé pour compatibilité (peut être activé en prod)

  automatic_failover_enabled = var.environment == "prod" ? true : false
  multi_az_enabled           = var.environment == "prod" ? true : false

  snapshot_retention_limit = var.environment == "prod" ? 5 : 1
  snapshot_window         = "03:00-05:00"

  maintenance_window = "mon:05:00-mon:06:00"

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redis"
    }
  )
}

