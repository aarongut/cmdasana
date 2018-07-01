import urwid
from datetime import date, datetime

from ui.task_list import TaskRow

class TaskDetails(object):
    def __init__(self, task, stories, on_subtask_click, on_project_click,
                 on_comment, on_assignee_click, on_due_date_click):
        self.task = task
        self.on_subtask_click = on_subtask_click,
        self.on_project_click = on_project_click,
        self.on_comment = on_comment

        body = [
            urwid.Text(('task', task.name())),
            urwid.Divider('⎼'),
            Memberships(task, on_subtask_click, on_project_click).component(),
            urwid.Divider('⎼'),
            Assignee(task, on_assignee_click).component(),
            DueDate(task, on_due_date_click).component(),
            CustomFields(task).component(),
            urwid.Divider('⎼'),
            urwid.Text(task.description()),
            urwid.Divider('⎼'),
        ]

        if task.subtasks():
            body.append(urwid.Pile([
                TaskRow(t, on_subtask_click) for t in task.subtasks()
            ]))

        stories = list(stories)
        if (len(stories) > 0):
            body = body + [
                urwid.Divider('-'),
                Stories(stories).component()
            ]

        self.details = urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def component(self):
            return self.details

class Assignee(object):
    def __init__(self, task, on_click):
        if task.assignee():
            assignee = task.assignee().name()
        else:
            assignee = "unassigned"


        self.assignee = urwid.SelectableIcon([('strong', 'Assignee: '), ('', assignee)])

        self.on_click = on_click
        #urwid.connect_signal(self.assignee, 'keypress', self.on_keypress)

    def component(self):
        return self.assignee

    def on_keypress(self, size, key):
        if key == "enter":
            self.on_click()
        else:
            return key

class DueDate(object):
    def __init__(self, task, on_click):
        due_date = task.due_date()
        self.due_date = urwid.SelectableIcon([('strong', 'Due: '), ('', str(task.due_date()))])

        self.on_click = on_click
        #urwid.connect_signal(self.due_date, 'keypress', self.on_keypress)

    def component(self):
        return self.due_date

    def on_keypress(self, size, key):
        if key == "enter":
            self.on_click()
        else:
            return key

class Memberships(object):
    def __init__(self, task, on_subtask_click, on_project_click):
        self.on_project_click = on_project_click

        components = [self.membership(p.name(), p.id()) for p in task.projects()]

        if task.parent():
            components.append(urwid.Button(
                ('task', 'Subtask of: %s' % task.parent().name()),
                on_press = lambda x: on_subtask_click(task.parent().id())
            ))

        self.memberships = urwid.Pile(components)

    def membership(self, name, id):
        return urwid.Button(('project', name),
                            on_press = lambda x: self.on_project_click(id)
                           )

    def component(self):
        return self.memberships

class CustomFields(object):
    def __init__(self, task):
        components = [urwid.Text([
            ('custom_fields', f.name() + ': '),
            f.string_value()
        ]) for f in task.custom_fields()]

        self.custom_fields = urwid.Pile(components)

    def component(self):
        return self.custom_fields

class Stories(object):
    def __init__(self, stories):
        components = [
            urwid.Text([('author', s.creator())] + s.text())
        for s in stories]

        self.stories = urwid.Pile(components)

    def  component(self):
        return self.stories
