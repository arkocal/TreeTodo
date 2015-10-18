from os.path import join

from gi.repository import GObject, Gtk, Gdk

from TreeElement import TreeElement
from Task import TaskUpdateType
import Config
import Dialogs



class TaskTreeElement(TreeElement):

    def __init__(self, task, includeArchived=False):
        TreeElement.__init__(self)
        self.task = task
        self.task.connect("updated", self.on_task_updated)

        self._init_ui()

        for subtask in self.task.subtasks:
            childElement = TaskTreeElement(subtask, includeArchived)
            self.add_child_element(childElement)
        if includeArchived:
            for subtask in self.task.archivedSubtasks:
                childElement = TaskTreeElement(subtask, includeArchived)
                self.add_child_element(childElement)



    def add_child_element(self, childElement):
        TreeElement.add_child_element(self, childElement)
        childElement.set_has_tooltip(False)


    def activate(self):
        self.task.emit("activated")


    def activate_secondary(self):
        Dialogs.TaskEditPopover(self)


    def on_task_updated(self, task, updateType):
        if task != self.task:
            return

        if updateType == TaskUpdateType.TITLE:
            self.titleLabel.set_text(self.task.title)

        elif updateType == TaskUpdateType.COLOR:
            self._update_color()

        elif updateType == TaskUpdateType.DATE:
            self._update_date()

        elif updateType == TaskUpdateType.DONE:
            self._update_done()

        elif updateType == TaskUpdateType.SUBTASK_ADDED:
            self._on_subtask_added()

        elif updateType == TaskUpdateType.DELETED:
            if self._parent:
                self._parent.remove_child_element(self)
            elif Gtk.Widget.get_parent(self):
                Gtk.Widget.get_parent(self).remove(self)

        elif updateType == TaskUpdateType.ARCHIVED:
            if not self._in_archive():
                if self._parent:
                    self._parent.remove_child_element(self)
                elif Gtk.Widget.get_parent(self):
                    Gtk.Widget.get_parent(self).remove(self)

        elif updateType == TaskUpdateType.SUBTASK_DEARCHIVED:
            self._on_subtask_dearchived()


    def _update_color(self):
        """Update task widget color"""
        self.modify_bg(Gtk.StateType.NORMAL,
                       Gdk.Color.parse(self.task.color)[1])
        # Choose correct foreground color
        red = int(self.task.color[1:3], 16)
        green = int(self.task.color[3:5], 16)
        blue = int(self.task.color[5:], 16)
        gray = red * 0.299 + green * 0.587 + blue * 0.114
        if gray > 186:
            self.titleLabel.modify_fg(0, Gdk.Color.parse("#000")[1])
            self.dateLabel.modify_fg(0, Gdk.Color.parse("#000")[1])
        else:
            self.titleLabel.modify_fg(0, Gdk.Color.parse("#FFF")[1])
            self.dateLabel.modify_fg(0, Gdk.Color.parse("#FFF")[1])


    def _update_date(self, *args):
        """Update UI when task date is changed"""
        if self.task.date:
            date = self.task.date
            dateStr = "{}/{}/{}".format(date[2], date[1], date[0])
            self.dateLabel.set_text(dateStr)
        if (self.dateLabel in self.labelHolder.get_children() and
                not self.task.date):
            self.labelHolder.remove(self.dateLabel)
        if (self.dateLabel not in self.labelHolder.get_children() and
                self.task.date):
            self.labelHolder.add(self.dateLabel)


    def _update_done(self):
        """Makes necessary UI changes after done is toggled

        If task has no children, a checkbox is shown, otherwise
        an ok emblem is shown if the task is completed.
        """
        if self.task.subtasks:
            if self.doneButton in self.ui.get_children():
                self.ui.remove(self.doneButton)
            if self.doneImage not in self.ui.get_children():
                self.ui.pack_end(self.doneImage, False, False, 6)
            if self.task.done:
                theme = Gtk.IconTheme.get_default()
                img = theme.load_icon("emblem-ok-symbolic", 16, 0)
            else:
                img = None
            self.doneImage.set_from_pixbuf(img)
        else:
            if self.doneButton not in self.ui.get_children():
                self.ui.add(self.doneButton)
            self.doneButton.set_active(self.task.done)
            if self.doneImage in self.ui.get_children():
                self.ui.remove(self.doneImage)


    def _in_archive(self):
        """ Return whether the Element is in an Archive view """
        topmost = self
        while topmost._parent:
            topmost = topmost._parent
        return topmost.task.archived


    def _on_subtask_added(self):
        subtask = self.task.subtasks[-1]
        newElement = TaskTreeElement(subtask)
        self.add_child_element(newElement)
        self.toggle_on()


    def _on_subtask_dearchived(self):
        subtask = self.task.subtasks[-1]
        newElement = TaskTreeElement(subtask)
        self.add_child_element(newElement)
        self.toggle_on()


    def _init_ui(self):
        builder = Gtk.Builder()
        builder.add_from_file(join(Config.DESIGN_DIR, "TaskWidget.glade"))
        self.ui = builder.get_object("TaskWidget")
        self.titleLabel = builder.get_object("titleLabel")
        self.dateLabel = builder.get_object("dueLabel")
        self.doneImage = builder.get_object("doneImage")
        self.doneButton = builder.get_object("doneButton")
        self.labelHolder = builder.get_object("labelHolder")

        self.titleLabel.set_text(self.task.title)
        self._update_date()
        self._update_done()

        self.set_widget(self.ui)
        self._update_color()

        if self.task.parent and self.task.parent.is_real_task():
            self.set_has_tooltip(True)
            self.set_tooltip_text(self.task.parent.title)

        self.show_all()

        handlers = {"doneToggle": self._on_done_toggle}
        builder.connect_signals(handlers)


    def _on_done_toggle(self, button):
        self.task.set_done(self.doneButton.get_active())
