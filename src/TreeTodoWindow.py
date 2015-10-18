import os

from gi.repository import Gtk, Gdk

from TaskTreeElement import TaskTreeElement
from ArchiveWidget import ArchiveWidget
from AgendaWidget import AgendaWidget
from Task import TaskUpdateType
import Dialogs
import Config



class TreeTodoWindow(Gtk.Window):

    def __init__(self, rootTask):
        Gtk.Window.__init__(self)
        self.set_default_size(Config.DEFAULT_WIDTH, Config.DEFAULT_HEIGHT)
        self.connect("delete-event", Gtk.main_quit)

        self.rootTask = rootTask
        rootTask.color = Config.DEFAULT_BG

        for task in (rootTask.get_all_subtasks() +
                     rootTask.get_all_archived_subtasks()):
            task.connect("updated", self.on_task_updated)

        self._build()
        self._create_ui()


    def on_task_updated(self, task, updateType):
        # Do not update contents of TaskTreeElement's here
        # but only their presence in various containers
        # TODO revisit
        if updateType == TaskUpdateType.SUBTASK_ADDED:
            for subtask in task.subtasks:
                subtask.connect("updated", self.on_task_updated)
                if subtask.date:
                    self.agendaWidget.on_update_task(subtask)
            self._update_pane_text()

        elif updateType == TaskUpdateType.DATE:
            self.agendaWidget.on_update_task(task)

        elif updateType == TaskUpdateType.DELETED:
            self.agendaWidget.on_task_deleted(task)
            if self.agendaWidget.get_dated_tasks(self.rootTask):
                self.stack.set_visible_child(self.agendaWidget)
            self._update_pane_text()

        elif updateType == TaskUpdateType.ARCHIVED:
            self.agendaWidget.on_task_deleted(task)
            self.archiveWidget.on_task_archived(task)
            self._update_pane_text()

        elif updateType == TaskUpdateType.DEARCHIVED:
            self.archiveWidget.on_task_dearchived(task)
            self.agendaWidget.on_update_task(task)
            self._update_pane_text()


    def _create_ui(self):
        self._init_stack()
        self._init_header()
        self.show_all()


    def _build(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(Config.DESIGN_DIR,
                                                "Window.glade"))

        self.scroll = self.builder.get_object("scrolledWindow")
        self.addButton = self.builder.get_object("addButton")
        self.noTaskLabel = self.builder.get_object("noTaskLabel")


    def _init_stack(self):
        self.tasks = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.rootElement = TaskTreeElement(self.rootTask)
        self.rootElement.toggle_on()
        # Root element should not be visible
        self.rootElement.remove(self.rootElement.get_children()[0])
        self.tasks.pack_end(self.rootElement, True, True, 0)

        if not self.rootTask.subtasks:
            self.tasks.add(self.noTaskLabel)

        self.scroll.add_with_viewport(self.tasks)

        self.agendaWidget = AgendaWidget(self.rootTask)
        self.archiveWidget = ArchiveWidget(self.rootTask)

        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stackSwitcher = Gtk.StackSwitcher(stack=self.stack)

        self.stack.add_titled(self.scroll, "tasks", "Tasks")
        self.stack.add_titled(self.agendaWidget, "agenda", "Agenda")
        self.stack.add_titled(self.archiveWidget, "archive", "Archive")

        self.add(self.stack)


    def _init_header(self):
        self.headerBar = Gtk.HeaderBar()
        self.headerBar.set_show_close_button(True)
        self.addButton.connect("clicked", self._new_task)
        self.headerBar.pack_start(self.addButton)
        self.headerBar.set_custom_title(self.stackSwitcher)
        self.set_titlebar(self.headerBar)


    def _new_task(self, *args):
        Dialogs.add_subtask(self, self.rootTask)


    def _update_pane_text(self):
        if (not self.rootTask.subtasks and
                self.noTaskLabel not in self.paneContent.get_children()):
            self.paneContent.pack_start(self.noTaskLabel, False, False, 12)
        elif (self.rootTask.subtasks and
                self.noTaskLabel in self.paneContent.get_children()):
            self.paneContent.remove(self.noTaskLabel)
