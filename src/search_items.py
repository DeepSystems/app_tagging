import os
from fuzzywuzzy import process as fuzzprocess

import supervisely_lib as sly
import supervisely_lib.io.json as sly_json
import utils

task_id, api, project_id = utils.get_task_api()

search_keywords = api.task.get_data(task_id, "state.selectedKeywords")
search_query = ' '.join(search_keywords)

project_dir = os.path.join(sly.app.SHARED_DATA, "app_tagging", str(project_id))
product_search = sly_json.load_json_file(os.path.join(project_dir, "product_search.json"))

choices_dict = {idx: el for idx, el in enumerate(product_search)}
results = fuzzprocess.extract(search_query, choices_dict, limit=max(30, len(product_search)))

gridIndices = []
for result in results:
    gridIndices.append(result[2])

api.task.set_data(task_id, gridIndices, "data.gridIndices")
api.task.set_data(task_id, {"selectedImageIndex": results[0][2], "searching": False}, sly.app.STATE, append=True)


