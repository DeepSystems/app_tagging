import os
import json
import html
import time
import csv
from collections import defaultdict
import supervisely_lib as sly

STATE = "state"
DATA = "data"
TEMPLATE = "template"

ITEMS_PATH = "/workdir/src/items.csv"

# state
categories = set()
category_items = defaultdict(list)


def read_items_csv(path):
    global categories, category_items
    items = []
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for idx, row in enumerate(csv_reader):
            if idx % 2 == 0:
                row['images'] = ["https://i.imgur.com/qb32PBI.jpg", "https://i.imgur.com/qb32PBI.jpg"]
            else:
                row['images'] = ["https://i.imgur.com/qH2xfxH.jpg", "https://i.imgur.com/qH2xfxH.jpg", "https://i.imgur.com/qH2xfxH.jpg"]
            items.append(row)
            categories.add(row["category"])
            category_items[row["category"]].append(row)


def main():
    read_items_csv(ITEMS_PATH)

    task_id = int(os.getenv("TASK_ID"))
    api = sly.Api.from_env()
    api.add_additional_field('taskId', task_id)
    api.add_header('x-task-id', str(task_id))

    with open('/workdir/src/gui.html', 'r') as file:
        gui_template = file.read()

    data = {}
    data["categories"] = list(categories)
    data["items"] = category_items

    default_category = data["categories"][0]

    payload = {}
    payload[TEMPLATE] = gui_template
    payload[DATA] = data
    payload[STATE] = {
        "category": default_category,
        "item": 0
    }

    #http://192.168.1.42/apps/2/sessions/75
    #http://192.168.1.42/app/images/1/9/28/35?page=1&sessionId=75#image-31872
    jresp = api.task.set_data(task_id, payload)


if __name__ == "__main__":
    main()
