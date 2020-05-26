import os
from fuzzywuzzy import process as fuzzprocess

import supervisely_lib as sly
import supervisely_lib.io.json as sly_json

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

task_info = sly_json.load_json_file(os.path.join(SCRIPT_DIR, "../task_config.json"))
task_id = task_info["task_id"]
server_address = task_info["server_address"]
api_token = task_info["api_token"]
api = sly.Api(server_address, api_token, retry_count=10)
api.add_additional_field('taskId', task_id)
api.add_header('x-task-id', str(task_id))


search_keywords = api.task.get_data(task_id, "state.selectedKeywords")
search_query = ' '.join(search_keywords)

project_id = api.task.get_data(task_id, "state.projectId")
project_dir = os.path.join(sly.app.SHARED_DATA, "app_tagging", str(project_id))
product_search = sly_json.load_json_file(os.path.join(project_dir, "product_search.json"))

choices_dict = {idx: el for idx, el in enumerate(product_search)}
results = fuzzprocess.extract(search_query, choices_dict, limit=12)

gridIndices = []
for result in results:
    gridIndices.append(result[2])

api.task.set_data(task_id, gridIndices, "data.gridIndices")


