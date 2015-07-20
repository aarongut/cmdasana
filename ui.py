import urwid
from event import Event

# TaskEdit modes
EDIT = 'edit'
LIST = 'list'

palette = [
    ('selected', 'standout', ''),
    ('selected workspace', 'white', 'dark red'),
]

class WorkspaceMenu(urwid.Columns):
    def __init__(self, workspaces):
        super(WorkspaceMenu, self).__init__([], dividechars=1)

        for workspace in workspaces:
            button = WorkspaceButton(workspace, self.loadWorkspace)
            self.contents.append((urwid.AttrMap(button,
                                               None,
                                               focus_map='selected workspace'),
                                 self.options('given', 24)))

    def loadWorkspace(self, widget, workspace_id):
        urwid.emit_signal(self, 'click', workspace_id)

class WorkspaceButton(urwid.Button):
    def __init__(self, workspace, onClick):
        super(WorkspaceButton, self).__init__(workspace['name'])
        urwid.connect_signal(self, 'click', onClick, workspace['id'])

class TaskList(urwid.ListBox):
    def __init__(self, tasks):
        self.tasks = tasks
        
        task_widgets = urwid.Pile(
            [TaskEdit(task) for task in tasks]
        )

        body = urwid.SimpleFocusListWalker([])
        for task_widget,_ in task_widgets.contents:
            urwid.connect_signal(task_widget, 'complete', self.completeTask)
            body.append(urwid.AttrMap(task_widget, None, focus_map='selected'))

        super(TaskList, self).__init__(body)

    def completeTask(self, task_id):
        del self.focus.contents[self.focus.focus_position]
        urwid.emit_signal(self, 'complete', task_id)

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
        self.task = task
        super(TaskEdit, self).__init__(task["name"])
    

    def keypress(self, size, key):
        if self.mode == EDIT:
            key = super(TaskEdit, self).keypress(size, key)

            if key in ('esc', 'up', 'down'):
                self.mode = LIST
                self.set_caption(self.edit_text)
                self.set_edit_text('')
                if key != 'esc':
                    return key
            else:
                return key
        else:
            if key == 'i':
                self.mode = EDIT
                self.set_edit_text(self.caption)
                self.set_caption('')
            elif key == 'enter':
                urwid.emit_signal(self, 'complete', self.task['id'])
            elif key in ('l', 'tab'):
                pass
            else:
                return key
