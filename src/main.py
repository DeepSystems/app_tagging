import os
import json
import html
import time

import csv
from collections import defaultdict
import supervisely_lib as sly
import utils

ITEMS_PATH = "/workdir/src/items.csv"

DEMO_IMAGES = []


#examples http://www.grocery.com/open-grocery-database-project/
def read_items_csv(path):
    products = []
    images = []
    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for idx, row in enumerate(csv_reader):
            products.append(row)
    #@TODO: table freezes page (110k)
    products = products[:1000]
    sly.logger.info("items count:", extra={"count": len(products)})

    return products


def main():
    products = []#read_items_csv(ITEMS_PATH)

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

    #data
    data = {
        "table": products,
        "productExamples": []
    }


    #state
    state = {
        "projectId": project_id,
        "perPage": 20,
        "pageSizes": [10, 15, 20, 50, 100],
        "table": {},
    }



    # data = {}
    # data["categories"] = list(categories)
    # data["items"] = category_items
    #
    # #default_category = data["categories"][0]

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
