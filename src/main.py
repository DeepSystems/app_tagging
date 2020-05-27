import time
_start = time.time()

import os
from urllib.parse import urlsplit

import csv
import supervisely_lib as sly
import supervisely_lib.io.json as sly_json
import utils

PROJECT_ID = 29


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ITEMS_PATH = os.path.join(SCRIPT_DIR, "products.csv")


def read_items_csv(path):
    products = []
    images = []
    keywords = set()
    product_search = []
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for idx, row in enumerate(csv_reader):
            products.append(row)
            keywords.add(row["Category"].lower())
            keywords.add(row["Brand"].lower())
            keywords.add(row["Item"].lower())

            images.append(row["image"])
            row["image"] = '<a href="{}" target="_blank">{}</a>'.format(row["image"], "image")

            sitename = "{0.netloc}".format(urlsplit(row["product_page"]))
            row["product_page"] = '<a href="{}" target="_blank">{}</a>'.format(row["product_page"], sitename)

            product_search.append("{} {} {}".format(row["Category"].lower(),
                                                    row["Brand"].lower(),
                                                    row["Item"].lower()))

    sly.logger.info("items count:", extra={"count": len(products)})
    return products, images, keywords, product_search


def init_project(api: sly.Api, project_id):
    project_dir = os.path.join(sly.app.SHARED_DATA, "app_tagging", str(project_id))

    #@TODO: comment
    sly.fs.remove_dir(project_dir)

    if sly.fs.dir_exists(project_dir):
        return
    else:
        sly.fs.mkdir(project_dir)

    meta_json = api.project.get_meta(project_id)
    meta = sly.ProjectMeta.from_json(meta_json)

    product_id = meta.get_tag_meta("product_id")
    if product_id is None:
        meta = meta.add_tag_meta(sly.TagMeta("product_id", sly.TagValueType.ANY_STRING))

    category = meta.get_tag_meta("category")
    if category is None:
        meta = meta.add_tag_meta(sly.TagMeta("category", sly.TagValueType.ANY_STRING))

    brand = meta.get_tag_meta("brand")
    if brand is None:
        meta = meta.add_tag_meta(sly.TagMeta("brand", sly.TagValueType.ANY_STRING))

    item_name = meta.get_tag_meta("item_name")
    if item_name is None:
        meta = meta.add_tag_meta(sly.TagMeta("item_name", sly.TagValueType.ANY_STRING))

    if product_id is None or category is None or brand is None or item_name is None:
        api.project.update_meta(project_id, meta.to_json())

    sly_json.dump_json_file(meta.to_json(), os.path.join(project_dir, "meta.json"))

    image_label_pairs = []
    for dataset in api.dataset.get_list(project_id):
        images = api.image.get_list(dataset.id)
        image_ids = [image.id for image in images]
        for batch in sly.batched(image_ids):
            annotations = api.annotation.download_batch(dataset.id, batch)
            for ann_info in annotations:
                ann_path = os.path.join(project_dir, str(dataset.id), str(ann_info.image_id) + sly.ANN_EXT)
                sly.fs.ensure_base_path(ann_path)
                sly_json.dump_json_file(ann_info.annotation, ann_path)
                image_ids.append(ann_info.image_id)
                ann = sly.Annotation.from_json(ann_info.annotation, meta)
                label_indices = list(range(0, len(ann.labels)))
                image_label_pairs.extend(
                    list(zip([ann_info.image_id] * len(label_indices),
                             [ann_path] * len(label_indices),
                             label_indices
                            )
                         )
                )

    sly_json.dump_json_file(image_label_pairs, os.path.join(project_dir, "image_labels_pairs.json"))
    sly_json.dump_json_file(list(range(len(image_label_pairs))), os.path.join(project_dir, "free_pairs.json"))
    return project_dir


def main():
    products, images, keywords_set, product_search = read_items_csv(ITEMS_PATH)

    keywords = []
    for item in keywords_set:
        keywords.append({"value": item})

    task_info = sly_json.load_json_file(os.path.join(SCRIPT_DIR, "../task_config.json"))
    task_id = task_info["task_id"]
    server_address = task_info["server_address"]
    api_token = task_info["api_token"]

    api = sly.Api(server_address, api_token, retry_count=10)
    api.add_additional_field('taskId', task_id)
    api.add_header('x-task-id', str(task_id))

    #context = api.task.get_data(task_id, sly.app.CONTEXT)
    #user_id = context["userId"]

    project_dir = init_project(api, PROJECT_ID)

    with open(os.path.join(SCRIPT_DIR, 'gui.html'), 'r') as file:
        gui_template = file.read()

    img_grid = []
    candidates = []
    for img_url, product in zip(images, products):
        img_grid.append({"url": img_url, "label": product["Item"]})
        candidate = [[img_url], [img_url]]
        candidates.append(candidate)

    sly_json.dump_json_file(products, os.path.join(project_dir, "products.json"))
    sly_json.dump_json_file(images, os.path.join(project_dir, "images.json"))
    sly_json.dump_json_file(product_search, os.path.join(project_dir, "product_search.json"))

    #data
    data = {
        "table": products,
        "objectToTag": [["https://i.imgur.com/x1l0qca.jpg"], ["https://i.imgur.com/YbWG8xE.jpg"]],
        "itemExamples": [["https://i.imgur.com/NYv2mml.jpg"], ["https://i.imgur.com/CnzYGbQ.jpg"], ["https://i.imgur.com/Yq4lYa0.jpg"]],
        "imagesGrid": img_grid,
        "gridIndices": list(range(min(30, len(img_grid)))),
        "keywords": keywords,
        "imagesCandidates": candidates,
        "gridData": [{ "date": '2016-05-02', "name": 'Jack', "address": 'New York City' },
                     { "date": '2016-05-04', "name": 'Jack', "address": 'New York City' },
                     { "date": '2016-05-01', "name": 'Jack', "address": 'New York City' },
                     { "date": '2016-05-03', "name": 'Jack', "address": 'New York City' },
                    ],
        "currentLabelIndex": -1

    }

    #state
    state = {
        "projectId": PROJECT_ID,
        "perPage": 20,
        "pageSizes": [10, 15, 20, 50, 100],
        "table": {},
        "selectedImageIndex": 0,
        "selectedKeywords": [],
        "searching": False,
        "tagging": False,
    }

    payload = {
        sly.app.TEMPLATE: gui_template,
        sly.app.STATE: state,
        sly.app.DATA: data,
    }

    #http://192.168.1.42/apps/2/sessions/75
    #http://192.168.1.42/app/images/1/9/28/35?page=1&sessionId=75#image-31872
    jresp = api.task.set_data(task_id, payload)
    utils.get_next_object(api, task_id)


if __name__ == "__main__":
    main()
    sly.logger.info("SCRIPT_TIME: {} sec".format(time.time() - _start))


#@TODO: сделать нормальный warning button
#@TODO: починить галерею - чтобы картинка вписывалась полностью а не только по ширине
#@TODO: починить поиск по таблице
#@TODO: починить выделение строки

#@TODO:
# прогресс аннотации
# сделать лоудинги на кнопку
# поправить верстку грид и табы
# добавить статистику по проаннотированным данным
# починить галерею
# отпрофилировать
# реализовать кнопку unknown
# автообновление фигур в кликере
# настройки: какие теги добавлять, сколько брать окрестность в пикселях
# finish labeling
