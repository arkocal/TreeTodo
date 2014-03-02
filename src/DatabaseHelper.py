from datetime import datetime
import os

import sqlite3 as sql

import Task

# TODO find a proper solution for this
INVALID_DATETIME = -100000000000


class TaskDatabaseHelper(object):

    """A helper class to connect to tasks database

    This class provides method for creating task database, making
    changes and logging them.

    Database Structure
    ==================
    tasks
    -----
    UUID (str)
    title (str)
    description (str)
    color (str)
    date (int as UNIX Time)
    done (int)
    parentUUID (str / 00000000-0000-0000-0000-000000000000 for none)
    archived (int)

    log (Not Implemented in 0.1)
    ---
    UUID (str)
    property (str) [name of changed column in DB]
    date (int as UNIX Time)
    """

    def __init__(self, pathToDb):
        """Initialize DatabaseHelper

        This method connects to database at pathToDb or creates a
        database if this fails.

        Return:
            if connection is made

        """
        # Try to connect to database
        if os.path.isfile(pathToDb):
            try:
                self.connection = sql.connect(pathToDb)
                self.cursor = self.connection.cursor()
            except sql.Error:
                return False
        # Create the database if file does not exist
        else:
            self._create_database(pathToDb)


    def get_root_task(self):
        """Return a tree of tasks

        Read all tasks from a database creating the hierarchy and add
        tasks with no parents to a rootTask.

        """
        # Create root task
        rootTask = Task.Task("Roottask")
        # Get all tasks
        self.cursor.execute("SELECT * FROM Tasks;")
        # Create hierarchy
        tasks = []
        for t in self.cursor.fetchall():
            # Add parent UUID to tuple as it is not stored in task
            tasks.append((t[6], Task.from_tuple(t)))

        for (parentUUID, t) in tasks:
            parents = [p for (_, p) in tasks if parentUUID == p.uuid]
            if parents:
                if t.archived:
                    parents[0].archivedSubtasks.append(t)
                    t.parent = parents[0]
                else:
                    parents[0].subtasks.append(t)
                    t.parent = parents[0]

            else:
                if t.archived:
                    rootTask.archivedSubtasks.append(t)
                    t.parent = rootTask
                else:
                    rootTask.subtasks.append(t)
                    t.parent = rootTask

        return rootTask


    def save_task(self, task):
        """Save task and change log

        Change log will be created by this method by comparing
        given task and the task saved on disk.

        """
        if self._is_task_in_database(task):
            self._update_entry(task)
        else:
            self._save_new_entry(task)


    def delete_task(self, task):
        """Delete task and save change log"""
        uuidStr = str(task.uuid)
        self.cursor.execute("DELETE FROM Tasks"
                            " WHERE UUID='{}'".format(uuidStr))
        self.connection.commit()


    def _create_database(self, pathToDb):
        # Return False if fails
        try:
            pathToDbDir = os.path.split(pathToDb)[0]
            if not os.path.isdir(pathToDbDir):
                os.mkdir(pathToDbDir)
            self.connection = sql.connect(pathToDb)
            self.cursor = self.connection.cursor()
            self.cursor.execute("CREATE TABLE Tasks(UUID TEXT, Title TEXT,"
                                "Description TEXT, Color TEXT, Date INT,"
                                "Done INT, ParentUUID TEXT, Archived INT )")
            self.connection.commit()
            return True
        except sql.Error:
            return False


    def _save_new_entry(self, task):
        self.cursor.execute("INSERT INTO Tasks VALUES ('{}', '{}', '{}', '{}',"
                            "{}, {}, '{}', {})".format(
                                *self._task_to_tuple(task)))
        self.connection.commit()


    def _update_entry(self, task):
        uuidStr = str(task.uuid)
        command = ("UPDATE Tasks SET UUID='{}', Title='{}', Description='{}', "
                   "Color='{}', Date={}, Done={}, ParentUUID='{}', "
                   "Archived={} WHERE UUID='{}';").format(
            *(self._task_to_tuple(task) + (uuidStr,)))
        self.cursor.execute(command)
        self.connection.commit()


    def _task_to_tuple(self, task):
        """Create a tuple from task as it will be saved in the DB"""
        if task.parent:
            parentUUID = str(task.parent.uuid)
        else:
            parentUUID = "00000000-0000-0000-0000-000000000000"
        if task.date:
            unixdate = datetime(*task.date).timestamp()
        else:
            unixdate = INVALID_DATETIME
        done = int(task.done)
        archived = int(task.archived)
        return (str(task.uuid), task.title.replace("'", "''"),
                task.description.replace("'", "''"), task.color,
                unixdate, done, parentUUID, archived)


    def _is_task_in_database(self, task):
        """Return if task is saved in DB"""
        uuidStr = str(task.uuid)
        self.cursor.execute("SELECT * FROM Tasks"
                            " WHERE UUID='{}'".format(uuidStr))
        return bool(self.cursor.fetchall())
