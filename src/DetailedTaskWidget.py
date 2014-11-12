from os.path import join

from gi.repository import Gtk

import Config
from Task import TaskUpdateType

import Dialogs


class DetailedTaskWidget(Gtk.Box):

    def __init__(self, task):
        self.task = task
        self.task.connect("updated", self.on_task_updated)

        Gtk.Box.__init__(self)
        self._init_ui()
        self._connect_signals()


    def set_task(self, task):
        self.task = task
        self.task.connect("updated", self.on_task_updated)
        self.titleLabel.set_text(self.task.title)
        self.descriptionLabel.set_text(self.task.description)

        if self.task.date:
            self._update_date()
        elif self.dateLabel in self.dateLabelHolder.get_children():
            self.dateLabelHolder.remove(self.dateLabel)
        self._update_archive_icon()


    def on_task_updated(self, task, updateType):
        if task != self.task:
            return

        if updateType == TaskUpdateType.TITLE:
            self.titleLabel.set_text(task.title)

        elif updateType == TaskUpdateType.DESCRIPTION:
            self.descriptionLabel.set_text(task.description)

        elif updateType == TaskUpdateType.DATE:
            self._update_date()

        elif updateType in [TaskUpdateType.ARCHIVED,
                            TaskUpdateType.DEARCHIVED]:
            self._update_archive_icon()

        elif updateType == TaskUpdateType.DELETED:
            self._select_none()


    def _update_date(self):
        """Update task date in UI"""
        date = self.task.date
        if date:
            dateStr = "{}/{}/{}".format(date[2], date[1], date[0])
        else:
            dateStr = ""
        self.dateLabel.set_text(dateStr)
        if self.dateLabel not in self.dateLabelHolder.get_children():
            self.dateLabelHolder.add(self.dateLabel)
            self.dateLabelHolder.show_all()


    def _init_ui(self):
        self.set_border_width(6)

        self.builder = Gtk.Builder()
        self.builder.add_from_file(join(Config.DESIGN_DIR,
                                        "DetailedTaskWidget.glade"))
        self.titleLabel = self.builder.get_object("title")
        self.dateLabel = self.builder.get_object("dateLabel")
        self.dateLabelHolder = self.builder.get_object("dateLabelHolder")
        self.descriptionLabel = self.builder.get_object("taskDescription")
        self.archiveIcon = self.builder.get_object("archiveIcon")
        self.whole = self.builder.get_object("DetailedTaskWidget")

        if self.task.archived:
            self._update_archive_icon()

        self.add(self.whole)
        self._select_none()

        self.show_all()


    def _select_none(self):
        """Show no task selected text"""
        noTaskText = self.builder.get_object("noTaskLabel").get_text()
        self.titleLabel.set_text(noTaskText)
        self.descriptionLabel.set_text("")
        self.dateLabel.set_text("")


    def _update_archive_icon(self):
        pixelSize = Gtk.IconSize.BUTTON
        if self.task.archived:
            self.archiveIcon.set_from_icon_name("document-revert", pixelSize)
        else:
            self.archiveIcon.set_from_icon_name("package-x-generic", pixelSize)


    def _connect_signals(self):
        handlers = {"editTask": self._on_edit_task_texts,
                    "editDate": self._on_edit_task_date,
                    "editColor": self._on_edit_task_color,
                    "addSubtask": self._on_add_subtask,
                    "deleteTask": self._on_task_delete,
                    "archive": self._on_archive}
        self.builder.connect_signals(handlers)


    def _on_edit_task_texts(self, button):
        Dialogs.edit_task_title_description(self.get_toplevel(), self.task)

    def _on_edit_task_date(self, button):
        Dialogs.edit_task_date(self.get_toplevel(), self.task)

    def _on_edit_task_color(self, button):
        Dialogs.edit_task_color(self.task)

    def _on_task_delete(self, button):
        self.task.delete()

    def _on_add_subtask(self, button):
        Dialogs.add_subtask(self.get_toplevel(), self.task)

    def _on_archive(self, button):
        if not self.task.archived:
            self.task.archive()
        else:
            self.task.dearchive()
