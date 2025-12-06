variable "project_name" {
  description = "Nom du projet"
  type        = string
}

variable "environment" {
  description = "Environnement (dev, staging, prod)"
  type        = string
}

variable "common_tags" {
  description = "Tags communs"
  type        = map(string)
  default     = {}
}

