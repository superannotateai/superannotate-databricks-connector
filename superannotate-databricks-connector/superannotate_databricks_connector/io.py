from delta.tables import DeltaTable
from pyspark.sql import DataFrame, SparkSession
import logging 


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def write_annotations_to_delta(annotations: DataFrame, database: str, table: str, spark: SparkSession) -> None:
    """
    Takes a list of annotations and writes them to the specified delta table

    Args:
        annotations (dataframe): Spark dataframe with annotations
        database (string): The name of the database to write to
        table (string): The name of the delta table to write to
        spark (sparkContext): The spark context
        create_if_not_exists (Bool): Should the function create the delta table if it does not exists, or raise an exception,

    Returns:
        None
    """
    logging.info('Writing annotations to delta...')
    # Set the database and table names
    database_name = database
    table_name = f"{database_name}.{table}"

    # Check if the table exists
    table_exists = spark.catalog.tableExists(table_name)

    if not table_exists:
        if create_if_not_exists:
            # If the table does not exist, create the database if it does not exist
            logging.warning(f"{database_name}.{table} not found.") 
            logging.info("Creating new table..." )
            spark.sql(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            # Write the DataFrame as a new Delta table in the specified schema and partitioned by projectId
            annotations.write.format("delta").partitionBy("projectId").mode("overwrite").saveAsTable(table_name)
        else:
            logging.warning(f"{database_name}.{table} not found.")
            raise Exception(f"{database_name}.{table} not found. To create table set the parameter create_if_not_exists=True")
    else:
        # If the table exists
        logging.info("Merging new records..." )

        # Read the managed Delta table
        delta_table = DeltaTable.forName(spark, table_name)

        # Define the merge condition using unique identifiers
        merge_condition = "source.image_name = target.image_name AND source.projectId = target.projectId"

        # Merge the DataFrame into the existing managed Delta table
        delta_table.alias("target")\
            .merge(annotations.alias("source"), merge_condition)\
            .whenMatchedUpdateAll()\
            .whenNotMatchedInsertAll()\
            .execute()
