import unittest
import json
import os
from pyspark.sql import SparkSession
from superannotate_databricks_connector import (
    process_comment,
    process_bounding_box,
    process_vector_instance,
    get_boxes,
    get_vector_dataframe
)


class TestVector(unittest.TestCase):
    def __init__(self, *args):
        super().__init__(*args)
        with open("./tests/test_annotation.json", "r") as f:
            data = json.load(f)
        self.test_data = data
        self.spark = SparkSession.builder.appName('test').getOrCreate()

    def test_bounding_box(self):
        
        for instance in self.test_data["instances"]:
            print(process_vector_instance(instance))
        self.assertEqual("bbox", "bbox")


if __name__ == '__main__':
    unittest.main()
