import urwid

from ui.constants import keys

class TaskList(object):
    def __init__(self, tasks, header, on_task_click):
        self.callback = on_task_click
        self.grid = urwid.Frame(
            urwid.ListBox(
                urwid.SimpleFocusListWalker(
                    [TaskRow(t, self.on_task_clicked) for t in tasks]
                )
            ),
            header=urwid.Text(header),
            focus_part='body'
        )

    def on_task_clicked(self, id):
        self.callback(id)

    def component(self):
        return self.grid

class MyTasks(object):
    def __init__(self, tasks, on_task_click):
        all_tasks = [t for t in tasks]

        today = [t for t in all_tasks if t.atm_section() == 'today']
        upcoming = [t for t in all_tasks if t.atm_section() == 'upcoming']
        later = [t for t in all_tasks if t.atm_section() == 'later']

        self.today_grid = TaskList(today,
                                   ('atm_section', 'Today'),
                                   on_task_click)
        self.upcoming_grid = TaskList(upcoming,
                                      ('atm_section', 'Upcoming'),
                                      on_task_click)
        self.later_grid = TaskList(later,
                                   ('atm_section', 'Later'),
                                   on_task_click)

    def component(self):
        return urwid.Frame(urwid.Pile([
                self.today_grid.component(),
                self.upcoming_grid.component(),
                self.later_grid.component()
            ]),
            header=urwid.Text(('header', 'My Tasks')),
            focus_part='body'
        )

class TaskRow(urwid.SelectableIcon):
    def __init__(self, task, on_click):
        self.on_click = on_click
        self.task = task
        style = 'section' if task.name()[-1] == ':' else 'task'
        super(TaskRow, self).__init__((style, task.name()))

    def keypress(self, size, key):
        if key in keys['select']:
            self.on_click(self.task.id())
        else:
            return key
