#!/usr/bin/env python
# -*- coding: latin-1 -*-
import os
import sys
import json

import urwid
import asana
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

import ui
from secrets import CLIENT_ID, CLIENT_SECRET

class CmdAsana:
    def __init__(self):
        try:
            f = open(".oauth", "r")
            token = json.loads(f.readline())
            f.close()
            self.client = asana.Client.oauth(
                client_id=CLIENT_ID,
                token=token
            )
        except IOError:
            self.getToken()

        try:
            self.me = self.client.users.me()
        except TokenExpiredError:
            token = self.client.session.fetch_token(code=token['refresh_token'])
            f = open('.oauth', 'w')
            f.write(json.dumps(token))
            f.close()
            self.me = self.client.users.me()

    def getToken(self):
        self.client = asana.Client.oauth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        (url, state) = self.client.session.authorization_url()
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            print "Go to the following link and enter the code:"
            print url

        code = sys.stdin.readline().strip()
        token = self.client.session.fetch_token(code=code)
        f = open('.oauth', 'w')
        f.write(json.dumps(token))
        f.close()

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
    
    def addComment(self, task_id, comment):
        self.client.stories.create_on_task(task_id, {"text": comment})
        self.loadDetails(task_id)

    def replaceBody(self, widget):
        old_widget,_ = self.frame.contents.pop()
        if old_widget != None:
            self.clearSignals(old_widget)
        self.frame.contents.append((widget, self.frame.options()))
        self.frame.focus_position = 0

    def showWorkspace(self, workspace_id):
        task_list = ui.TaskList(self.allMyTasks(workspace_id))
        self.connectTaskListSignals(task_list)
        self.replaceBody(task_list)
        self.workspace_id = workspace_id

    def loadDetails(self, task_id):
        task = self.client.tasks.find_by_id(task_id)
        stories = self.client.stories.find_by_task(task_id)
        task_details = ui.TaskDetails(task, stories)
        urwid.connect_signal(task_details, 'comment', self.addComment)
        self.replaceBody(task_details)

    def refreshTaskList(self):
        self.showWorkspace(self.workspace_id)

    def registerSignals(self):
        urwid.register_signal(ui.TaskList, [
            'complete',
            'newtask',
            'updatetask',
            'details'
        ])
        urwid.register_signal(ui.TaskEdit, [
            'complete',
            'newtask',
            'updatetask',
            'details'
        ])

        urwid.register_signal(ui.TaskDetails, ['comment'])
        urwid.register_signal(ui.CommentEdit, ['comment'])

        urwid.register_signal(ui.WorkspaceMenu, 'click')

    def clearSignals(self, widget):
        urwid.disconnect_signal(widget, 'complete', self.completeTask)
        urwid.disconnect_signal(widget, 'newtask', self.newTask)
        urwid.disconnect_signal(widget, 'updatetask', self.updateTask)
        urwid.disconnect_signal(widget, 'details', self.loadDetails)

    def connectTaskListSignals(self, task_list):
        urwid.connect_signal(task_list, 'complete', self.completeTask)
        urwid.connect_signal(task_list, 'newtask', self.newTask)
        urwid.connect_signal(task_list, 'updatetask', self.updateTask)
        urwid.connect_signal(task_list, 'details', self.loadDetails)

    def handleInput(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def render(self):
        urwid.set_encoding("UTF-8")
        self.registerSignals()

        workspace_menu = ui.WorkspaceMenu(self.myWorkspaces())
        urwid.connect_signal(workspace_menu, 'click', self.showWorkspace)

        self.frame = urwid.Pile([
            ('pack', urwid.AttrMap(workspace_menu, 'workspace')),
            None
        ])
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
