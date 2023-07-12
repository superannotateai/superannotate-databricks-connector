from superannotate_databricks_connector.schemas.vector_schema import (
    get_vector_schema
)


def process_comment(comment):
    comment["x"] = float(comment.get("x"))
    comment["y"] = float(comment.get("y"))
    return comment


def process_vector_object(instance, custom_id_map=None):
    """
    Takes one annotation instance of an object and unpacks it.

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
        'bbox': {k: float(v) for k, v in instance['points'].items()}
        if instance["type"] == "bbox" else None,
        'rbbox': {k: float(v) for k, v in instance['points'].items()}
        if instance["type"] == "rbbox" else None,
        'polygon': {"points": [float(p) for p in instance['points']]
                    if instance["type"] == "polygon" else None,
                    'exclude': instance.get("exclude")}
        if instance["type"] == "polygon" else None,
        'point': {"x": float(instance.get("x")),
                  "y": float(instance.get("y"))
                  } if instance["type"] == "point" else None,
        'ellipse': {"cx": float(instance["cx"]),
                    "cy": float(instance["cy"]),
                    "rx": float(instance["rx"]),
                    "ry": float(instance["ry"]),
                    "angle": float(instance["angle"])}
        if instance["type"] == "ellipse" else None,
        'cuboid': {outer_k: {inner_k: float(inner_v)
                             for inner_k, inner_v in outer_v.items()}
                   for outer_k, outer_v in instance['points'].items()}
        if instance["type"] == "cuboid" else None,
        "polyline": [float(p) for p in instance['points']]
        if instance["type"] == "polyline" else None,
        'groupId': instance.get('groupId'),
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


def process_vector_tag(instance, custom_id_map=None):
    """
    Takes one annotation instance of a tag and unpacks it.

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
        'attributes': instance['attributes'],
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

    object_box = [int(round(x)) for x in [bbox["points"]["x1"],
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
            "instances": [process_vector_object(instance, custom_id_map)
                          for instance in item["instances"]
                          if instance["type"] != "tag"],
            "bounding_boxes": get_boxes(item["instances"], custom_id_map),
            "tags": [process_vector_tag(instance, custom_id_map)
                     for instance in item["instances"]
                     if instance["type"] == "tag"],
            "comments": [process_comment(comment)
                         for comment in item["comments"]]
        }

        rows.append(flattened_item)
    schema = get_vector_schema()

    spark_df = spark.createDataFrame(rows, schema=schema)
    return spark_df


def process_attribute(attribute):
    return {"groupName": attribute["groupName"],
            "name": attribute["name"]}


def create_instance_dict(item):
    """Funciton that unpacks a dataframe row converted into a dict
    and transformes it to a superannotate annotaiton dictionary

    Arg:
        item (dict): dictionary with a instance in the superannotate-databricks
                     format
    Returns:
        dict processed into superannotate json format
    """
    item_dict = {
        "type": item["instance_type"],
        "classId": int(item["classId"]),
        "probability": item["probability"],
        "groupId": int(item["groupId"]),
        # "pointLabels": item.get("pointLabels", None), # uncomment if needed
        "locked": item["locked"],
        "trackingId": item["trackingId"],
        "attributes": [process_attribute(att) for att in item["attributes"]],
        "error": item["error"],
        "createdAt": item["createdAt"],
        "createdBy": item["createdBy"],
        "creationType": item["creationType"],
        "updatedAt": item["updatedAt"],
        "updatedBy": item["updatedBy"],
        "className": item["className"]
    }

    instance_type = item["instance_type"]
    if instance_type in ["bbox", "rbbox"]:
        item_dict["points"] = item[instance_type].asDict()
    elif instance_type == "cuboid":
        item_dict["points"] = {k: v.asDict()
                               for k, v in item["cuboid"].asDict().items()}
    elif instance_type == "polygon":
        item_dict["points"] = item["polygon"].asDict()["points"]
        item_dict["exclude"] = item["polygon"].asDict()["exclude"]
    elif instance_type == "point":
        item_dict["x"] = item["point"].asDict()["x"]
        item_dict["y"] = item["point"].asDict()["y"]
    elif instance_type == "ellipse":
        ellipse = item["ellipse"].asDict()
        item_dict["cx"] = ellipse["cx"]
        item_dict["cy"] = ellipse["cy"]
        item_dict["rx"] = ellipse["rx"]
        item_dict["ry"] = ellipse["ry"]
        item_dict["angle"] = ellipse["angle"]
    elif instance_type == "polyline":
        item_dict["points"] = item["polyline"]
    return item_dict


def create_tag_dict(item):
    """Funciton that unpacks a dataframe row converted into a dict
    and transformes it to a superannotate annotaiton dictionary

    Arg:
        item (dict): dictionary with a tag in the superannotate-databricks
                     format
    Returns:
        dict processed into superannotate json format
    """
    item_dict = {
        "type": item["instance_type"],
        "classId": item["classId"],
        "probability": item["probability"],
        "attributes": [process_attribute(att) for att in item["attributes"]],
        "createdAt": item["createdAt"],
        "createdBy": item["createdBy"],
        "creationType": item["creationType"],
        "updatedAt": item["updatedAt"],
        "updatedBy": item["updatedBy"],
        "className": item["className"]
    }
    return item_dict


def unpack_vector_row(row):
    """Funciton that unpacks a dataframe row into a
       superannotate json ready to be uploaded

    Arg:
        row (spark.sql.Row): row from superannotate formated dataframe
    Returns:
        dict processed into superannotate json format
    """
    metadata = {"height": row["image_height"],
                "width": row["image_width"],
                "name": row["image_name"],
                "projectId": row["projectId"],
                "isPredicted": row["isPredicted"],
                "status": row["status"],
                "pinned": row["pinned"],
                "annotatorEmail": row["annotatorEmail"],
                "qaEmail": row["qaEmail"]}
    instances = []
    for instance in row["instances"]:
        instances.append(create_instance_dict(instance.asDict()))
    for tag in row["tags"]:
        instances.append(create_tag_dict(tag.asDict()))
    comments = []
    for comment in row["comments"]:
        comments.append(comment.asDict())
    return {"metadata": metadata,
            "instances": instances,
            "comments": comments}
