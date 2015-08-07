# -*- coding: latin-1 -*-
import urwid
import sys

# TaskEdit modes
EDIT = 'edit'
LIST = 'list'

palette = [
    ('selected', 'standout', ''),
    ('selected workspace', 'standout,bold', ''),
    ('header', 'bold,light green', ''),
    ('secondary', 'light gray', ''),
    ('task', 'light green', ''),
    ('section', 'white', 'dark green'),
    ('workspace', 'white', 'dark blue'),
    ('pager', 'standout', ''),
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

class PagerButton(urwid.Button):
    def __init__(self, loadPage):
        super(PagerButton, self).__init__(('pager', 'load more'))
        urwid.connect_signal(self, 'click', loadPage)

class TypeAheadButton(urwid.Button):
    def __init__(self, item, onClick):
        super(TypeAheadButton, self).__init__(item['name'])
        urwid.connect_signal(self, 'click', onClick, item)

class ProjectIcon(urwid.SelectableIcon):
    def __init__(self, project, onClick):
        self.project = project
        self.onClick = onClick
        super(ProjectIcon, self).__init__(project['name'])

    def keypress(self, size, key):
        if key in ('enter', 'right', 'l'):
            self.onClick(self.project['id'])
        else:
            return super(ProjectIcon, self).keypress(size, key)

class ProjectList(urwid.ListBox):
    def __init__(self, projects):
        self.projects = projects

        body = urwid.SimpleFocusListWalker(
            [ProjectIcon({'name': 'My Tasks', 'id': None},
                         self.loadProject),
             None]
        )
        super(ProjectList, self).__init__(body)
        self.loadPage()

    def loadPage(self, opt=None):
        self.body.pop()
        for i in range(50):
            try:
                self.body.append(ProjectIcon(self.projects.next(),
                                             self.loadProject))
            except StopIteration:
                return

        self.body.append(PagerButton(self.loadPage))

    def keypress(self, size, key):
        if key == 'j':
            key = 'down'
        elif key == 'k':
            key = 'up'

        return super(ProjectList, self).keypress(size, key)

    def loadProject(self, project_id):
        urwid.emit_signal(self, 'loadproject', project_id)


class TaskList(urwid.ListBox):
    def __init__(self, tasks):
        self.tasks = tasks
        
        task_widgets = urwid.Pile(
            [TaskEdit(task) for task in tasks]
        )

        body = urwid.SimpleFocusListWalker([])
        for task_widget,_ in task_widgets.contents:
            self.connectSignals(task_widget)
            style = 'section' if len(task_widget.task['name']) and \
                    task_widget.task['name'][-1] == ':' else 'task'
            body.append(urwid.AttrMap(task_widget, style, focus_map='selected'))

        super(TaskList, self).__init__(body)

    def insertNewTask(self, task):
        task_widget = TaskEdit(task, mode=EDIT)
        self.connectSignals(task_widget)
        index = self.focus_position + 1
        self.body.insert(index,
                         urwid.AttrMap(task_widget, 'task',
                                       focus_map='selected'))
        self.focus_position += 1

    def connectSignals(self, task_widget):
        urwid.connect_signal(task_widget, 'complete', self.completeTask)
        urwid.connect_signal(task_widget, 'newtask', self.newTask)
        urwid.connect_signal(task_widget, 'updatetask', self.updateTask)
        urwid.connect_signal(task_widget, 'details', self.details)

    def completeTask(self, task_id):
        urwid.emit_signal(self, 'complete', task_id)
        del self.body[self.focus_position]

    def newTask(self, task_after_id=None):
        urwid.emit_signal(self, 'newtask', task_after_id)

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
                urwid.emit_signal(self, 'newtask', self.task['id'])
            elif key in ('l', 'right'):
                urwid.emit_signal(self, 'details', self.task['id'])
            else:
                return key

class CommentEdit(urwid.Edit):
    def __init__(self, task):
        self.task = task
        super(CommentEdit, self).__init__(('secondary', u'Add a comment:\n'))

    def keypress(self, size, key):
        if key != 'enter':
            return super(CommentEdit, self).keypress(size, key)
        urwid.emit_signal(self, 'comment', self.task['id'], self.edit_text)

class TaskNameEdit(urwid.Edit):
    def __init__(self, task):
        self.task = task
        super(TaskNameEdit, self).__init__(('secondary',
                                            u'#' + str(task['id']) + ' '),
                                           task['name'])

    def keypress(self, size, key):
        if key in ('enter', 'esc', 'up', 'down'):
            if (self.edit_text != self.task['name']):
                urwid.emit_signal(self, 'updatetask', self.task['id'],
                                  self.edit_text)
        return super(TaskNameEdit, self).keypress(size, key)

class DescriptionEdit(urwid.Edit):
    def __init__(self, task):
        self.task = task
        super(DescriptionEdit, self).__init__(('secondary', u'Description:\n'),
                                              task['notes'],
                                              multiline=True)

    def keypress(self, size, key):
        if key != 'esc':
            return super(DescriptionEdit, self).keypress(size, key)
        urwid.emit_signal(self, 'updatedescription', self.task['id'],
                          self.edit_text)

class AssigneeTypeAhead(urwid.Pile):
    def __init__(self, task):
        self.task = task

        if task['assignee'] != None:
            assignee = task['assignee']['name']
        else:
            assignee = ""

        self.edit = urwid.Edit('Assignee: ', assignee)
        urwid.connect_signal(self.edit, 'change', self.typeAhead)

        body = [('pack', self.edit)]

        super(AssigneeTypeAhead, self).__init__(body)

    def typeAhead(self, widget, text):
        urwid.emit_signal(self, 'usertypeahead', text, self.updateTypeAhead)

    def updateTypeAhead(self, users):
        users = [(TypeAheadButton(u, self.assign), ('pack', None)) for u in users]

        users.insert(0, self.contents[0])

        self.contents = users

    def assign(self, widget, user):
        urwid.emit_signal(self, 'assigntask', self.task['id'], user['id'])
        self.contents = [self.contents[0]]
        self.edit.set_edit_text(user['name'])

class TaskDetails(urwid.ListBox):
    def __init__(self, task, stories, subtasks):
        self.task = task
        self.stories = stories

        comment_edit = CommentEdit(task)
        urwid.connect_signal(comment_edit, 'comment', self.comment)

        self.description_edit = DescriptionEdit(task)
        urwid.connect_signal(self.description_edit, 'updatedescription',
                             self.updateDescription)
        
        task_name_edit = TaskNameEdit(task)
        urwid.connect_signal(task_name_edit, 'updatetask', self.updateTask)

        assignee_type_ahead = AssigneeTypeAhead(task)
        urwid.connect_signal(assignee_type_ahead, 'usertypeahead',
                             self.userTypeAhead)
        urwid.connect_signal(assignee_type_ahead, 'assigntask', self.assignTask)

        projects = [ProjectIcon(project, self.loadProject)
                    for project in task['projects']]

        if task['parent'] != None:
            parent = TaskEdit(task['parent'])
            urwid.connect_signal(parent, 'updatetask', self.updateSubtask)
            urwid.connect_signal(parent, 'details', self.showDetails)
            projects.append(parent)
    
        all_subtasks = [t for t in subtasks]
        subtask_list = TaskList(all_subtasks)
        urwid.connect_signal(subtask_list, 'complete', self.completeTask)
        urwid.connect_signal(subtask_list, 'newtask', self.newTask)
        urwid.connect_signal(subtask_list, 'updatetask', self.updateSubtask)
        urwid.connect_signal(subtask_list, 'details', self.showDetails)

        body = projects + \
            [
                urwid.Divider('='),
                task_name_edit,
                assignee_type_ahead,
                urwid.Divider('-'),
                self.description_edit,
                urwid.Divider('-'),
                urwid.BoxAdapter(subtask_list, len(all_subtasks)),
                urwid.Divider('-'),
            ] + \
            [urwid.Text('[' + story['created_by']['name'] + '] ' + \
                        story['text']) for story in stories] + \
            [comment_edit]

        super(TaskDetails, self).__init__(body)

    def completeTask(self, task_id):
        urwid.emit_signal(self, 'complete', task_id)
        del self.body[self.focus_position]

    def newTask(self, task_after_id=None):
        urwid.emit_signal(self, 'newtask', task_after_id)

    def updateSubtask(self, task_id, name):
        urwid.emit_signal(self, 'updatetask', task_id, name)
    
    def showDetails(self, task_id):
        urwid.emit_signal(self, 'details', task_id)

    def keypress(self, size, key):
        key = super(TaskDetails, self).keypress(size, key)

        if self.focus != self.description_edit and \
           self.description_edit.edit_text != self.task['notes']:
            self.updateDescription(self.task['id'],
                                   self.description_edit.edit_text)

        return key

    def comment(self, task_id, comment):
        urwid.emit_signal(self, 'comment', task_id, comment)

    def updateDescription(self, task_id, description):
        urwid.emit_signal(self, 'updatedescription', task_id, description)

    def updateTask(self, task_id, name):
        urwid.emit_signal(self, 'updatetask', task_id, name)

    def loadProject(self, project_id):
        urwid.emit_signal(self, 'loadproject', project_id)

    def userTypeAhead(self, text, callback):
        urwid.emit_signal(self, 'usertypeahead', text, callback)

    def assignTask(self, task_id, user_id):
        urwid.emit_signal(self, 'assigntask', task_id, user_id)
