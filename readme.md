# Superannotate Databricks Connector
SuperAnnotate is the cornerstone of your data labeling pipeline. It brings you a cutting-edge annotation tool for all types of data including image, video, text, LiDAR, audio, and more.

This Python package provides a set of utilities for working with SuperAnnotate data on Databricks. It includes functionality to process SuperAnnotate data and save it to Delta tables.


### Features
- Process SuperAnnotate vector instance data.
- Convert processed data into a PySpark DataFrame.
- Write DataFrame to a Delta table, creating the table if it does not exist, or updating the existing table with new data.


### Example notebooks.
Copy the notebooks in the demo folder to your databricks workspace to get started with SuperAnnotate quickly!

### Installation
```bash
pip install your-package-name
``` 

### Usage
First import the required function

```python
from your_package_name import get_vector_dataframe, write_annotations_to_delta
from superannotate import SAClient
```

You can then convert your annotations to a spark dataframe

```python
sa = SAClient(token="<TOKEN>")
annotations = sa.get_annotations("<PROJECT_NAME>)
df = get_vector_dataframe(annotations, spark)
```

Finally you can write the data frame to a delta table

```python
write_annotations_to_delta(df, "your_database", "your_table", spark)
```
