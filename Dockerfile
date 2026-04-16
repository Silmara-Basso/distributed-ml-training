# Dockerfile for creating a custom image with Terraform and AWS CLI
FROM ubuntu:latest

LABEL maintainer="Silmara"

# Update and install necessary dependencies for Terraform and AWS CLI
RUN apt-get update && \
    apt-get install -y wget unzip curl git openssh-client iputils-ping

# Set the Terraform version (adjust as needed)
ENV TERRAFORM_VERSION=1.7.4

# Download and install Terraform
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Create the /iac folder as a mount point for a volume. This allows users to mount their local infrastructure as code (IaC) files into the container.
RUN mkdir /iac
VOLUME /iac

# Create the Downloads folder and install the AWS CLI. This allows users to interact with AWS services from within the container.
RUN mkdir Downloads && \
    cd Downloads && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

# Set the default command to run when the container starts. This will open a bash shell, allowing users to interact with the container and use Terraform and AWS CLI.
CMD ["/bin/bash"]
