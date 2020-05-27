import os
import supervisely_lib as sly
import supervisely_lib.io.json as sly_json
import time


def get_task_api():
    PROJECT_ID = 29
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    task_info = sly_json.load_json_file(os.path.join(SCRIPT_DIR, "../task_config.json"))
    task_id = task_info["task_id"]
    server_address = task_info["server_address"]
    api_token = task_info["api_token"]
    api = sly.Api(server_address, api_token, retry_count=10)
    api.add_additional_field('taskId', task_id)
    api.add_header('x-task-id', str(task_id))
    # context = api.task.get_data(task_id, sly.app.CONTEXT)
    # user_id = context["userId"]
    return task_id, api, PROJECT_ID

@sly.ptimer
def pack_images(cropped_image, cropped_context):
    cropped_url = sly.image.np_image_to_data_url(cropped_image)
    cropped_context_url = sly.image.np_image_to_data_url(cropped_context)
    return cropped_url, cropped_context_url

@sly.ptimer
def get_next_object(api, task_id, project_id):
    project_dir = os.path.join(sly.app.SHARED_DATA, "app_tagging", str(project_id))

    image_labels = sly_json.load_json_file(os.path.join(project_dir, "image_labels_pairs.json"))
    free_pairs = sly_json.load_json_file(os.path.join(project_dir, "free_pairs.json"))

    if len(free_pairs) == 0:
        # @TODO: show message to user
        sly.logger.info("labeling finished")

    item = image_labels[free_pairs[0]]

    image_id = item[0]
    ann_path = item[1]
    label_index = item[2]

    image_path = os.path.join(project_dir, "images", "{}.png".format(image_id))
    if not sly.fs.file_exists(image_path):
        api.image.download_path(image_id, image_path)

    image = sly.image.read(image_path)

    meta_json = sly_json.load_json_file(os.path.join(project_dir, "meta.json"))
    meta = sly.ProjectMeta.from_json(meta_json)

    ann_json = sly_json.load_json_file(ann_path)
    ann = sly.Annotation.from_json(ann_json, meta)

    label = ann.labels[label_index]

    rect = label.geometry.to_bbox()
    cropped_image = sly.image.crop(image, label.geometry.to_bbox())

    canvas = image.copy()

    label.draw_contour(canvas, thickness=3)

    pad = 150
    rect_context = sly.Rectangle(
        max(0, rect.top - pad),
        max(0, rect.left - pad),
        min(image.shape[0]-1, rect.bottom + pad),
        min(image.shape[1]-1, rect.right + pad)
    )

    cropped_context = sly.image.crop(canvas, rect_context)
    cropped_url, cropped_context_url = pack_images(cropped_image, cropped_context)

    api.task.set_data(task_id, [[cropped_url], [cropped_context_url]], "data.objectToTag")
