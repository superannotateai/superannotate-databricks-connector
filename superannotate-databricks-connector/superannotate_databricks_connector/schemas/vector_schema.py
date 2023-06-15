from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    FloatType,
    BooleanType,
    MapType,
    ArrayType
)
from .comment import get_comment_schema


def get_point_schema():
    point_schema = StructType([
        StructField("x", FloatType(), True),
        StructField("y", FloatType(), True)
    ])
    return point_schema


def get_cuboid_schema():
    cuboid_points_schema = StructType([
        StructField("f1", get_point_schema(), True),
        StructField("f2", get_point_schema(), True),
        StructField("r1", get_point_schema(), True),
        StructField("r2", get_point_schema(), True)
    ])
    return cuboid_points_schema


def get_vector_instance_schema():
    instance_schema = StructType([
        StructField("instance_type", StringType(), True),
        StructField("classId", IntegerType(), True),
        StructField("probability", IntegerType(), True),
        StructField("bbox_points", MapType(StringType(), FloatType()), True),
        StructField("polygon_points", ArrayType(FloatType()), True),
        StructField("polygon_exclude", ArrayType(ArrayType(FloatType())),
                    True),
        StructField("cuboid_points", get_cuboid_schema(), True),
        StructField("ellipse_points", MapType(StringType(), FloatType()),
                    True),
        StructField("point_points", MapType(StringType(), FloatType()), True),
        StructField("groupId", IntegerType(), True),
        StructField("locked", BooleanType(), True),
        StructField("attributes", ArrayType(MapType(StringType(),
                                                    StringType())),
                    True),
        StructField("trackingId", StringType(), True),
        StructField("error", StringType(), True),
        StructField("createdAt", StringType(), True),
        StructField("createdBy", MapType(StringType(), StringType()), True),
        StructField("creationType", StringType(), True),
        StructField("updatedAt", StringType(), True),
        StructField("updatedBy", MapType(StringType(), StringType()), True),
        StructField("className", StringType(), True)
    ])
    return instance_schema


def get_vector_schema():
    schema = StructType([
        StructField("image_height", IntegerType(), True),
        StructField("image_width", IntegerType(), True),
        StructField("image_name", StringType(), True),
        StructField("projectId", IntegerType(), True),
        StructField("isPredicted", BooleanType(), True),
        StructField("status", StringType(), True),
        StructField("pinned", BooleanType(), True),
        StructField("annotatorEmail", StringType(), True),
        StructField("qaEmail", StringType(), True),
        StructField("instances", ArrayType(get_vector_instance_schema()),
                    True),
        StructField("bounding_boxes", ArrayType(IntegerType()), True),
        StructField("comments", ArrayType(get_comment_schema()), True)
    ])
    return schema
