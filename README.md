# Eto Labs Python SDK

This is the python SDK for Eto, the AI focused data platform for teams bringing AI models to production.
The python SDK makes it easy to integrate Eto's features into your AI training and analysis workflow.

## Installation

The Eto python SDK is available on PyPI and can be installed via Pip:

```bash
pip install etosdk
```

Eto SDK is compatible with Python 3.7+

## Setup

Before using the SDK for the first time, you must configure it with your Eto API url and the API token.

```python
import eto
eto.configure(url='<eto-api-url>', token='<api-token>')
```

The above configuration function creates a configuration file under `$XDG_CONFIG_HOME/eto/eto.conf`,
which is usually `~/.config/eto/eto.conf`.

## Ingesting data

To create an ingestion job to convert raw data in Coco format and create a new dataset:

```python
import eto
job = eto.ingest_coco('<dataset_name>',
                      {'image_dir': '<path/to/images>',
                       'annotations': '<path/to/annotations>',
                       'extras': {'key': 'value'}})
```

The ingestion job will run asynchronously server-side and convert the data to [Rikai (parquet) format](github.com/eto-ai/rikai).
Once complete, you should be able to see it in the data registry:

```python
import eto

eto.list_datasets() # list all datasets

eto.get_dataset('<dataset_name>') # get information about a single dataset
```

## Analysis

Accessing a particular dataset is easy via Pandas:

```python
import eto
import pandas as pd

df = pd.read_eto('<dataset_name>') # Eto SDK adds a pandas extension
```

## Training 

To train a pytorch model, you can use the Dataset/DataLoader classes in Rikai: 

```python
import eto
from rikai.torch.vision import Dataset

dataset = Dataset('<dataset_name>') # Eto SDK adds an extension to Rikai to resolve dataset references 

for next_record in dataset:
    # training loop
    pass
```

A plain pytorch dataloader is also available from `rikai.torch.data.DataLoader`.

## Local Spark configuration

For now, the Eto SDK relies on PySpark locally to read some of the custom Rikai types like annotations.
While PySpark should be automatically installed as a transitive dependency, you may find that you need
to change the Spark configurations to suit your local setup.

Your `$SPARK_HOME/conf/spark-defaults.conf` file should look something like the following:

```text
spark.sql.extensions               ai.eto.rikai.sql.spark.RikaiSparkSessionExtensions
spark.jars.packages                ai.eto:rikai_2.12:0.0.13,org.apache.hadoop:hadoop-aws:3.2.0

# AWS
spark.executor.extraJavaOptions -Dcom.amazonaws.services.s3.enableV4=true -Dio.netty.tryReflectionSetAccessible=true
spark.driver.extraJavaOptions -Dcom.amazonaws.services.s3.enableV4=true -Dio.netty.tryReflectionSetAccessible=true
spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version 2
spark.hadoop.com.amazonaws.services.s3.enableV4 true
fs.AbstractFileSystem.s3a.impl org.apache.hadoop.fs.s3a.S3A
fs.s3a.impl org.apache.hadoop.fs.s3a.S3AFileSystem
fs.s3a.aws.credentials.provider com.amazonaws.auth.InstanceProfileCredentialsProvider,com.amazonaws.auth.DefaultAWSCredentialsProviderChain
```