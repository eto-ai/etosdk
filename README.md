![Apache License](https://img.shields.io/github/license/eto-ai/etosdk?style=for-the-badge)
[![Read The Doc](https://img.shields.io/readthedocs/etosdk?style=for-the-badge)](https://etosdk.readthedocs.io/)
![Pypi version](https://img.shields.io/pypi/v/etosdk?style=for-the-badge)


# Eto Labs Python SDK

This is the python SDK for Eto, the AI focused data platform for teams bringing AI models to production.
The python SDK makes it easy to integrate Eto's features into your AI training and analysis workflow.
For a full walkthrough of Eto SDK features, see the [Getting Started](https://github.com/eto-ai/etosdk/blob/main/notebooks/Getting%20Started.ipynb)
Jupyter notebook

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
eto.configure(account='<fill_in_your_account_name>', token='<your_api_token>')
```

The above configuration function creates a configuration file under `$XDG_CONFIG_HOME/eto/eto.conf`,
which is usually `~/.config/eto/eto.conf`.

## Ingesting data

To create an ingestion job to convert raw data in Coco format and create a new dataset:

```python
job = eto.ingest_coco('<dataset_name>',
                      {'image_dir': '<path/to/images>',
                       'annotation': '<path/to/annotations>',
                       'extras': {'key': 'value'}})
```

The ingestion job will run asynchronously server-side and convert the data to [Rikai (parquet) format](https://github.com/eto-ai/rikai).
Once complete, you should be able to see it in the data registry:

```python
# Retrieve all datasets in the registry
# as a DataFrame with project_id, dataset_id, uri, and created_at
eto.list_datasets() 

# Get detailed information about a particular dataset
# (Specifically get the schema)
eto.get_dataset('<dataset_name>')
```

## Pandas

Accessing a particular dataset is easy via Pandas:

```python
import eto
import pandas as pd
# when you `import eto` we add a pandas extension to read Eto datasets
df = pd.read_eto('<dataset_name>')
```

Using the dataframe it's easy to satisfy your analytics needs for your dataset.

## Training 

To train a pytorch model, you can use the Dataset/DataLoader classes in Rikai: 

```python
import eto
from rikai.torch.vision import Dataset
# When you `import eto`, we can automatically resolve the dataset_name
# by looking it up in the Eto dataset registry
dataset = Dataset('<dataset_name>') 

for next_record in dataset:
    # training loop
    pass
```

A plain pytorch dataloader is also available from `rikai.torch.data.DataLoader`.