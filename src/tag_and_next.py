import time
_start = time.time()

import os
import supervisely_lib as sly
import supervisely_lib.io.json as sly_json
import utils

task_id, api, project_id = utils.get_task_api()

#tag here
project_dir = os.path.join(sly.app.SHARED_DATA, "app_tagging", str(project_id))
image_labels = sly_json.load_json_file(os.path.join(project_dir, "image_labels_pairs.json"))
free_pairs = sly_json.load_json_file(os.path.join(project_dir, "free_pairs.json"))

if len(free_pairs) == 0:
    sly.logger.info("labeling finished")
    exit(0)

item = image_labels[free_pairs[0]]
image_id = item[0]
ann_path = item[1]
label_index = item[2]

meta_json = sly_json.load_json_file(os.path.join(project_dir, "meta.json"))
meta = sly.ProjectMeta.from_json(meta_json)

ann_json = sly_json.load_json_file(ann_path)
ann = sly.Annotation.from_json(ann_json, meta)

product_id_tm = meta.get_tag_meta("product_id")
category_tm = meta.get_tag_meta("category")
brand_tm = meta.get_tag_meta("brand")
item_name_tm = meta.get_tag_meta("item_name")

selectedImageIndex = api.task.get_data(task_id, "state.selectedImageIndex")
product = sly_json.load_json_file(os.path.join(project_dir, "products.json"))[selectedImageIndex]
print(product)

labels = ann.labels
new_label = labels[label_index].add_tags([
    sly.Tag(product_id_tm, product["Id"]),
    sly.Tag(category_tm, product["Category"]),
    sly.Tag(brand_tm, product["Brand"]),
    sly.Tag(item_name_tm, product["Item"]),
])

labels[label_index] = new_label
ann = ann.clone(labels=labels)

api.annotation.upload_ann(image_id, ann)
sly_json.dump_json_file(ann.to_json(), ann_path)

free_pairs.pop(0)
sly_json.dump_json_file(free_pairs, os.path.join(project_dir, "free_pairs.json"))

utils.get_next_object(api, task_id, project_id)
api.task.set_data(task_id, False, "state.tagging")
sly.logger.info("SCRIPT_TIME {}: {} sec".format(os.path.basename(__file__), time.time() - _start))
