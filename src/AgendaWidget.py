from os.path import join
from datetime import date

from gi.repository import Gtk, Gdk

from TaskTreeElement import TaskTreeElement
import Config



class AgendaWidget(Gtk.ScrolledWindow):

    def __init__(self, rootTask):
        Gtk.ScrolledWindow.__init__(self)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.listbox.modify_bg(0, Gdk.Color.parse(Config.DEFAULT_BG)[1])
        self.add(self.listbox)

        self.tasks = self.get_dated_tasks(rootTask)
        self.populate()


    def on_update_task(self, task):
        """Update task date in UI"""
        # Get task element displaying given task
        taskElement = None
        found = False
        for row in self.listbox.get_children():
            taskElement = row.get_child()
            if not isinstance(taskElement, TaskTreeElement):
                continue
            if taskElement.task == task:
                found = True
                break

        # Add element if not present
        if not found and task.date is not None and not task.archived:
            self.tasks.append(task)
            self.tasks.sort(key=lambda t: t.date)
            index = self.tasks.index(task)

            newElement = TaskTreeElement(task)
            newElement.set_margin_top(6)

            row = Gtk.ListBoxRow()
            row.add(newElement)
            row.modify_bg(0, Gdk.Color.parse(Config.DEFAULT_BG)[1])

            self.listbox.insert(row, index)

        # Remove element is date is removed
        elif taskElement.task.date is None:
            row = Gtk.Widget.get_parent(taskElement)
            self.listbox.remove(row)
            self.tasks.remove(task)

        self._update_timeline_labels()


    def on_task_deleted(self, task):
        if task not in self.tasks:
            return

        for row in self.listbox.get_children():
            taskElement = row.get_child()
            if not isinstance(taskElement, TaskTreeElement):
                continue
            if taskElement.task == task:
                row.remove(taskElement)
                self.listbox.remove(row)
                break

        self.tasks.remove(task)
        self._update_timeline_labels()


    def get_dated_tasks(self, rootTask):
        """Return a list of rootTask's subtasks which have a date stated
        sorted by dates."""
        tasks = [task for task in rootTask.get_all_children() if task.date]
        tasks.sort(key=lambda task: task.date)
        return tasks


    def populate(self):
        """Add elements of self.tasks to UI"""
        for task in self.tasks:
            taskWidget = TaskTreeElement(task)
            taskWidget.set_margin_top(Config.MARGIN)
            row = Gtk.ListBoxRow()
            row.modify_bg(0, Gdk.Color.parse(Config.DEFAULT_BG)[1])
            row.add(taskWidget)
            self.listbox.add(row)

        self._update_timeline_labels()


    def _update_timeline_labels(self):

        # Remove all timeline labels
        for row in self.listbox.get_children():
            element = row.get_child()
            if element is None:
                self.listbox.remove(row)  # Remove empty rows
            if isinstance(element, Gtk.Label):
                row.remove(element)
                self.listbox.remove(row)

        intervals = [0, 1, 2, 7, 14]
        last = -1000000000  # There should not be any older tasks than this
        # if there is, that guy has deserved a bug.
        # TODO develop a proper solution
        builder = Gtk.Builder()
        builder.add_from_file(join(Config.DESIGN_DIR, "Agenda.glade"))
        labels = {0: builder.get_object("oneday"),
                  1: builder.get_object("twodays"),
                  2: builder.get_object("oneweek"),
                  7: builder.get_object("twoweeks"),
                  14: builder.get_object("more")}
        emptyLabel = builder.get_object("emptyLabel")
        today = date.today()

        if not len(self.listbox.get_children()):  # No scheduled tasks
            row = Gtk.ListBoxRow()
            row.add(emptyLabel)
            row.modify_bg(0, Gdk.Color.parse(Config.DEFAULT_BG)[1])
            self.listbox.add(row)
            self.listbox.show_all()
            return

        i = 0
        while i < len(self.listbox.get_children()):
            row = self.listbox.get_row_at_index(i)
            task = row.get_child().task
            taskDate = date(*task.date)
            dayDiff = (taskDate - today).days
            validIntervals = [i for i in intervals if i <= dayDiff]
            if validIntervals:
                candidate = max(validIntervals)
                if candidate > last:
                    row = Gtk.ListBoxRow()
                    row.add(labels[candidate])
                    row.modify_bg(0, Gdk.Color.parse(Config.DEFAULT_BG)[1])
                    self.listbox.insert(row, i)
                    last = candidate
                    i += 1
            i += 1
        self.listbox.show_all()
