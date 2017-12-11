import urwid

class TaskDetails(object):
    def __init__(self, task, stories, on_subtask_click, on_project_click,
                 on_comment):
        self.task = task
        self.on_subtask_click = on_subtask_click,
        self.on_project_click = on_project_click,
        self.on_comment = on_comment

        self.details = urwid.Pile([
            ('pack', urwid.Text(('task', task.name()))),
            ('pack', urwid.Divider('-')),
            ('weight', 1, Memberships(task, on_subtask_click, on_project_click) \
             .component()),
            ('pack', urwid.Divider('-')),
            ('pack', CustomFields(task).component()),
            ('pack', urwid.Divider('-')),
            ('weight', 20, urwid.Filler(urwid.Text(task.description()))),
            ('weight', 5, urwid.Filler(Stories(stories).component()))
        ])

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

        self.memberships = urwid.ListBox(
            urwid.SimpleFocusListWalker(components)
        )

    def component(self):
        return self.memberships

class CustomFields(object):
    def __init__(self, task):
        components = [urwid.Text('%s: %s' % (f.name(), f.string_value()))
                      for f in task.custom_fields()]

        self.custom_fields = urwid.Pile(components)

    def component(self):
        return self.custom_fields

class Stories(object):
    def __init__(self, stories):
        components = [urwid.Text(s.string_value()) for s in stories]

        self.stories = urwid.Pile(components)

    def  component(self):
        return self.stories
