# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Storage module with S3

# Criação do bucket
resource "aws_s3_bucket" "create_bucket" {

  # Destroy the bucket even if it contains content
  bucket = var.name_bucket
  
  force_destroy = true

  tags = {
    Name        = "Bucket for use in conjunction with AWS EMR"
    Environment = "Scripts"
  }

}

# Bucket versioning
resource "aws_s3_bucket_versioning" "versioning_bucket" {
  
  bucket = aws_s3_bucket.create_bucket.id
  
  versioning_configuration {status = var.versioning_bucket}
  
  depends_on = [aws_s3_bucket.create_bucket]
}

# Blocks public access
resource "aws_s3_bucket_public_access_block" "example" {
  
  bucket = aws_s3_bucket.create_bucket.id

  block_public_policy     = false
  
  restrict_public_buckets = false
}

# Módulo S3
module "s3_object" {
  source       = "./s3_objects"
  files_bucket = var.files_bucket
  files_data   = var.files_data
  files_bash   = var.files_bash
  name_bucket  = aws_s3_bucket.create_bucket.bucket
}


