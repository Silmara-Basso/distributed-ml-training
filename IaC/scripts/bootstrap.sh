# Deploying a Distributed Machine Learning Training Stack with PySpark on Amazon EMR
# Python Environment Setup Script

# Download Miniconda (Python language interpreter)
wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p $HOME/conda

# Configure miniconda in the PATH
echo -e '\nexport PATH=$HOME/conda/bin:$PATH' >> $HOME/.bashrc && source $HOME/.bashrc

# Install the packages via conda
conda install -y boto3 pendulum numpy scikit-learn 

# Install the packages via pip
pip install --upgrade pip
pip install findspark
pip install pendulum
pip install boto3
pip install numpy
pip install python-dotenv
pip install scikit-learn

# Create the folders for the pipeline and logs
mkdir $HOME/pipeline
mkdir $HOME/logs

