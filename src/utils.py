import pickle
import os
import supervisely_lib as sly
import pickle
import supervisely_lib.io.json as sly_json

def write_file():
    pass


def get_next_object(api, task_id):
    project_id = api.task.get_data(task_id, "state.projectId")
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
    rect_context = sly.Rectangle(
        max(0, rect.top - 50),
        max(0, rect.left - 50),
        min(image.shape[0]-1, rect.bottom + 50),
        min(image.shape[1]-1, rect.right + 50)
    )

    cropped_context = sly.image.crop(canvas, rect_context)

    cropped_url = sly.image.np_image_to_data_url(cropped_image)
    cropped_context = sly.image.np_image_to_data_url(cropped_context)

    api.task.set_data(task_id, [[cropped_url], [cropped_context]], "data.objectToTag")
