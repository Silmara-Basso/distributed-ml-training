# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Upload to S3

# Imports
import os
import os.path
from IaC.pipeline.mllab_log import record_log

# Defines the function to upload a directory in parquet format to an S3 bucket
def upload_processed_data_bucket(df, path, s3_path, bucket, EMR_execution_environment):
	
    # Checks if the function is being executed in an EMR environment
    if EMR_execution_environment:
        # Checks if any object already exists in the specified path in S3
        if len(list(bucket.objects.filter(Prefix=(s3_path)).limit(1))) > 0:
            # If it already exists, overwrite the parquet file in the local path
            df.write.mode("Overwrite").partitionBy("label").parquet(path)
        else:
            # If it doesn't exist, write the parquet file to the local path without overwriting
            df.write.partitionBy("label").parquet(path)
    else:
        # Writes to the log
        record_log("record_log - This script runs only on EMR clusters", bucket)

# Define a function to upload a machine learning model to an S3 bucket
def upload_ml_model_bucket(model, path, s3_path, bucket, EMR_execution_environment):
	
    # Checks if the function is being executed in an EMR environment
    if EMR_execution_environment:
        # Checks if any object already exists in the specified path in S3
        if len(list(bucket.objects.filter(Prefix=(s3_path)).limit(1))) > 0:
            # If it already exists, overwrite the model in the specified path
            model.write().overwrite().save(path)
        else:
            # If it doesn't exist, save the model in the specified path without overwriting
            model.save(path)
    else:
        # Writes to the log
        record_log("record_log - This script runs only on EMR clusters", bucket)

