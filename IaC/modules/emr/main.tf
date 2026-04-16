# Deploying the Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Provisioning EMR resources

# EMR cluster creation resource
resource "aws_emr_cluster" "cluster" {
  
  # Cluster name
  name = var.name_emr
  
  # Version
  release_label = "emr-7.0.0"
  
  # Applications
  applications  = ["Hadoop", "Spark"]

  # Protection against cluster termination
  termination_protection = false
  
  # Keep the processing job active.
  keep_job_flow_alive_when_no_steps = false
  
  # URI of the folder containing the logs
  log_uri = "s3://${var.name_bucket}/logs/"

  # Role AI of the service
  service_role = var.service_role

  # Attributes of the EC2 instances in the cluster
  ec2_attributes {
    instance_profile = var.instance_profile
    emr_managed_master_security_group = aws_security_group.main_security_group.id
    emr_managed_slave_security_group = aws_security_group.core_security_group.id
  }

  # Master instance type
  master_instance_group {
    instance_type = "m5.4xlarge"
  }

  # Worker instance type
  core_instance_group {
    instance_type  = "m5.2xlarge"
    instance_count = 2
  }

  # Executes the installation script for the Python interpreter and additional packages.
  bootstrap_action {
    name = "Install additional Python packages"
    path = "s3://${var.name_bucket}/scripts/bootstrap.sh"
  }

  # Steps performed in the cluster

  # 1. Copies the files from S3 to the EC2 instances of the cluster. If it fails, terminates the cluster.
  # 2. Copies the log files from S3 to the EC2 instances of the cluster. If it fails, terminates the cluster.
  # 3. Executes a Python script with the job processing. If it fails, keeps the cluster active to investigate the cause of the failure.

  step = [
    {
      name              = "Copy python scripts to EC2 machines"
      action_on_failure = "TERMINATE_CLUSTER"

      hadoop_jar_step = [
        {
          jar        = "command-runner.jar"
          args       = ["aws", "s3", "cp", "s3://${var.name_bucket}/pipeline", "/home/hadoop/pipeline/", "--recursive"]
          main_class = ""
          properties = {}
        }
      ]
    },
    {
      name              = "Copy log files to EC2 machines"
      action_on_failure = "TERMINATE_CLUSTER"

      hadoop_jar_step = [
        {
          jar        = "command-runner.jar"
          args       = ["aws", "s3", "cp", "s3://${var.name_bucket}/logs", "/home/hadoop/logs/", "--recursive"]
          main_class = ""
          properties = {}
        }
      ]
    },
    {
      name              = "Run python script"
      action_on_failure = "CONTINUE"

      hadoop_jar_step = [
        {
          jar        = "command-runner.jar"
          args       = ["spark-submit", "/home/hadoop/pipeline/mllab.py"]
          main_class = ""
          properties = {}
        }
      ]
    }
  ]

  # Spark configuration file
  configurations_json = <<EOF
    [
    {
    "Classification": "spark-defaults",
      "Properties": {
      "spark.pyspark.python": "/home/hadoop/conda/bin/python",
      "spark.dynamicAllocation.enabled": "true",
      "spark.network.timeout":"800s",
      "spark.executor.heartbeatInterval":"60s"
      }
    }
  ]
  EOF

}