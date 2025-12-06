output "ecs_task_role_arn" {
  description = "ARN du rôle IAM pour les tâches ECS"
  value       = aws_iam_role.ecs_task.arn
}

output "ecs_exec_role_arn" {
  description = "ARN du rôle IAM pour l'exécution ECS"
  value       = aws_iam_role.ecs_exec.arn
}

