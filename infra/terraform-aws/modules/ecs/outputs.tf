output "cluster_name" {
  description = "Nom du cluster ECS"
  value       = aws_ecs_cluster.main.name
}

output "cluster_arn" {
  description = "ARN du cluster ECS"
  value       = aws_ecs_cluster.main.arn
}

output "app_service_name" {
  description = "Nom du service ECS pour l'application"
  value       = aws_ecs_service.app.name
}

output "auth_service_name" {
  description = "Nom du service ECS pour l'authentification"
  value       = aws_ecs_service.auth.name
}

output "ecs_security_group_id" {
  description = "ID du security group ECS"
  value       = aws_security_group.ecs.id
}

