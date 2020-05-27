import os
import supervisely_lib as sly
import supervisely_lib.io.json as sly_json
import utils


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
task_info = sly_json.load_json_file(os.path.join(SCRIPT_DIR, "../task_config.json"))
task_id = task_info["task_id"]
server_address = task_info["server_address"]
api_token = task_info["api_token"]
api = sly.Api(server_address, api_token, retry_count=10)
api.add_additional_field('taskId', task_id)
api.add_header('x-task-id', str(task_id))

project_id = api.task.get_data(task_id, "state.projectId")
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

labels = ann.labels
new_label = labels[label_index].add_tags([
    sly.Tag(product_id_tm, "unknown"),
])


free_pairs.pop(0)
sly_json.dump_json_file(free_pairs, os.path.join(project_dir, "free_pairs.json"))

utils.get_next_object(api, task_id)

api.task.set_data(task_id, False, "state.tagging")