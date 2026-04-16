# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Variable Definition Script 

variable "name_bucket" {
  type        = string
  description = "Bucket name"
}

variable "versioning_bucket" {
  type        = string
  description = "Defines whether bucket versioning will be enabled"
}

variable "files_bucket" {
  type        = string
  description = "Folder from which the Python scripts will be retrieved for processing"
  default     = "./pipeline"
}

variable "files_data" {
  type        = string
  description = "Folder from which the data will be retrieved"
  default     = "./data"
}

variable "files_bash" {
  type        = string
  description = "Folder from which the bash scripts will be obtained"
  default     = "./scripts"
}

variable "name_emr" {
  type        = string
  description = "EMR cluster name"
}
