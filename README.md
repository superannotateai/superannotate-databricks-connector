# Python Package for SuperAnnotate on Databricks
This Python package provides a set of utilities for working with SuperAnnotate data on Databricks. It includes functionality to process SuperAnnotate data and save it to Delta tables.

# Features
Process SuperAnnotate vector instance data.
Convert processed data into a PySpark DataFrame.
Write DataFrame to a Delta table, creating the table if it does not exist, or updating the existing table with new data.

# Requirements
Python 3.7+
PySpark 3.0+
Delta Lake 1.0+
Databricks Runtime 7.3 LTS+

# Installation
 
```bash
pip install superspark
```


# Usage
First, import the required functions:

```python
from superspark import get_vector_dataframe, write_annotations_to_delta
```
Then, you can process your annotations and convert them to a DataFrame:

```python
annotations = [...]  # Your SuperAnnotate data
spark = SparkSession.builder.getOrCreate()
df = get_vector_dataframe(annotations, spark)
```

Finally, you can write the DataFrame to a Delta table:

```python
write_annotations_to_delta(df, "your_database", "your_table", spark)
```
Replace "your_database" and "your_table" with the name of your database and table.

# Testing
To run the unit tests, use the following command:

```bash
python -m unittest d
```
