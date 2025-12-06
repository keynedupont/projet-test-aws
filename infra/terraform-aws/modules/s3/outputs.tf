output "ml_data_bucket_name" {
  description = "Nom du bucket S3 pour les données ML"
  value       = aws_s3_bucket.ml_data.id
}

output "ml_data_bucket_arn" {
  description = "ARN du bucket S3 pour les données ML"
  value       = aws_s3_bucket.ml_data.arn
}

