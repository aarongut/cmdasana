#!/usr/bin/env python
# -*- coding: latin-1 -*-
import json
import os
import sys
from threading import Thread

import urwid
import asana

import ui
from auth import Auth
from data import Data

class CmdAsana:
    loop = None

    def __init__(self):
        auth = Auth()
        self.data = Data(auth.getClient())

    def saveState(self):
        f = open('.state', 'w')
        f.write(json.dumps(self.state))
        f.close()

    def loadState(self):
        try:
            f = open('.state', 'r')
            self.state = json.loads(f.readline())
            f.close()
        except IOError:
            workspace_id = self.myWorkspaces()[0]['id']
            self.state = {
                'view': 'workspace',
                'id': workspace_id,
                'workspace_id': workspace_id
            }


    def newTask(self, task_after_id):
        def runInThread():
            if self.state['view'] == 'project':
                task = self.data.createTask(
                    self.state['workspace_id'],
                    opt_projects=[self.state['id']],
                    opt_after=task_after_id
                )
            else:
                task = self.data.createTask(
                    self.state['workspace_id'],
                    assignee=self.me['id']
                )

            update(task)

        def update(task):
            task_list,_ = self.frame.contents[1]
            task_list.insertNewTask(task)
            self.loop.draw_screen()

        thread = Thread(target=runInThread)
        thread.start()

    def updateTask(self, task_id, opt_name=None, opt_projects=None,
                   opt_assignee=None, opt_notes=None):
        def runInThread():
            self.data.updateTask(task_id,
                                 opt_name=opt_name,
                                 opt_projects=opt_projects,
                                 opt_assignee=opt_assignee,
                                 opt_notes=opt_notes)

        thread = Thread(target=runInThread)
        thread.start()

    def addComment(self, task_id, comment):
        def runInThread():
            self.data.addComment(task_id, comment)
            self.showDetails(task_id, show_loading=False)

        thread = Thread(target=runInThread)
        thread.start()

    def userTypeAhead(self, text, callback):
        def runInThread():
            callback(self.data.userTypeahead(self.state['workspace_id'], text))
            self.loop.draw_screen()

        thread = Thread(target=runInThread)
        thread.start()

    def replaceBody(self, widget):
        old_widget,_ = self.frame.contents.pop()
        if old_widget != None:
            self.clearSignals(old_widget)
        self.frame.contents.append((widget, self.frame.options()))
        self.frame.focus_position = 0
        if self.loop != None:
            self.loop.draw_screen()

    def showMainLoading(self):
        text = urwid.Text(('loading', '[loading...]'))
        self.replaceBody(urwid.Filler(text))

    def showMyTasks(self, workspace_id):
        self.state['view'] = 'atm'
        self.state['id'] = workspace_id
        self.state['workspace_id'] = workspace_id

        self.showMainLoading()

        def runInThread():
            tasks = self.data.myTasks(workspace_id)
            update(tasks)

        def update(tasks):
            task_list = ui.TaskList(tasks)
            self.connectTaskListSignals(task_list)
            self.replaceBody(task_list)

        thread = Thread(target=runInThread)
        thread.start()

    def showProject(self, project_id):
        if project_id == None:
            return self.showMyTasks(self.state['workspace_id'])
        self.state['view'] = 'project'
        self.state['id'] = project_id

        self.showMainLoading()

        def runInThread():
            tasks = self.data.tasksInProject(project_id)
            update(tasks)

        def update(tasks):
            task_list = ui.TaskList(tasks)
            self.connectTaskListSignals(task_list)
            self.replaceBody(task_list)

        thread = Thread(target=runInThread)
        thread.start()

    def showProjectList(self, workspace_id):
        self.state['view'] = 'workspace'
        self.state['id'] = workspace_id
        self.state['workspace_id'] = workspace_id
        self.workspace_id = workspace_id

        self.showMainLoading()

        def runInThread():
            projects = self.data.allMyProjects()
            update(projects)

        def update(projects):
            project_list = ui.ProjectList(projects)
            urwid.connect_signal(project_list, 'loadproject', self.showProject)
            self.replaceBody(project_list)

        thread = Thread(target=runInThread)
        thread.start()

    def showDetails(self, task_id, show_loading=True):
        self.state['view'] = 'details'
        self.state['id'] = task_id

        if show_loading:
            self.showMainLoading()

        def runInThread():
            task, stories, subtasks = self.data.getTask(task_id)
            update(task, stories, subtasks)

        def update(task, stories, subtasks):
            task_details = ui.TaskDetails(task, stories, subtasks)
            self.connectDetailsSignals(task_details)
            self.replaceBody(task_details)

        thread = Thread(target=runInThread)
        thread.start()

    def registerSignals(self):
        urwid.register_signal(ui.TaskList, [
            'complete',
            'newtask',
            'updatetask',
            'details',
        ])
        urwid.register_signal(ui.TaskEdit, [
            'complete',
            'newtask',
            'updatetask',
            'details',
        ])

        urwid.register_signal(ui.TaskDetails, [
            'comment',
            'loadproject',
            'updatedescription',
            'updatetask',
            'usertypeahead',
            'assigntask',
            'complete',
            'newtask',
            'details',
        ])

        urwid.register_signal(ui.AssigneeTypeAhead, [
            'usertypeahead',
            'assigntask',
        ])

        urwid.register_signal(ui.CommentEdit, ['comment'])
        urwid.register_signal(ui.DescriptionEdit, ['updatedescription'])
        urwid.register_signal(ui.TaskNameEdit, 'updatetask')
        urwid.register_signal(ui.WorkspaceMenu, 'click')
        urwid.register_signal(ui.ProjectList, 'loadproject')


    def clearSignals(self, widget):
        urwid.disconnect_signal(widget, 'complete', self.completeTask)
        urwid.disconnect_signal(widget, 'newtask', self.newTask)
        urwid.disconnect_signal(widget, 'updatetask', self.updateTask)
        urwid.disconnect_signal(widget, 'details', self.showDetails)
        urwid.disconnect_signal(widget, 'updatedescription',
                                self.updateDescription)
        urwid.disconnect_signal(widget, 'updatetask', self.updateTask)
        urwid.disconnect_signal(widget, 'usertypeahead', self.userTypeAhead)

    def connectTaskListSignals(self, task_list):
        urwid.connect_signal(task_list, 'complete', self.completeTask)
        urwid.connect_signal(task_list, 'newtask', self.newTask)
        urwid.connect_signal(task_list, 'updatetask', self.updateTask)
        urwid.connect_signal(task_list, 'details', self.showDetails)

    def connectDetailsSignals(self, task_details):
        urwid.connect_signal(task_details, 'comment', self.addComment)
        urwid.connect_signal(task_details, 'loadproject', self.showProject)
        urwid.connect_signal(task_details, 'updatedescription',
                             self.updateDescription)
        urwid.connect_signal(task_details, 'updatetask', self.updateTask)
        urwid.connect_signal(task_details, 'usertypeahead', self.userTypeAhead)
        urwid.connect_signal(task_details, 'assigntask', self.assignTask)
        urwid.connect_signal(task_details, 'complete', self.completeTask)
        urwid.connect_signal(task_details, 'newtask', self.newTask)
        urwid.connect_signal(task_details, 'details', self.showDetails)

    def handleInput(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def render(self):
        urwid.set_encoding("UTF-8")
        self.registerSignals()

        workspace_menu = ui.WorkspaceMenu(self.data.myWorkspaces())
        urwid.connect_signal(workspace_menu, 'click', self.showProjectList)

        self.frame = urwid.Pile([
            ('pack', urwid.AttrMap(workspace_menu, 'workspace')),
            None
        ])
        if self.state['view'] == 'workspace':
            self.showProjectList(self.state['id'])
        elif self.state['view'] == 'project':
            self.showProject(self.state['id'])
        elif self.state['view'] == 'atm':
            self.showMyTasks(self.state['id'])
        elif self.state['view'] == 'details':
            self.showDetails(self.state['id'])
        else:
            raise KeyError

        self.loop = urwid.MainLoop(self.frame,
                              unhandled_input=self.handleInput,
                              palette=ui.palette
                             )
        self.loop.run()

def main():
    cmdasana = CmdAsana()
    cmdasana.loadState()
    cmdasana.render()
    cmdasana.saveState()

if __name__ == "__main__": main()
