import os
import supervisely_lib as sly
import constants as const
from random import randint

task_id = int(os.getenv("TASK_ID"))
print(task_id)
api = sly.Api.from_env()
api.add_additional_field('taskId', task_id)
api.add_header('x-task-id', str(task_id))

state = api.task.get_data(task_id, field=const.STATE)

selected_product = state["table"].get("selectedRowData", None)

# read urls from file of from task_id.data
urls_db = [["https://i.imgur.com/x1l0qca.jpg"],
           ["https://i.imgur.com/YbWG8xE.jpg"],
           ["https://i.imgur.com/NYv2mml.jpg"],
           ["https://i.imgur.com/CnzYGbQ.jpg"],
           ["https://i.imgur.com/Yq4lYa0.jpg"]]

urls = []
cnt_images = randint(0, 5)
for i in range(cnt_images):
    urls.append(urls_db[randint(0, len(urls_db) - 1)])

api.task.set_data(task_id, payload=urls, field="data.productExamples")

print(selected_product)