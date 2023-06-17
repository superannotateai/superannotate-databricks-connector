import unittest
import json
from pyspark.sql import SparkSession
from superannotate_databricks_connector.text import (
    get_text_dataframe
)


class TestVectorDataFrame(unittest.TestCase):
    def test_vector_dataframe(self):
        spark = SparkSession.builder.master("local").getOrCreate()
        with open("./tests/test_data/text/example_annotation.json",
                  "r") as f:
            data = json.load(f)

        actual_df = get_text_dataframe([data], spark)

        expected_df = spark.read.parquet(
            "./tests/test_data/text/expected_df.parquet")
        self.assertEqual(sorted(actual_df.collect()),
                         sorted(expected_df.collect()))


if __name__ == '__main__':
    unittest.main()
