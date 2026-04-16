# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# S3 Variables

variable "name_bucket" {
  type        = string
  description = "Bucket name"
}

variable "files_bucket" {
  type        = string
  description = "Folder from which the Python scripts will be retrieved for processing"
}

variable "files_data" {
  type        = string
  description = "Folder from which the data will be retrieved"
}

variable "files_bash" {
  type        = string
  description = "Folder from which the bash scripts will be obtained"
}