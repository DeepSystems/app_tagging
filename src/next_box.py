import os
import supervisely_lib as sly


task_id = int(os.getenv("TASK_ID"))
api = sly.Api.from_env()
api.add_additional_field('taskId', task_id)
api.add_header('x-task-id', str(task_id))

state = api.task.get_data(task_id, field=const.STATE)

project_id = state["projectId"]
