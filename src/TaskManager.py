from gi.repository import GObject

import Config
import DatabaseHelper
from Task import TaskUpdateType



class TaskManager(GObject.GObject):

    def __init__(self):

        GObject.GObject.__init__(self)

        self._dbHelper = DatabaseHelper.TaskDatabaseHelper(Config.DB_PATH)

        self.rootTask = self._dbHelper.get_root_task()
        for task in (self.rootTask.get_all_subtasks() +
                     self.rootTask.get_all_archived_subtasks()):
            task.connect("updated", self.on_task_updated)


    def on_task_updated(self, task, updateType):
        if updateType in [TaskUpdateType.TITLE,
                          TaskUpdateType.DESCRIPTION,
                          TaskUpdateType.COLOR,
                          TaskUpdateType.DATE,
                          TaskUpdateType.DONE,
                          TaskUpdateType.NEW,
                          TaskUpdateType.ARCHIVED,
                          TaskUpdateType.DEARCHIVED]:
            if task.parent:  # Root task should not be saved
                self._dbHelper.save_task(task)

        elif updateType == TaskUpdateType.SUBTASK_ADDED:
            for subtask in task.subtasks:
                subtask.connect("updated", self.on_task_updated)

        elif updateType == TaskUpdateType.DELETED:
            self._dbHelper.delete_task(task)
