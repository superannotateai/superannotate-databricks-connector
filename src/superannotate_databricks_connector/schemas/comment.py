from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    FloatType,
    BooleanType,
    MapType,
    ArrayType
)


def get_comment_schema():
    comment_schema = StructType([
        StructField("correspondence",
                    ArrayType(MapType(
                        StringType(),
                        StringType())),
                    True),
        StructField("x", FloatType(), True),
        StructField("y", FloatType(), True),
        StructField("resolved", BooleanType(), True),
        StructField("createdAt", StringType(), True),
        StructField("createdBy", MapType(
            StringType(),
            StringType()),
                    True),
        StructField("creationType", StringType(), True),
        StructField("updatedAt", StringType(), True),
        StructField("updatedBy", MapType(
            StringType(),
            StringType()),
                    True)
    ])
    return comment_schema
