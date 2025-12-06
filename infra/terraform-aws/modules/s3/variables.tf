variable "project_name" {
  description = "Nom du projet"
  type        = string
}

variable "environment" {
  description = "Environnement (dev, staging, prod)"
  type        = string
}

variable "ml_data_bucket_name" {
  description = "Nom du bucket S3 pour les données ML"
  type        = string
}

variable "common_tags" {
  description = "Tags communs"
  type        = map(string)
  default     = {}
}

