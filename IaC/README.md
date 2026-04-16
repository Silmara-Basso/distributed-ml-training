# Instruction part 2

The data used in the Project was prepared based on the data available at the link below:
https://ai.stanford.edu/~amaas/data/sentiment/

Include your AWS ID in config.tf and terraform.tfvars to ensure uniqueness.

In the mllab.py script, add your AWS ID and AWS keys.

### Manually create the S3 bucket named: mllab-l1-terraform-aws-id (replace aws_id with your AWS ID)

### adjust replacing aws_id with your AWS ID and access keys
** terraform.tfvars **
name_bucket       = "mllab-l1-aws-id"
name_emr          = "mllab-l1-emr-aws-id"

** config.tf **
bucket  = "mllab-l1-terraform-aws-id"

** mllab.py **
# Bucket Name
# BUCKET_NAME = "mllab-l1-aws-id"

# AWS access keys
AWSACCESSKEYID = "put-your-aws-key-here"
AWSSECRETKEY = "put-your-aws-secret-key-here"

### RUN:
````
terraform init

terraform plan -out terraform.tfplan

terraform apply
````


### Monitor the pipeline's execution through the AWS interface.


### Destroy
````
terraform plan -destroy -out terraform.tfplan
terraform apply terraform.tfplan
````
