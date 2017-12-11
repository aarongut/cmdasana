import urwid
from threading import Thread

from asana_service import AsanaService

from ui.task_list import MyTasks, TaskList
from ui.task_details import TaskDetails

class Ui(object):
    nav_stack = []
    def __init__(self, asana_service, update):
        self.asana_service = asana_service
        self.update = update

    def my_tasks(self):
        self.nav_stack.append(('mytasks', None))

        def runInThread():
            tasks = self.asana_service.get_my_tasks()
            self.update(MyTasks(tasks, self.task_details).component())

        thread = Thread(target=runInThread())
        thread.start()


    def task_details(self, id):
        self.nav_stack.append(('task', id))
        def runInThread():
            task = self.asana_service.get_task(id)
            stories = self.asana_service.get_stories(id)
            self.update(TaskDetails(task,
                                    stories,
                                    self.task_details,
                                    self.task_list,
                                    None).component())
        thread = Thread(target=runInThread())
        thread.start()

    def task_list(self, id):
        self.nav_stack.append(('project', id))
        def runInThread():
            tasks = self.asana_service.get_tasks(id)
            self.update(TaskList(tasks,
                                 'TODO: get project name',
                                 self.task_details
                                ).component())
        thread = Thread(target=runInThread())
        thread.run()

    def go_back(self):
        if len(self.nav_stack) < 2:
            return

        self.nav_stack.pop()
        (location, id) = self.nav_stack.pop()
        if location == 'mytasks':
            self.my_tasks()
        elif location == 'task':
            self.task_details(id)
        elif location == 'project':
            self.task_list(id)


def loading():
    return urwid.Overlay(
        urwid.BigText('Loading...', urwid.font.HalfBlock5x4Font()),
        urwid.SolidFill('#'),
        'center',
        'pack',
        'middle',
        'pack'
    )
