import urwid

from ui.constants import keys

class TaskList(object):
    def __init__(self, tasks, header, on_task_click):
        self.callback = on_task_click
        self.grid = urwid.Frame(
            urwid.ListBox(
                urwid.SimpleFocusListWalker(
                    [TaskRow(t, self.callback) for t in tasks]
                )
            ),
            header=urwid.Text(('header', header)),
            focus_part='body'
        )

    def component(self):
        return self.grid

class MyTasks(object):
    def __init__(self, tasks, on_task_click):
        self.callback = on_task_click
        all_tasks = [t for t in tasks]

        self.new = [t for t in all_tasks if t.atm_section() == 'inbox']
        self.today = [t for t in all_tasks if t.atm_section() == 'today']
        self.upcoming = [t for t in all_tasks if t.atm_section() == 'upcoming']
        self.later = [t for t in all_tasks if t.atm_section() == 'later']

    def component(self):
        return urwid.Frame(
            urwid.ListBox(
                urwid.SimpleFocusListWalker([
                    urwid.Text(('atm_section', 'New'))
                ] + [TaskRow(t, self.callback) for t in self.new] + [
                    urwid.Text(('atm_section', 'Today'))
                ] + [TaskRow(t, self.callback) for t in self.today] + [
                    urwid.Text(('atm_section', 'Upcoming'))
                ] + [TaskRow(t, self.callback) for t in self.upcoming] + [
                    urwid.Text(('atm_section', 'Upcoming'))
                ] + [TaskRow(t, self.callback) for t in self.later]
                )
            ),
            header=urwid.Text(('header', 'My Tasks')),
            focus_part='body'
        )

class TaskRow(urwid.SelectableIcon):
    def __init__(self, task, on_click):
        self.on_click = on_click
        self.task = task
        style = 'section' if task.name() and task.name()[-1] == ':' else 'task'
        super(TaskRow, self).__init__((style, task.name()))

    def keypress(self, size, key):
        if key in keys['select']:
            self.on_click(self.task.id())
        else:
            return key
