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
        StructField("bbox_points", MapType(StringType(),
                                           FloatType()), True),
        StructField("polygon_points", ArrayType(FloatType()), True),
        StructField("polygon_exclude", ArrayType(
                                        ArrayType(
                                         FloatType())),
                    True),
        StructField("cuboid_points", get_cuboid_schema(), True),
        StructField("ellipse_points", MapType(StringType(),
                                              FloatType()), True),
        StructField("point_points", MapType(StringType(),
                                            FloatType()), True),
        StructField("groupId", IntegerType(), True),
        StructField("locked", BooleanType(), True),
        StructField("attributes", ArrayType(
                                    MapType(StringType(),
                                            StringType())), True),
        StructField("trackingId", StringType(), True),
        StructField("error", StringType(), True),
        StructField("createdAt", StringType(), True),
        StructField("createdBy", MapType(StringType(),
                                         StringType()), True),
        StructField("creationType", StringType(), True),
        StructField("updatedAt", StringType(), True),
        StructField("updatedBy", MapType(StringType(),
                                         StringType()), True),
        StructField("className", StringType(), True)
    ])
    return instance_schema


def get_boxes_schema():
    instance_schema = StructType([
            StructField("classes", ArrayType(IntegerType()), True),
            StructField("boxes", ArrayType(ArrayType(IntegerType())), True)
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


def process_comment(comment):
    comment["x"] = float(comment.get("x"))
    comment["y"] = float(comment.get("y"))
    return comment


def process_vector_instance(instance, custom_id_map=None):
    """
    Takes one annotation instance and unpacks it.

    Args:
        instance (dict). One instance from the SuperAnnotate annotation format.

    Returns:
        (dict) reformated instance
    """
    return {
        'instance_type': instance['type'],
        'classId': instance["classId"] if custom_id_map is None
        else custom_id_map.get(instance["className"]),
        'probability': instance.get('probability'),
        'bbox_points': {k: float(v) for k, v in instance['points'].items()}
        if instance["type"] == "bbox" else None,
        'polygon_points': [float(p) for p in instance['points']]
        if instance["type"] == "polygon" else None,
        'polygon_exclude': instance["exclude"]
        if instance["type"] == "polygon" else None,
        'point_points': {"x": float(instance["x"]),
                         "y": float(instance["y"])
                         } if instance["type"] == "point" else None,
        'ellipse_points': {"cx": float(instance["cx"]),
                           "cy": float(instance["cy"]),
                           "rx": float(instance["rx"]),
                           "ry": float(instance["ry"]),
                           "angle": float(instance["angle"])}
        if instance["type"] == "ellipse" else None,
        'cuboid_points': {outer_k: {inner_k: float(inner_v) 
                                    for inner_k, inner_v in outer_v.items()}
                          for outer_k, outer_v in instance['points'].items()}
        if instance["type"] == "cuboid" else None,
        'groupId': instance['groupId'],
        'locked': instance.get('locked'),
        'attributes': instance['attributes'],
        'trackingId': instance.get('trackingId'),
        'error': instance.get('error'),
        'createdAt': instance.get('createdAt'),
        'createdBy': instance.get('createdBy'),
        'creationType': instance.get('creationType'),
        'updatedAt': instance.get('updatedAt'),
        'updatedBy': instance.get('updatedBy'),
        'className': instance.get('className')
    }


def process_bounding_box(bbox, custom_id_map=None):
    """Class that converts a bounding box and a class to
        XYXYC format

        LEFT: left of the bounding box
        TOP: top of the bounding box
        RIGHT: right of the bounding box
        BOTTOM: bottom of the bounding box
        CLASS: class id of the bounding box"""
    
    object_box = [int(x) for x in [bbox["points"]["x1"],
                                   bbox["points"]["y1"],
                                   bbox["points"]["x2"],
                                   bbox["points"]["y2"]]]
    object_class = bbox["classId"]
    if custom_id_map is not None:
        object_class = custom_id_map.get(bbox["className"])
    object_box.append(object_class)
    return object_box


def get_boxes(instances, custom_id_map=None):
    """
    Takes all the instances and return the bounding boxes
    as a one dimensional array with XYXYC format
    """
    boxes = []
    for instance in instances:
        if instance["type"] == "bbox":
            ob = process_bounding_box(instance, custom_id_map)
            boxes.extend(ob)
    return boxes


def get_vector_dataframe(annotations, spark, custom_id_map=None):
    """
    Transforms a list of SuperAnnotate annotations from a vector
    project into a spark dataframe

    Args:
        annotations (list[dict]): The annotations in the SuperAnnotate format
        spark (sparkContext): The spark context

    Returns:
        spark_df: A spark dataframe containing the annotations.
    """
    rows = []
    for item in annotations:
        flattened_item = {
            "image_height": item["metadata"]["height"],
            "image_width": item["metadata"]["width"],
            "image_name": item["metadata"]["name"],
            'projectId': item["metadata"]['projectId'],
            'isPredicted': item["metadata"]['isPredicted'],
            'status': item["metadata"]['status'],
            'pinned': item["metadata"]['pinned'],
            'annotatorEmail': item["metadata"]['annotatorEmail'],
            'qaEmail': item["metadata"]['qaEmail'],
            "instances": [process_vector_instance(instance, custom_id_map)
                          for instance in item["instances"]],
            "bounding_boxes": get_boxes(item["instances"], custom_id_map),
            "comments": [process_comment(comment)
                         for comment in item["comments"]]
            }
        rows.append(flattened_item)
    schema = get_vector_schema()
    spark_df = spark.createDataFrame(rows, schema=schema)
    return spark_df
