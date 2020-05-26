import os
import json
import html
import time
from urllib.parse import urlsplit

import csv
import supervisely_lib as sly
import utils

ITEMS_PATH = "/workdir/src/products.csv"

DEMO_IMAGES = []


def read_items_csv(path):
    products = []
    images = []
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for idx, row in enumerate(csv_reader):
            products.append(row)
            images.append(row["image"])
            row["image"] = '<a href="{}" target="_blank">{}</a>'.format(row["image"], "image")

            sitename = "{0.netloc}".format(urlsplit(row["product_page"]))
            row["product_page"] = '<a href="{}" target="_blank">{}</a>'.format(row["product_page"], sitename)

    #@TODO: table freezes page (110k)
    products = products[:100]
    sly.logger.info("items count:", extra={"count": len(products)})

    return products, images


def main():
    products, images = read_items_csv(ITEMS_PATH)

    task_id = int(os.getenv("TASK_ID"))
    api = sly.Api.from_env()
    api.add_additional_field('taskId', task_id)
    api.add_header('x-task-id', str(task_id))

    #context = api.task.get_data(task_id, sly.app.CONTEXT)
    #user_id = context["userId"]

    project_id = 28 # get from context menu somehow
    #session_path = "/shared_data/app_tagging/{}".format(project_id)

    #utils.init_project(api, project_id, session_path)


    with open('/workdir/src/gui.html', 'r') as file:
        gui_template = file.read()

    # images = ["https://i.imgur.com/x1l0qca.jpg", "https://i.imgur.com/YbWG8xE.jpg",
    #           "https://i.imgur.com/NYv2mml.jpg", "https://i.imgur.com/CnzYGbQ.jpg",
    #           "https://i.imgur.com/NYv2mml.jpg", "https://i.imgur.com/CnzYGbQ.jpg",
    #           "https://i.imgur.com/x1l0qca.jpg", "https://i.imgur.com/YbWG8xE.jpg",
    #           "https://i.imgur.com/x1l0qca.jpg", "https://i.imgur.com/YbWG8xE.jpg",
    #           "https://i.imgur.com/x1l0qca.jpg", "https://i.imgur.com/YbWG8xE.jpg",
    #           "https://i.imgur.com/NYv2mml.jpg", "https://i.imgur.com/CnzYGbQ.jpg",
    #           "https://i.imgur.com/NYv2mml.jpg", "https://i.imgur.com/CnzYGbQ.jpg",
    #           "https://i.imgur.com/x1l0qca.jpg", "https://i.imgur.com/YbWG8xE.jpg",
    #           "https://i.imgur.com/x1l0qca.jpg", "https://i.imgur.com/YbWG8xE.jpg",
    #           "https://i.imgur.com/x1l0qca.jpg", "https://i.imgur.com/YbWG8xE.jpg",
    #           "https://i.imgur.com/NYv2mml.jpg", "https://i.imgur.com/CnzYGbQ.jpg",
    #           "https://i.imgur.com/NYv2mml.jpg", "https://i.imgur.com/CnzYGbQ.jpg",
    #           "https://i.imgur.com/Yq4lYa0.jpg"]


    img_grid = []
    candidates = []
    for img_url in images:
        img_grid.append({"url": img_url, "label": sly.rand_str(65)})
        candidate = [[img_url], [img_url]]
        candidates.append(candidate)


    keywords = []
    words = ["Alabama", "Alaska", "Arizona",
        "Arkansas", "California", "Colorado",
        "Connecticut", "Delaware", "Florida",
        "Georgia", "Hawaii", "Idaho", "Illinois",
        "Indiana", "Iowa", "Kansas", "Kentucky",
        "Louisiana", "Maine", "Maryland",
        "Massachusetts", "Michigan", "Minnesota",
        "Mississippi", "Missouri", "Montana",
        "Nebraska", "Nevada", "New Hampshire",
        "New Jersey", "New Mexico", "New York",
        "North Carolina", "North Dakota", "Ohio",
        "Oklahoma", "Oregon", "Pennsylvania",
        "Rhode Island", "South Carolina",
        "South Dakota", "Tennessee", "Texas",
        "Utah", "Vermont", "Virginia",
        "Washington", "West Virginia", "Wisconsin",
        "Wyoming"]
    for word in words:
        keywords.append({"value": word})#{"value": word, "label": word, "key": word})


    #data
    data = {
        "table": products,
        "objectToTag": [["https://i.imgur.com/x1l0qca.jpg"], ["https://i.imgur.com/YbWG8xE.jpg"]],
        "itemExamples": [["https://i.imgur.com/NYv2mml.jpg"], ["https://i.imgur.com/CnzYGbQ.jpg"], ["https://i.imgur.com/Yq4lYa0.jpg"]],
        "imagesGrid": img_grid,
        "keywords": keywords,
        "imagesCandidates": candidates,
        "gridData": [{ "date": '2016-05-02', "name": 'Jack', "address": 'New York City' },
                     { "date": '2016-05-04', "name": 'Jack', "address": 'New York City' },
                     { "date": '2016-05-01', "name": 'Jack', "address": 'New York City' },
                     { "date": '2016-05-03', "name": 'Jack', "address": 'New York City' },
                    ]
    }

    #state
    state = {
        "projectId": project_id,
        "perPage": 20,
        "pageSizes": [10, 15, 20, 50, 100],
        "table": {},
        "selectedImageIndex": 0,
        "selectedKeywords": []

    }

    payload = {
        sly.app.TEMPLATE: gui_template,
        sly.app.STATE: state,
        sly.app.DATA: data,
    }

    #http://192.168.1.42/apps/2/sessions/75
    #http://192.168.1.42/app/images/1/9/28/35?page=1&sessionId=75#image-31872
    jresp = api.task.set_data(task_id, payload)


if __name__ == "__main__":
    main()
