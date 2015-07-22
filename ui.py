# -*- coding: latin-1 -*-
import urwid

# TaskEdit modes
EDIT = 'edit'
LIST = 'list'

palette = [
    ('selected', 'standout', ''),
    ('selected workspace', 'standout,bold', ''),
    ('header', 'bold,light green', ''),
    ('task', 'light green', ''),
    ('section', 'white', 'dark green'),
    ('workspace', 'white', 'dark blue')
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
    def keypress(self, size, key):
        if key == 'j':
            key = 'down'
        elif key == 'h':
            key = 'left'
        elif key == 'l':
            key = 'right'
        return super(WorkspaceMenu, self).keypress(size, key)

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
            self.connectSignals(task_widget)
            style = 'section' if task_widget.task['name'][-1] == ':' else 'task'
            body.append(urwid.AttrMap(task_widget, style, focus_map='selected'))

        super(TaskList, self).__init__(body)

    def insertNewTask(self, task):
        task_widget = TaskEdit(task, mode=EDIT)
        self.connectSignals(task_widget)
        index = self.focus_position + 1
        style = 'section' if task['name'][-1] == ':' else 'task'
        self.body.insert(index,
                         urwid.AttrMap(task_widget, style, focus_map='selected'))
        self.focus_position += 1

    def connectSignals(self, task_widget):
        urwid.connect_signal(task_widget, 'complete', self.completeTask)
        urwid.connect_signal(task_widget, 'newtask', self.newTask)
        urwid.connect_signal(task_widget, 'updatetask', self.updateTask)
        urwid.connect_signal(task_widget, 'details', self.details)

    def completeTask(self, task_id):
        urwid.emit_signal(self, 'complete', task_id)
        del self.body[self.focus_position]

    def newTask(self):
        urwid.emit_signal(self, 'newtask')

    def updateTask(self, task_id, name):
        urwid.emit_signal(self, 'updatetask', task_id, name)
    
    def details(self, task_id):
        urwid.emit_signal(self, 'details', task_id)

    def keypress(self, size, key):
        # The ListBox will handle scrolling for us, so we trick it into thinking
        # it's being passed arrow keys
        if self.focus.original_widget.mode == LIST:
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
    completed = False
    def __init__(self, task, mode=LIST):
        self.task = task
        self.mode = mode
        super(TaskEdit, self).__init__(task["name"])

    def keypress(self, size, key):
        if self.mode == EDIT:
            key = super(TaskEdit, self).keypress(size, key)

            if key in ('esc', 'up', 'down'):
                self.mode = LIST
                self.set_caption(self.edit_text)
                self.set_edit_text('')
                urwid.emit_signal(self, 'updatetask', self.task['id'],
                                  self.caption)
                if key != 'esc':
                    return key
        else:
            if key == 'i':
                if self.completed:
                    return
                self.mode = EDIT
                self.set_edit_text(self.caption)
                self.set_caption('')
            elif key == 'tab':
                urwid.emit_signal(self, 'complete', self.task['id'])
            elif key == 'enter':
                urwid.emit_signal(self, 'newtask')
            elif key in ('l', 'right'):
                urwid.emit_signal(self, 'details', self.task['id'])
            else:
                return key

class CommentEdit(urwid.Edit):
    def __init__(self, task):
        self.task = task
        super(CommentEdit, self).__init__('Add a comment:\n')

    def keypress(self, size, key):
        if key != 'enter':
            return super(CommentEdit, self).keypress(size, key)
        urwid.emit_signal(self, 'comment', self.task['id'], self.edit_text)

class TaskDetails(urwid.Pile):
    def __init__(self, task, stories):
        self.task = task
        self.stories = stories

        comment_edit = CommentEdit(task)
        urwid.connect_signal(comment_edit, 'comment', self.comment)

        if task['assignee']:
            assignee = urwid.Text('Assigned to: ' + task['assignee']['name'])
        else:
            assignee = urwid.Text('(not assigned)')


        body = [('pack', urwid.Text(project['name']))
                                for project in task['projects']] + \
            [
                ('pack', urwid.Divider('=')),
                ('pack', urwid.Text(('header', task['name']))),
                ('pack', assignee),
                ('pack', urwid.Divider('-')),
                ('pack', urwid.Text(task['notes'])),
            ] + \
            [('pack', urwid.Text('[' + story['created_by']['name'] + '] ' + \
                        story['text'])) for story in stories] + \
            [
                ('weight', 1, urwid.Filler(comment_edit, 'bottom'))
            ]

        super(TaskDetails, self).__init__(body)

    def comment(self, task_id, comment):
        urwid.emit_signal(self, 'comment', task_id, comment)
