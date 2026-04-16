# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Main Script

import subprocess
comando = "pip install boto3"
subprocess.run(comando.split())

# Imports
import os
import boto3
import traceback
import pyspark 
from pyspark.sql import SparkSession
from IaC.pipeline.mllab_log import record_log
from mllab_processing import clean_transform_data
from IaC.pipeline.mllab_model import create_ml_models

# Bucket Name
BUCKET_NAME = "mllab-l1-<aws-id>"

# AWS access keys
AWSACCESSKEYID = "put-your-aws-key-here"
AWSSECRETKEY = "put-your-aws-secret-key-here"


print("\nRecord_log - Initializing Processing.")

# Creates a resource for accessing S3 via Python code
s3_resource = boto3.resource('s3', aws_access_key_id = AWSACCESSKEYID, aws_secret_access_key = AWSSECRETKEY)

# Defines the object for accessing the bucket via Python
bucket = s3_resource.Bucket(BUCKET_NAME)

record_log("Record_log - Bucket Found.", bucket)

record_log("Record_log - Initializing Apache Spark.", bucket)

# Creates the Spark Session and logs any errors that may occur during the initialization process
try:
	spark = SparkSession.builder.appName("MLLab_Lab1").getOrCreate()
	spark.sparkContext.setLogLevel("ERROR")
except:
	record_log("Record_log - An error occurred while initializing Spark", bucket)
	record_log(traceback.format_exc(), bucket)
	raise Exception(traceback.format_exc())

record_log("Record_log - Spark Inicializado.", bucket)

# Defines the Amazon EMR runtime environment
EMR_execution_environment = False if os.path.isdir('Data/') else True

# Cleaning and transformation block
try:
	DataHTFfeaturized, DataTFIDFfeaturized, DataW2Vfeaturized = clean_transform_data(spark, 
																							  bucket, 
																							  BUCKET_NAME, 
																							  EMR_execution_environment)
except:
	record_log("Record_log - An error occurred while cleaning and transforming the data", bucket)
	record_log(traceback.format_exc(), bucket)
	spark.stop()
	raise Exception(traceback.format_exc())

# Building block for creating Machine Learning models
try:
	create_ml_models (spark, 
					     DataHTFfeaturized, 
					     DataTFIDFfeaturized, 
					     DataW2Vfeaturized, 
					     bucket, 
					     BUCKET_NAME, 
					     EMR_execution_environment)
except:
	record_log("Record_log - An error occurred while creating the machine learning models", bucket)
	record_log(traceback.format_exc(), bucket)
	spark.stop()
	raise Exception(traceback.format_exc())

record_log("Record_log - Models Created and Saved in S3.", bucket)

record_log("Record_log - Processamento Finalizado com Sucesso.", bucket)

# This terminates Spark (closes the EMR cluster)
spark.stop()



