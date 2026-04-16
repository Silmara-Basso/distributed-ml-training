# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Processing

# Imports
import os
import os.path
import numpy
from pyspark.ml.feature import * 
from pyspark.sql import functions
from pyspark.sql.functions import * 
from pyspark.sql.types import StringType,IntegerType
from pyspark.ml.classification import *
from pyspark.ml.evaluation import *
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from IaC.pipeline.mllab_log import record_log
from IaC.pipeline.mllab_upload_s3 import upload_processed_data_bucket

# Define a function to calculate the quantity and percentage of null values ​​in each column of a DataFrame
def calculate_null_values(df):
    
    null_columns_counts = []
    numRows = df.count()

    for k in df.columns:
        
        nullRows = df.where(col(k).isNull()).count()

        if(nullRows > 0):
            
            # Creates a tuple containing the column name, the number of null values, and the percentage of null values
            temp = k, nullRows, (nullRows / numRows) * 100

            null_columns_counts.append(temp)

    # Returns the list of columns with the count and percentage of null values
    return null_columns_counts

# Function for cleaning and transformation
def clean_transform_data(spark, bucket, bucket_name, EMR_execution_environment):
	
	# Define the path to store the processing result
	path =  f"s3://{bucket_name}/data/" if EMR_execution_environment else  "data/"

	# Writes to the log
	record_log("record_log - Importing the data...", bucket)

	# Upload the CSV file from the specified path into a Spark DataFrame
	reviews = spark.read.csv(path+'dataset.csv', header=True, escape="\"")

	# Writes to the log
	record_log("record_log - Data imported successfully.", bucket)
	record_log("record_log - Total records: " + str(reviews.count()), bucket)
	record_log("record_log - Checking for null values.", bucket)

	# Calculate the missing values in the dataset
	null_columns_calc_list = calculate_null_values(reviews)

	# Action based on missing values
	if (len(null_columns_calc_list) > 0):
		for column in null_columns_calc_list:
			record_log("record_log - Column " + str(column[0]) + " has " + str(column[2]) + " null values", bucket)
		reviews = reviews.dropna()
		record_log("record_log - Null values removed", bucket)
		record_log("record_log - Total records after cleaning: " + str(reviews.count()), bucket)
	else:
		record_log("record_log - No null values detected.", bucket)

	# Writes to the log
	record_log("record_log - Checking class balance.", bucket)
	
	# Count the records of positive and negative reviews
	count_positive_sentiment = reviews.where(reviews['sentiment'] == "positive").count()
	count_negative_sentiment = reviews.where(reviews['sentiment'] == "negative").count()

	# Writes to the log
	record_log("record_log - There are " + str(count_positive_sentiment) + " positive reviews and " + str(count_negative_sentiment) + " negative reviews", bucket)

	# Creates the DataFrame
	df = reviews

	record_log("record_log - Transforming the Data", bucket)
	
	# Create the indexer
	indexer = StringIndexer(inputCol="sentiment", outputCol="label")
	
	# Train the indexer
	df = indexer.fit(df).transform(df)

	record_log("record_log - Cleaning the Data", bucket)
	
	# Cleans the text data by removing HTML tags, special characters, extra spaces, and converting to lowercase
	df = df.withColumn("review", regexp_replace(df["review"], '<.*/>', ''))
	df = df.withColumn("review", regexp_replace(df["review"], '[^A-Za-z ]+', ''))
	df = df.withColumn("review", regexp_replace(df["review"], ' +', ' '))
	df = df.withColumn("review", lower(df["review"]))

	record_log("record_log - Text Data Cleaned", bucket)
	record_log("record_log - Tokenizing Text Data.", bucket)

	# Creates the tokenizer (converts text data into numerical representations)
	regex_tokenizer = RegexTokenizer(inputCol="review", outputCol="words", pattern="\\W")

	# Applies the tokenizer
	df = regex_tokenizer.transform(df)

	record_log("record_log - Removing Stop Words.", bucket)

	# Creates the object to remove stop words (common words that do not add much meaning to the text)
	remover = StopWordsRemover(inputCol="words", outputCol="filtered")

	# Applies the object and removes stop words
	feature_data = remover.transform(df)

	record_log("record_log - Applying HashingTF.", bucket)

	# Create and apply the word processor
	hashingTF = HashingTF(inputCol="filtered", outputCol="rawfeatures", numFeatures=250)
	HTFfeaturizedData = hashingTF.transform(feature_data)

	record_log("record_log - Aplicando IDF.", bucket)

	idf = IDF(inputCol="rawfeatures", outputCol="features")
	idfModel = idf.fit(HTFfeaturizedData)
	TFIDFfeaturizedData = idfModel.transform(HTFfeaturizedData)
	
	# Adjusts the names of the objects
	TFIDFfeaturizedData.name = 'TFIDFfeaturizedData'
	HTFfeaturizedData = HTFfeaturizedData.withColumnRenamed("rawfeatures","features")
	HTFfeaturizedData.name = 'HTFfeaturizedData' 

	record_log("record_log - Applying IDF.", bucket)
	record_log("record_log - Applying Word2Vec.", bucket)

	# Create and apply the word processor
	word2Vec = Word2Vec(vectorSize=250, minCount=5, inputCol="filtered", outputCol="features")
	model = word2Vec.fit(feature_data)
	W2VfeaturizedData = model.transform(feature_data)

	record_log("record_log - Padronizando os Dados com MinMaxScaler.", bucket)

	# Create and apply the pattern standardization processor (scales the features to a specific range, in this case, between 0 and 1)
	scaler = MinMaxScaler(inputCol="features", outputCol="scaledFeatures")
	scalerModel = scaler.fit(W2VfeaturizedData)
	scaled_data = scalerModel.transform(W2VfeaturizedData)
	
	# Adjusts the names of the objects
	W2VfeaturizedData = scaled_data.select('sentiment','review','label','scaledFeatures')
	W2VfeaturizedData = W2VfeaturizedData.withColumnRenamed('scaledFeatures','features')
	W2VfeaturizedData.name = 'W2VfeaturizedData'

	record_log("record_log - Saving Clean and Transformed Data.", bucket)

	# Define the path to save the results, which will be used in the function to upload to the bucket
	path = f"s3://{bucket_name}/data/" if EMR_execution_environment else 'data/'
	s3_path = 'data/'

	# Upload para o bucket S3
	upload_processed_data_bucket(HTFfeaturizedData, path + 'HTFfeaturizedData', s3_path + 'HTFfeaturizedData' , bucket, EMR_execution_environment)
	upload_processed_data_bucket(TFIDFfeaturizedData, path + 'TFIDFfeaturizedData', s3_path + 'TFIDFfeaturizedData', bucket, EMR_execution_environment)
	upload_processed_data_bucket(W2VfeaturizedData, path + 'W2VfeaturizedData', s3_path + 'W2VfeaturizedData', bucket, EMR_execution_environment)

	return HTFfeaturizedData, TFIDFfeaturizedData, W2VfeaturizedData


	