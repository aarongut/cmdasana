import urwid

from ui.task_list import TaskRow

class TaskDetails(object):
    def __init__(self, task, stories, on_subtask_click, on_project_click,
                 on_comment):
        self.task = task
        self.on_subtask_click = on_subtask_click,
        self.on_project_click = on_project_click,
        self.on_comment = on_comment

        body = [
            urwid.Text(('task', task.name())),
            urwid.Divider('-'),
            Memberships(task, on_subtask_click, on_project_click).component(),
            urwid.Divider('-'),
            CustomFields(task).component(),
            urwid.Divider('='),
            urwid.Text(task.description()),
            urwid.Divider('-'),
        ]

        if task.subtasks():
            body.append(urwid.Pile([
                TaskRow(t, on_subtask_click) for t in task.subtasks()
            ]))

        body = body + [
            urwid.Divider('-'),
            Stories(stories).component()
        ]

        self.details = urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def component(self):
            return self.details

class Memberships(object):
    def __init__(self, task, on_subtask_click, on_project_click):
        components = [urwid.Button(
            ('project', p.name()),
            on_press = lambda x: on_project_click(p.id())
        ) for p in task.projects()]
        if task.parent():
            components.append(urwid.Button(
                ('task', 'Subtask of: %s' % task.parent().name()),
                on_press = lambda x: on_subtask_click(task.parent().id())
            ))

        self.memberships = urwid.Pile(components)

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
        components = [urwid.Text([
            ('author', s.creator()),
            s.text(),
            '\n'
        ]) for s in stories]

        self.stories = urwid.Pile(components)

    def  component(self):
        return self.stories
