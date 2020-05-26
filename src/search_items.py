import os
from fuzzywuzzy import fuzz
from fuzzywuzzy import process as fuzzprocess
import pandas as pd
import numpy as np

import supervisely_lib as sly
import supervisely_lib.io.json as sly_json

task_id = int(os.getenv("TASK_ID"))
api = sly.Api.from_env()
api.add_additional_field('taskId', task_id)
api.add_header('x-task-id', str(task_id))


search_keywords = api.task.get_data(task_id, "state.selectedKeywords")
search_query = ' '.join(search_keywords)

project_id = api.task.get_data(task_id, "state.projectId")
project_dir = os.path.join(sly.app.SHARED_DATA, "app_tagging", str(project_id))

product_search = sly_json.load_json_file(os.path.join(project_dir, "product_search.json"))
choices_dict = {idx: el for idx, el in enumerate(product_search)}
results = fuzzprocess.extract(search_query, choices_dict, limit=10)

gridIndices = []
for result in results:
    gridIndices.append(result[2])

api.task.set_data(task_id, gridIndices, "data.gridIndices")


