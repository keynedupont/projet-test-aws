output "rds_endpoint" {
  description = "Endpoint RDS (hostname)"
  value       = aws_db_instance.main.endpoint
}

output "rds_address" {
  description = "Adresse RDS (sans le port)"
  value       = aws_db_instance.main.address
}

output "rds_port" {
  description = "Port RDS"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Nom de la base de données"
  value       = aws_db_instance.main.db_name
}

output "rds_security_group_id" {
  description = "ID du security group RDS"
  value       = aws_security_group.rds.id
}

