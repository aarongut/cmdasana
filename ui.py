import urwid

# TaskEdit modes
EDIT = 'edit'
LIST = 'list'

class TaskList(urwid.ListBox):
    def __init__(self, tasks):
        self.tasks = tasks
        task_widgets = urwid.Pile(
            [TaskEdit(task) for task in tasks]
        )

        body = urwid.SimpleFocusListWalker([task_widgets])
        super(TaskList, self).__init__(body)

    def keypress(self, size, key):
        # The ListBox will handle scrolling for us, so we trick it into thinking
        # it's being passed arrow keys
        if key == 'j':
            key = 'down'
        elif key == 'k':
            key = 'up'

        key = super(TaskList, self).keypress(size, key)

        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        else:
            return key

class TaskEdit(urwid.Edit):
    mode = LIST
    def __init__(self, task):
        super(TaskEdit, self).__init__(task["name"])

    def keypress(self, size, key):
        if self.mode == EDIT:
            key = super(TaskEdit, self).keypress(size, key)

            if key == 'esc':
                self.mode = LIST
                self.set_caption(self.edit_text)
                self.set_edit_text('')
            else:
                return key
        else:
            if key == 'i':
                self.mode = EDIT
                self.set_edit_text(self.caption)
                self.set_caption('')
            elif key == 'enter':
                self.set_caption(self.caption + ' [done]')
            elif key in ('l', 'tab'):
                self.set_caption(self.caption + ' [details]')
            else:
                return key
