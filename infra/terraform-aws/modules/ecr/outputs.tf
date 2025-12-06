output "app_repository_url" {
  description = "URL du repository ECR pour l'application"
  value       = aws_ecr_repository.app.repository_url
}

output "auth_repository_url" {
  description = "URL du repository ECR pour l'authentification"
  value       = aws_ecr_repository.auth.repository_url
}

output "app_repository_arn" {
  description = "ARN du repository ECR pour l'application"
  value       = aws_ecr_repository.app.arn
}

output "auth_repository_arn" {
  description = "ARN du repository ECR pour l'authentification"
  value       = aws_ecr_repository.auth.arn
}

