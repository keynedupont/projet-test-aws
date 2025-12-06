# ============================================================================
# FICHIER : outputs.tf
# DESCRIPTION : Valeurs de sortie de Terraform
# ============================================================================
# Les outputs permettent d'afficher des informations importantes
# après la création des ressources (IP, URL, etc.)

# Output : IP publique de l'instance
output "instance_public_ip" {
  description = "IP publique de l'instance Scaleway"
  value       = scaleway_instance_server.main.public_ip
}

# Output : IP privée de l'instance
output "instance_private_ip" {
  description = "IP privée de l'instance Scaleway"
  value       = scaleway_instance_server.main.private_ip
}

# Output : Commande SSH pour se connecter
output "ssh_command" {
  description = "Commande SSH pour se connecter à l'instance"
  value       = var.ssh_key_id != "" ? "ssh root@${scaleway_instance_server.main.public_ip}" : "SSH non configuré (ssh_key_id vide)"
}

# Output : Informations de la base de données (si activée)
output "database_endpoint" {
  description = "Endpoint de la base de données PostgreSQL"
  value       = var.enable_database ? scaleway_rdb_instance.main[0].endpoint_ip : "Base de données non activée"
}

output "database_port" {
  description = "Port de la base de données PostgreSQL"
  value       = var.enable_database ? scaleway_rdb_instance.main[0].endpoint_port : null
}

output "database_name" {
  description = "Nom de la base de données"
  value       = var.enable_database ? scaleway_rdb_database.main[0].name : null
}

output "database_user" {
  description = "Utilisateur de la base de données"
  value       = var.enable_database ? scaleway_rdb_instance.main[0].user_name : null
}

output "database_password" {
  description = "Mot de passe de la base de données (sensible)"
  value       = var.enable_database ? random_password.db_password[0].result : null
  sensitive   = true  # Ne pas afficher dans les logs
}

# Output : Informations Redis (si activé)
output "redis_endpoint" {
  description = "Endpoint du cluster Redis"
  value       = var.enable_redis ? scaleway_redis_cluster.main[0].endpoint_ip : "Redis non activé"
}

output "redis_port" {
  description = "Port du cluster Redis"
  value       = var.enable_redis ? scaleway_redis_cluster.main[0].endpoint_port : null
}

# Output : URL de l'application
output "app_url" {
  description = "URL de l'application web"
  value       = "http://${scaleway_instance_server.main.public_ip}:8001"
}

output "auth_url" {
  description = "URL du service d'authentification"
  value       = "http://${scaleway_instance_server.main.public_ip}:8000"
}

# Output : Résumé
output "summary" {
  description = "Résumé de l'infrastructure déployée"
  value = <<-EOT
    ✅ Infrastructure Scaleway déployée avec succès !
    
    📦 Instance:
       - IP publique: ${scaleway_instance_server.main.public_ip}
       - IP privée: ${scaleway_instance_server.main.private_ip}
       - Type: ${var.instance_type}
    
    ${var.enable_database ? "🗄️  Base de données PostgreSQL:\n       - Endpoint: ${scaleway_rdb_instance.main[0].endpoint_ip}:${scaleway_rdb_instance.main[0].endpoint_port}\n       - Database: ${scaleway_rdb_database.main[0].name}\n       - User: ${scaleway_rdb_instance.main[0].user_name}\n" : ""}
    ${var.enable_redis ? "🔴 Redis:\n       - Endpoint: ${scaleway_redis_cluster.main[0].endpoint_ip}:${scaleway_redis_cluster.main[0].endpoint_port}\n" : ""}
    🌐 Application:
       - Web: http://${scaleway_instance_server.main.public_ip}:8001
       - Auth: http://${scaleway_instance_server.main.public_ip}:8000
    
    ${var.ssh_key_id != "" ? "🔑 SSH:\n       ssh root@${scaleway_instance_server.main.public_ip}\n" : ""}
  EOT
}

