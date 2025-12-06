output "alb_dns_name" {
  description = "DNS name de l'Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID de l'ALB"
  value       = aws_lb.main.zone_id
}

output "alb_arn" {
  description = "ARN de l'ALB"
  value       = aws_lb.main.arn
}

output "alb_security_group_id" {
  description = "ID du security group ALB"
  value       = aws_security_group.alb.id
}

output "app_target_group_arn" {
  description = "ARN du target group pour l'application"
  value       = aws_lb_target_group.app.arn
}

output "auth_target_group_arn" {
  description = "ARN du target group pour l'authentification"
  value       = aws_lb_target_group.auth.arn
}

