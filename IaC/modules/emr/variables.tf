# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# EMR Variables

variable "name_emr" {
  type        = string
  description = "EMR cluster name"
}

variable "name_bucket" {
  type        = string
  description = "Bucket name"
}

variable "instance_profile" {}

variable "service_role" {}
