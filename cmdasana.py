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
        
        f = open('.config', 'r')
        config = f.read()
        self.config = json.loads(config)
        f.close()

    def shouldShowWorkspace(self, workspace_id):
        try:
            return not (workspace_id in self.config['excluded_domains'])
        except KeyError:
            return True

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

    def newTask(self): pass
    
    def deleteTask(self): pass

    def showDetails(self, task_id): pass

    def replaceBody(self, widget):
        self.frame.contents.pop()
        self.frame.contents.append((widget, self.frame.options()))

    def showWorkspace(self, workspace_id):
        task_list = ui.TaskList(self.allMyTasks(workspace_id))
        urwid.connect_signal(task_list, 'complete', self.completeTask)
        self.replaceBody(task_list)

    def registerSignals(self):
        urwid.register_signal(ui.TaskList, 'complete')
        urwid.register_signal(ui.TaskEdit, 'complete')
        urwid.register_signal(ui.WorkspaceMenu, 'click')
         
    def handleInput(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def render(self):
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
