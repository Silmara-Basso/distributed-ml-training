# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Log Generation

import subprocess
comando = "pip install pendulum"
subprocess.run(comando.split())

import os
import os.path
import pendulum
import traceback

# mllab_grava_log function that receives text and a bucket object as parameters
def mllab_grava_log(mltext, bucket):
    
    # Set the path to store the logs to the current directory if "logs" is a directory; otherwise, use "/home/hadoop"
    path = "." if (os.path.isdir("logs")) else "/home/hadoop"
    
    # Get the current moment using a pendulum
    cur_moment = pendulum.now()
    file_date = cur_moment.format('YYYYMMDD')
    date_time_log= cur_moment.format('YYYY-MM-DD HH:mm:ss')
    
    # Assemble the log file name with the path, date, and prefix -log_spark.txt
    file_name = path + "/logs/" + file_date + "-log_spark.txt"

    text_log = ''
    
    # Try opening the log file for writing, in append mode if the file already exists, or create a new file.
    try:

        if os.path.isfile(file_name):  
            arquivo = open(file_name, "a")  
            text_log = text_log + '\n'  

        else:

            # Creates a new file if it doesn't exist
            arquivo = open(file_name, "w")  
    
    # Catches any exceptions during the attempt to open the file
    except:
        print("Error in the attempt to access the file for creating logs")

        # Re-run the exception with the traceback for diagnostic purposes
        raise Exception(traceback.format_exc())  
    
    # Adds the date, time, and log text to the log_text variable
    text_log = text_log + "[" + date_time_log + "] - " + mltext

    # Write the log to the file
    arquivo.write(text_log)  

    print(mltext)  

    arquivo.close()  
    
    # Upload the log file to the specified bucket with a filename that includes the date
    bucket.upload_file(file_name, 'logs/' + file_date + "-log_spark.txt")
