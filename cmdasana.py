#!/usr/bin/env python
# -*- coding: latin-1 -*-
import os
import json

import urwid
import asana

import ui

class CmdAsana:
    ASANA_API_KEY = os.environ['ASANA_API_KEY']

    def __init__(self):
        self.client = asana.Client.basic_auth(self.ASANA_API_KEY)
        self.me = self.client.users.me()

    def myWorkspaces(self):
        return self.me['workspaces']

    def allMyTasks(self, workspace_id):
        return self.client.tasks.find_all(params={
            'assignee': self.me['id'],
            'workspace': workspace_id,
            'completed_since': 'now'
        })

    def completeTask(self, task_id):
        self.client.tasks.update(task_id, completed=True)

    def newTask(self): 
        task = self.client.tasks.create_in_workspace(self.workspace_id,
                                                     assignee=self.me['id'])
        task_list,_ = self.frame.contents[1]
        task_list.insertNewTask(task)

    def updateTask(self, task_id, name):
        self.client.tasks.update(task_id, name=name)

    def showDetails(self, task_id): pass

    def replaceBody(self, widget):
        old_widget,_ = self.frame.contents.pop()
        if old_widget != None:
            self.clearSignals(old_widget)
        self.frame.contents.append((widget, self.frame.options()))

    def showWorkspace(self, workspace_id):
        task_list = ui.TaskList(self.allMyTasks(workspace_id))
        self.connectTaskListSignals(task_list)
        self.replaceBody(task_list)
        self.workspace_id = workspace_id

    def refreshTaskList(self):
        self.showWorkspace(self.workspace_id)

    def registerSignals(self):
        urwid.register_signal(ui.TaskList,
                              ['complete',
                               'newtask',
                               'updatetask'])
        urwid.register_signal(ui.TaskEdit,
                              ['complete',
                               'newtask',
                               'updatetask'])
        urwid.register_signal(ui.WorkspaceMenu, 'click')

    def clearSignals(self, widget):
        urwid.disconnect_signal(widget, 'complete', self.completeTask)
        urwid.disconnect_signal(widget, 'newtask', self.newTask)
        urwid.disconnect_signal(widget, 'updatetask', self.updateTask)

    def connectTaskListSignals(self, task_list):
        urwid.connect_signal(task_list, 'complete', self.completeTask)
        urwid.connect_signal(task_list, 'newtask', self.newTask)
        urwid.connect_signal(task_list, 'updatetask', self.updateTask)

    def handleInput(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def render(self):
        urwid.set_encoding("UTF-8")
        self.registerSignals()

        workspace_menu = ui.WorkspaceMenu(self.myWorkspaces())
        urwid.connect_signal(workspace_menu, 'click', self.showWorkspace)

        self.frame = urwid.Pile([('pack', workspace_menu), None])
        self.showWorkspace(self.myWorkspaces()[0]['id'])

        loop = urwid.MainLoop(self.frame,
                              unhandled_input=self.handleInput,
                              palette=ui.palette
                             )
        loop.run()

def main():
    cmdasana = CmdAsana()
    cmdasana.render()

if __name__ == "__main__": main()
