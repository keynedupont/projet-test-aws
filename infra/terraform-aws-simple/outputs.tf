# ============================================================================
# FICHIER : outputs.tf
# DESCRIPTION : Valeurs de sortie après création des ressources
# ============================================================================
# Les outputs sont affichés après "terraform apply" et peuvent être réutilisés
# dans d'autres configurations Terraform ou scripts.

# Output 1 : ID de l'instance EC2
# ID unique de l'instance (ex: i-0123456789abcdef0)
# Utile pour référencer l'instance dans d'autres scripts ou la console AWS
output "ec2_instance_id" {
  description = "ID de l'instance EC2"
  value       = aws_instance.main.id     # Récupère l'ID de la ressource aws_instance.main
}

# Output 2 : IP publique de l'instance
# IP publique = Adresse IP accessible depuis Internet
# Si Elastic IP activé, on utilise l'IP Elastic (fixe)
# Sinon, on utilise l'IP publique normale (peut changer au redémarrage)
output "ec2_public_ip" {
  description = "IP publique de l'instance EC2"
  # Condition ternaire : si enable_elastic_ip = true, utiliser l'IP Elastic, sinon l'IP normale
  # [0] = premier élément du tableau (car count peut créer 0 ou 1 ressource)
  value       = var.enable_elastic_ip ? aws_eip.main[0].public_ip : aws_instance.main.public_ip
}

# Output 3 : DNS public de l'instance
# DNS = Nom de domaine (ex: ec2-12-34-56-78.eu-north-1.compute.amazonaws.com)
# Plus facile à retenir qu'une IP, mais peut changer si l'IP change
output "ec2_public_dns" {
  description = "DNS public de l'instance EC2"
  value       = aws_instance.main.public_dns
}

# Output 4 : Commande SSH prête à l'emploi
# Génère automatiquement la commande SSH complète pour se connecter
# Utile pour copier-coller directement dans le terminal
output "ssh_command" {
  description = "Commande SSH pour se connecter à l'instance"
  # Si ssh_key_name existe, génère la commande SSH, sinon message d'erreur
  value       = var.ssh_key_name != "" ? "ssh -i ~/.ssh/${var.ssh_key_name}.pem ec2-user@${var.enable_elastic_ip ? aws_eip.main[0].public_ip : aws_instance.main.public_ip}" : "SSH non configuré (ssh_key_name vide)"
}

# Output 5 : URL du service d'authentification
# URL complète pour accéder au service auth (port 8000)
output "auth_service_url" {
  description = "URL du service d'authentification"
  # Construit l'URL avec l'IP publique et le port 8000
  value       = "http://${var.enable_elastic_ip ? aws_eip.main[0].public_ip : aws_instance.main.public_ip}:8000"
}

# Output 6 : URL de l'application web
# URL complète pour accéder à l'application (port 8001)
output "app_service_url" {
  description = "URL de l'application web"
  # Construit l'URL avec l'IP publique et le port 8001
  value       = "http://${var.enable_elastic_ip ? aws_eip.main[0].public_ip : aws_instance.main.public_ip}:8001"
}

# Output 7 : Commande pour vérifier Docker
# Commande à exécuter en SSH pour voir si Docker fonctionne
output "docker_status_command" {
  description = "Commande pour vérifier le statut de Docker (à exécuter en SSH)"
  value       = "sudo systemctl status docker"
}

# Output 8 : Commande pour vérifier Docker Compose
# Commande pour voir la version de Docker Compose installée
output "docker_compose_version_command" {
  description = "Commande pour vérifier la version de Docker Compose"
  value       = "docker-compose --version"
}

# Output 9 : Guide des prochaines étapes
# Instructions complètes pour déployer l'application après création de l'infrastructure
output "next_steps" {
  description = "Prochaines étapes"
  # Heredoc multi-lignes avec les instructions
  value = <<-EOT
    1. Connectez-vous en SSH : ${var.ssh_key_name != "" ? "ssh -i ~/.ssh/${var.ssh_key_name}.pem ec2-user@${var.enable_elastic_ip ? aws_eip.main[0].public_ip : aws_instance.main.public_ip}" : "Configurez ssh_key_name dans terraform.tfvars"}
    2. Vérifiez Docker : sudo systemctl status docker
    3. Clonez votre repo ou copiez vos fichiers
    4. Lancez docker-compose up -d
    5. Accédez à l'app : http://${var.enable_elastic_ip ? aws_eip.main[0].public_ip : aws_instance.main.public_ip}:8001
  EOT
}

