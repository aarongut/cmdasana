#!/usr/bin/env python
# -*- coding: latin-1 -*-
import os
import sys
import json

import urwid
import asana
from asana.session import AsanaOAuth2Session
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
                client_secret=CLIENT_SECRET,
                token=token,
                token_updater=self.saveToken,
                auto_refresh_url=AsanaOAuth2Session.token_url,
                auto_refresh_kwargs={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET
                },
            )
        except IOError:
            self.getToken()

        self.me = self.client.users.me()

    def saveToken(self, token):
        f = open('.oauth', 'w')
        f.write(json.dumps(token))
        f.close()

    def getToken(self):
        self.client = asana.Client.oauth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob',
            token_updater=self.saveToken,
            auto_refresh_url=AsanaOAuth2Session.token_url,
            auto_refresh_kwargs={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            },
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
        self.saveToken(token)

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

    def myWorkspaces(self):
        return self.me['workspaces']

    def allMyTasks(self, workspace_id):
        return self.client.tasks.find_all(params={
            'assignee': self.me['id'],
            'workspace': workspace_id,
            'completed_since': 'now'
        })

    def allMyProjects(self):
        return self.client.projects.find_by_workspace(self.workspace_id,
                                                     page_size=None)

    def projectTasks(self, project_id):
        return self.client.tasks.find_by_project(project_id, params={
            'completed_since': 'now'
        })

    def completeTask(self, task_id):
        self.client.tasks.update(task_id, completed=True)

    def newTask(self, task_after_id): 
        if self.state['view'] == 'project':
            task = self.client.tasks.create_in_workspace(
                self.state['workspace_id'],
                projects=[self.state['id']]
            )
            if task_after_id != None:
                self.client.tasks.add_project(task['id'],
                                              project=self.state['id'],
                                              insert_after=task_after_id)
        else:
            task = self.client.tasks.create_in_workspace(
                self.state['workspace_id'],
                assignee=self.me['id']
            )

        task_list,_ = self.frame.contents[1]
        task_list.insertNewTask(task)

    def updateTask(self, task_id, name):
        self.client.tasks.update(task_id, name=name)
    
    def addComment(self, task_id, comment):
        self.client.stories.create_on_task(task_id, {"text": comment})
        self.showDetails(task_id)

    def replaceBody(self, widget):
        old_widget,_ = self.frame.contents.pop()
        if old_widget != None:
            self.clearSignals(old_widget)
        self.frame.contents.append((widget, self.frame.options()))
        self.frame.focus_position = 0

    def showMyTasks(self, workspace_id):
        self.state['view'] = 'atm'
        self.state['id'] = workspace_id
        self.state['workspace_id'] = workspace_id

        task_list = ui.TaskList(self.allMyTasks(workspace_id))
        self.connectTaskListSignals(task_list)
        self.replaceBody(task_list)

    def showProject(self, project_id):
        self.state['view'] = 'project'
        self.state['id'] = project_id

        task_list = ui.TaskList(self.projectTasks(project_id))
        self.connectTaskListSignals(task_list)
        self.replaceBody(task_list)

    def showProjectList(self, workspace_id):
        self.state['view'] = 'workspace'
        self.state['id'] = workspace_id
        self.state['workspace_id'] = workspace_id

        self.workspace_id = workspace_id
        project_list = ui.ProjectList(self.allMyProjects())
        urwid.connect_signal(project_list, 'loadproject', self.showProject)
        self.replaceBody(project_list)

    def showDetails(self, task_id):
        self.state['view'] = 'details'
        self.state['id'] = task_id

        task = self.client.tasks.find_by_id(task_id)
        stories = self.client.stories.find_by_task(task_id)
        task_details = ui.TaskDetails(task, stories)
        urwid.connect_signal(task_details, 'comment', self.addComment)
        urwid.connect_signal(task_details, 'loadproject', self.showProject)
        self.replaceBody(task_details)

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

        urwid.register_signal(ui.TaskDetails, ['comment', 'loadproject'])
        urwid.register_signal(ui.CommentEdit, ['comment'])

        urwid.register_signal(ui.WorkspaceMenu, 'click')

        urwid.register_signal(ui.ProjectList, 'loadproject')

    def clearSignals(self, widget):
        urwid.disconnect_signal(widget, 'complete', self.completeTask)
        urwid.disconnect_signal(widget, 'newtask', self.newTask)
        urwid.disconnect_signal(widget, 'updatetask', self.updateTask)
        urwid.disconnect_signal(widget, 'details', self.showDetails)

    def connectTaskListSignals(self, task_list):
        urwid.connect_signal(task_list, 'complete', self.completeTask)
        urwid.connect_signal(task_list, 'newtask', self.newTask)
        urwid.connect_signal(task_list, 'updatetask', self.updateTask)
        urwid.connect_signal(task_list, 'details', self.showDetails)

    def handleInput(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def render(self):
        urwid.set_encoding("UTF-8")
        self.registerSignals()

        workspace_menu = ui.WorkspaceMenu(self.myWorkspaces())
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

        loop = urwid.MainLoop(self.frame,
                              unhandled_input=self.handleInput,
                              palette=ui.palette
                             )
        loop.run()

def main():
    cmdasana = CmdAsana()
    cmdasana.loadState()
    cmdasana.render()
    cmdasana.saveState()

if __name__ == "__main__": main()
