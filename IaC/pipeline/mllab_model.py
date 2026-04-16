# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Machine Learning

# Installs Python package within Python code
import subprocess
comando = "pip install numpy"
subprocess.run(comando.split())

# Imports
import os
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
from IaC.pipeline.mllab_upload_s3 import dsa_upload_modelos_ml_bucket

# Class for training and evaluating the model
def TrainEvaluateModel(spark, classifier, features, classes, train, test, bucket, bucket_name, EMR_execution_environment):

    # Method for defining the classifier type
    def FindMtype(classifier):
        M = classifier
        Mtype = type(M).__name__
        return Mtype
    
    # Creates an instance of the class
    Mtype = FindMtype(classifier)
    
    # Method for training the model and evaluating the results
    def IntanceFitModel(Mtype, classifier, classes, features, train):
        
        if Mtype in("LogisticRegression"):
  
            # Hyperparameter grid for optimization
            paramGrid = (ParamGridBuilder().addGrid(classifier.maxIter, [10, 15, 20]).build())
            
            # Cross-validation for hyperparameter optimization
            crossval = CrossValidator(estimator = classifier,
                                      estimatorParamMaps = paramGrid,
                                      evaluator = MulticlassClassificationEvaluator(),
                                      numFolds = 2)

            # Create training object
            fitModel = crossval.fit(train)

            return fitModel
    
    # Model training
    fitModel = IntanceFitModel(Mtype, classifier, classes, features, train)
    
    # Print some metrics
    if fitModel is not None:

        if Mtype in("LogisticRegression"):
            BestModel = fitModel.bestModel
            record_log( Mtype, bucket)
            global LR_coefficients
            LR_coefficients = BestModel.coefficientMatrix.toArray()
            global LR_BestModel
            LR_BestModel = BestModel
        
    # Establish columns of the table that will compare the results of each classifier
    columns = ['Classifier', 'Result']
    
    # Extract predictions from the model with test data
    predictions = fitModel.transform(test)
    
    # Create the evaluator
    MC_evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
    
    # Calculate the accuracy
    accuracy = (MC_evaluator.evaluate(predictions)) * 100
    
    # Register in log
    record_log( "Classificador: " + Mtype + " / Acuracia: " + str(accuracy), bucket)
    
    # Generates the result table with the classifier name and the accuracy score    Mtype = [Mtype]
    score = [str(accuracy)]
    Mtype = [Mtype]
    score = [str(accuracy)]
    result = spark.createDataFrame(zip(Mtype,score), schema=columns)
    result = result.withColumn('Result',result.Result.substr(0, 5))
    
    # Path to record the result
    path = f"s3://{bucket_name}/output/" + Mtype[0] + '_' + train.name if EMR_execution_environment else 'output/' + Mtype[0] + '_' + train.name
    s3_path = 'output/' + Mtype[0] + '_' + train.name
    
    # Save the result to the bucket
    dsa_upload_modelos_ml_bucket(fitModel, path , s3_path , bucket, EMR_execution_environment)
    return result

# Function to create the Machine Learning model
def create_ml_models(spark, HTFfeaturizedData, TFIDFfeaturizedData, W2VfeaturizedData, bucket, bucket_name, EMR_execution_environment):

    # I will only use one classifier, but it is possible to include others
    classifiers = [LogisticRegression()] 

    # Attribute list
    featureDF_list = [HTFfeaturizedData, TFIDFfeaturizedData, W2VfeaturizedData]

    # Loop for each attribute
    for featureDF in featureDF_list:

        record_log( featureDF.name + " Results: ", bucket)
        
        # Training and testing division
        train, test = featureDF.randomSplit([0.7, 0.3],seed = 11)

        train.name = featureDF.name
        
        # Attributes in Spark format (input data)
        features = featureDF.select(['features']).collect()
        
        # Classes (output data)
        classes = featureDF.select("label").distinct().count()

        columns = ['Classifier', 'Result']
        
        # List of terms to create the initial dataframe with the results of the classifiers, which will be updated in the loop
        vals = [("Place Holder","N/A")]
        
        # Create the dataframe with the results of the classifiers, which will be updated in the loop
        results = spark.createDataFrame(vals, columns)

        # Loop pela lista de classificadores
        for classifier in classifiers:
            
            # Creates an object of the class
            new_result = TrainEvaluateModel(spark,
                                               classifier,
                                               features,
                                               classes,
                                               train,
                                               test, 
                                               bucket, 
                                               bucket_name, 
                                               EMR_execution_environment)
            
            # Generates the result table with the classifier name and the accuracy score
            results = results.union(new_result)
            results = results.where("Classifier!='Place Holder'")



        