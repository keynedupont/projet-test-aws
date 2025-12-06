# RDS - Relational Database Service
# Base de données PostgreSQL managée

# Security Group pour RDS
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group pour RDS PostgreSQL"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ecs_security_group_id != "" ? [1] : []
    content {
      description     = "PostgreSQL depuis ECS"
      from_port       = 5432
      to_port         = 5432
      protocol        = "tcp"
      security_groups = [var.ecs_security_group_id]
    }
  }

  # Fallback : autoriser depuis les subnets privés si security group ECS pas encore créé
  dynamic "ingress" {
    for_each = var.ecs_security_group_id == "" ? [1] : []
    content {
      description = "PostgreSQL depuis subnets privés"
      from_port   = 5432
      to_port     = 5432
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
      Name = "${var.project_name}-rds-sg"
    }
  )
}

# Subnet Group pour RDS (doit être dans au moins 2 AZ)
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-rds-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-rds-subnet-group"
    }
  )
}

# Instance RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-postgres"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.allocated_storage * 2 # Auto-scaling
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.database_name
  username = var.username
  password = var.password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  skip_final_snapshot       = var.environment == "dev" ? true : false
  final_snapshot_identifier = var.environment == "dev" ? null : "${var.project_name}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  deletion_protection        = var.environment == "prod" ? true : false

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  performance_insights_enabled    = var.environment == "prod" ? true : false

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-postgres"
    }
  )
}

