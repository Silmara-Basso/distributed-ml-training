# distributed-ml-training
Distributed Machine Learning training using PySpark on Amazon Elastic MapReduce (EMR) with IAC

The Lab structure includes setting up an EMR cluster on AWS, configured to run distributed Machine Learning tasks. The training stack is designed to be scalable and resilient, leveraging AWS services for resource management and monitoring. Automated deployment and continuous integration are facilitated by infrastructure-as-code (Terraform) scripts and templates, ensuring environment replicability and consistency.

### Instructions


Create the Docker image.
````
docker build -t mllab-l1-terraform-image:v1 .
````


Create the Docker container.
```
docker run -dit --name mllab-l1 -v ./IaC:/iac mllab-l1-terraform-image:v1 /bin/bash
```

Check the Terraform and AWS CLI versions using the commands below.
```
terraform version

aws --version
```
#### Further instructions can be found in the IAC folder's readme file.
