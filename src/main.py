from sys import argv

from gi.repository.Gtk import Application

from TaskManager import TaskManager
from TreeTodoWindow import TreeTodoWindow



class TreeTodoApplication(Application):

    def __init__(self):
        """Create TreeTodoApplication"""

        Application.__init__(self)
        self.connect("activate", self.on_activate)

        self.taskManager = TaskManager()


    def on_activate(self, *args):
        """Start application"""

        self.add_window(TreeTodoWindow(self.taskManager.rootTask))


if __name__ == "__main__":
    application = TreeTodoApplication()
    application.run(argv)
