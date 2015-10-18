from os.path import join

from gi.repository import Gtk

import Config
from TaskTreeElement import TaskTreeElement


class ArchiveWidget (Gtk.ScrolledWindow):

    def __init__(self, rootTask):
        Gtk.ScrolledWindow.__init__(self)

        self.rootTask = rootTask
        self._init_ui()


    def _init_ui(self):
        builder = Gtk.Builder()
        builder.add_from_file(join(Config.DESIGN_DIR, "Archive.glade"))
        self.noTaskLabel = builder.get_object("noTaskLabel")

        self.archiveHolder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.archiveHolder.pack_start(self.flowbox, False, False, 0)
        self.add(self.archiveHolder)

        allTasks = self.rootTask.get_all_archived_subtasks(onlyTop=True)
        for child in allTasks:
            self._add_task(child)
        if not allTasks:
            self.flowbox.add(self.noTaskLabel)

        self.show_all()


    def on_task_archived(self, task):
        if task.parent.archived:
            pass
        elif task.get_all_archived_subtasks():
        # TODO revisit, not everything needs to be updated
            for child in self.flowbox.get_children():
                print(child)
                self.flowbox.remove(child)
            for task in self.rootTask.get_all_archived_subtasks(onlyTop=True):
                self._add_task(task)
        else:
            self._add_task(task)


    # TODO revisit, not everythin needs to be updated
    def on_task_dearchived(self, task):
        for child in self.flowbox.get_children():
            self.flowbox.remove(child)
        for task in self.rootTask.get_all_archived_subtasks(onlyTop=True):
            self._add_task(task)

        if not self.flowbox.get_children():
            self.flowbox.add(self.noTaskLabel)


    def _add_task(self, task):
        labelHolder = self.noTaskLabel.get_parent()
        if labelHolder in self.flowbox.get_children():
            labelHolder.remove(self.noTaskLabel)
            self.flowbox.remove(labelHolder)
        element = TaskTreeElement(task, True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(element, True, True, 0)
        self.flowbox.add(box)
        self.flowbox.show_all()
