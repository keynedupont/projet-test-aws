output "redis_endpoint" {
  description = "Endpoint Redis (configuration endpoint pour cluster)"
  value       = aws_elasticache_replication_group.main.configuration_endpoint_address
}

output "redis_primary_endpoint" {
  description = "Endpoint Redis primaire"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "redis_port" {
  description = "Port Redis"
  value       = aws_elasticache_replication_group.main.port
}

output "redis_security_group_id" {
  description = "ID du security group Redis"
  value       = aws_security_group.redis.id
}

