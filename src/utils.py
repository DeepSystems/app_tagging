import pickle
import os
import supervisely_lib as sly
import pickle


def write_file():
    pass


def init_project(api: sly.Api, project_id, path):
    path_for_project = os.path.join(path, str(project_id))

    #@TODO: uncomment
    #if sly.fs.dir_exists(path_for_project):
    #    return

    sly.fs.mkdir(path_for_project)

    # meta_json = api.project.get_meta(project_id)
    # meta = sly.ProjectMeta.from_json(meta_json)

    all_images = []
    for dataset in api.dataset.get_list(project_id):
        for image in api.image.get_list(dataset.id):
            all_images.append(image.id)

    in_progress_images = {}
    finished_images = {}

    pickle.dump(all_images, open(os.path.join(path, "all_images.p"), "wb"))
    pickle.dump(in_progress_images, open(os.path.join(path, "in_progress_images.p"), "wb"))
    pickle.dump(in_progress_images, open(os.path.join(path, "finished_images.p"), "wb"))


    # total_boxes = 0
    # img_ann = {}
    # for image in all_images:
    #     ann_json = api.annotation.download(image.id).annotation
    #     ann = sly.Annotation.from_json(ann_json, meta)
    #     total_boxes += len(ann.labels)
    #     img_ann[image.id] = ann





