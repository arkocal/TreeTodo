import os
import uuid
from datetime import datetime

from gi.repository import GObject



class TaskUpdateType(GObject.GObject):
    TITLE = 0
    DESCRIPTION = 1
    COLOR = 2
    DATE = 3
    DONE = 4
    NEW = 5
    SUBTASK_ADDED = 6
    DELETED = 7
    ARCHIVED = 8
    DEARCHIVED = 9
    SUBTASK_DEARCHIVED = 10



class Task(GObject.GObject):

    __gsignals__ = {
        'updated': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        'activated': (GObject.SIGNAL_RUN_FIRST, None, ())}


    def __init__(self, arg):
        GObject.GObject.__init__(self)
        if type(arg) == tuple:
            self.new_from_tuple(arg)
        elif type(arg) == str:
            self.new_from_title(arg)


    def new_from_title(self, title):
        self.title = title
        self.description = ""
        self.color = "#FFFFFF"
        self.date = None
        self.done = False
        self.archived = False

        """List of subtasks"""
        self.subtasks = []
        """Subtasks of task that are archived"""
        self.archivedSubtasks = []
        """Parent task, use parent.add_child to reparent"""

        self.parent = None
        """How many levels of parents exist"""
        self.depth = 0

        """Task UUID"""
        self.uuid = str(uuid.uuid1())


    def new_from_tuple(self, t):
        (uuid, title, description, color,
         unixdate, done, parentUUID, archived) = t
        self.title = title
        self.description = description
        self.color = color
        try:
            date = datetime.fromtimestamp(unixdate)
            self.date = (date.year, date.month, date.day)
        except ValueError:  # Invalid / No date
            self.date = None
        self.done = bool(done)
        self.archived = bool(archived)

        self.subtasks = []
        self.archivedSubtasks = []

        self.parent = None
        self.depth = 0
        self.uuid = uuid

    def set_title(self, title):
        if title:
            self.title = title
            self.emit("updated", TaskUpdateType.TITLE)


    def set_description(self, description):
        if description:
            self.description = description
            self.emit("updated", TaskUpdateType.DESCRIPTION)


    def set_color(self, color):
        if color:
            self.color = color
            self.emit("updated", TaskUpdateType.COLOR)


    def set_date(self, date):
        oldDate = self.date

        if date != oldDate:
            self.date = date
            self.emit("updated", TaskUpdateType.DATE)


    def set_done(self, done):
        self.done = done
        self.update_done()

        self.emit("updated", TaskUpdateType.DONE)


    def update_done(self):
        """Update if task is completed

        A task with no subtasks can be done or not depending on user
        input. A task with subtasks is done, if all of its subtasks are.
        """
        wasDone = self.done

        if self.subtasks:
            self.done = True
            for subtask in self.subtasks:
                self.done = self.done and subtask.done

        if (not self.subtasks) or wasDone != self.done:
            self.emit("updated", TaskUpdateType.DONE)
            if self.parent:
                self.parent.update_done()


    def add_subtask(self, subtask):
        self.subtasks.append(subtask)
        subtask.parent = self
        subtask.depth = self.depth + 1
        self.emit("updated", TaskUpdateType.SUBTASK_ADDED)
        subtask.emit("updated", TaskUpdateType.NEW)
        self.update_done()


    def delete(self):
        if self.parent:
            self.parent.remove_subtask(self)
        else:
            self.emit("updated", TaskUpdateType.DELETED)



    def remove_subtask(self, subtask):
        if subtask in self.subtasks:
            self.subtasks.remove(subtask)
        elif subtask in self.archivedSubtasks:
            self.archivedSubtasks.remove(subtask)
        else:
            raise ValueError()
        for toDelete in subtask.get_all_subtasks():
            toDelete.emit("updated", TaskUpdateType.DELETED)
        self.update_done()


    def archive(self):
        if self.parent:
            self.parent.archive_subtask(self)
            self.archived = True
            self.emit("updated", TaskUpdateType.ARCHIVED)


    def archive_subtask(self, subtask):
        self.subtasks.remove(subtask)
        self.archivedSubtasks.append(subtask)
        self.update_done()


    def dearchive(self):
        if self.parent:
            self.parent.dearchive_subtask(self)
            self.archived = False
            self.emit("updated", TaskUpdateType.DEARCHIVED)


    def dearchive_subtask(self, subtask):
        self.archivedSubtasks.remove(subtask)
        self.subtasks.append(subtask)
        self.emit("updated", TaskUpdateType.SUBTASK_DEARCHIVED)
        self.update_done()


    def get_all_subtasks(self):
        """Return a list of self and children and their children and so on"""
        allSubtasks = [self]
        for subtask in self.subtasks:
            allSubtasks += subtask.get_all_subtasks()
        return allSubtasks


    def get_all_archived_subtasks(self, onlyTop=False):
        """Gets all children in tree that are in the archive.

        Params:
            onlyTop: only get children their parents are not archived

        """
        if onlyTop and self.archived:
            return [self]
        result = self.archivedSubtasks[:]
        if self.archived:
            result.append(self)
        for child in self.subtasks:
            result += [c for c in child.get_all_archived_subtasks(onlyTop)
                       if c not in result]
        if not onlyTop:
            for child in self.archivedSubtasks:
                result += [c for c in child.get_all_archived_subtasks(onlyTop)
                           if c not in result]
        return result

    def is_real_task(self):
        """ Return if task is real or a placeholder like rootTask"""
        return self.uuid != "00000000-0000-0000-0000-000000000000"
