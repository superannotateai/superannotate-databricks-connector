from .schemas import get_vector_schema


def process_comment(comment):
    comment["x"] = float(comment.get("x"))
    comment["y"] = float(comment.get("y"))
    return comment


def process_vector_instance(instance,custom_id_map=None):
    """
    Takes one annotation instance and unpacks it.

    Args:
        instance (dict). One instance from the SuperAnnotate annotation format.

    Returns:
        (dict) reformated instance
    """
    return {
    'instance_type': instance['type'],
    'classId': instance["classId"] if custom_id_map is None else custom_id_map.get(instance["className"]),
    'probability': instance.get('probability'),
    'bbox_points': {k:float(v) for k,v in instance['points'].items()} if instance["type"] == "bbox" else None,
    'polygon_points': [float(p) for p in instance['points']] if instance["type"] == "polygon" else None,
    'polygon_exclude': instance["exclude"] if instance["type"] == "polygon" else None,
    'point_points':{"x":float(instance["x"]),
                      "y":float(instance["y"])} if instance["type"] == "point" else None,
    'ellipse_points':{"cx":float(instance["cx"]),
                      "cy":float(instance["cy"]),
                      "rx":float(instance["rx"]),
                      "ry":float(instance["ry"]),
                      "angle":float(instance["angle"])} if instance["type"] == "ellipse" else None,
    'cuboid_points':{outer_k: {inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()} for outer_k, outer_v in d['points'].items()}  if instance["type"] == "cuboid" else None,
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


def process_bounding_box(bbox,custom_id_map=None):
    """XYXY class
        keras_cv.bounding_box.XYXY()
        XYXY contains axis indices for the XYXY format.

        All values in the XYXY format should be absolute pixel values.

        The XYXY format consists of the following required indices:

        LEFT: left of the bounding box
        TOP: top of the bounding box
        RIGHT: right of the bounding box
        BOTTOM: bottom of the bounding box"""
    
    object_box = [int(x) for x in [bbox["points"]["x1"],
                                    bbox["points"]["y1"],
                                    bbox["points"]["x2"],
                                    bbox["points"]["y2"]]]
    object_class = bbox["classId"] if custom_id_map is None else custom_id_map.get(bbox["className"])
    return object_box,object_class

def get_boxes(instances,custom_id_map=None):
    boxes = []
    classes = []
    for instance in instances:
        if instance["type"] == "bbox":
            ob,oc = process_bounding_box(instance,custom_id_map)
            boxes.append(ob)
            classes.append(oc)
    return {"classes":classes,"boxes":boxes}


def get_vector_dataframe(annotations,spark,custom_id_map = None):
    print(custom_id_map)
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
            "instances": [process_vector_instance(instance,custom_id_map) for instance in item["instances"]],
            "bounding_boxes":get_boxes(item["instances"],custom_id_map),
            "comments":[process_comment(comment) for comment in item["comments"]]
            }
        rows.append(flattened_item)
    schema = get_vector_schema()
    spark_df = spark.createDataFrame(rows, schema=schema)
    return spark_df