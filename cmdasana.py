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

    def allMyTasks(self):
        task_list = []
        for workspace in self.me['workspaces']:
            if not self.shouldShowWorkspace(workspace['id']):
                continue

            tasks = self.client.tasks.find_all(params={
                'assignee': self.me['id'],
                'workspace': workspace['id'],
                'completed_since': 'now'
            })

            task_list += tasks
        return task_list

    def completeTask(self, task_id):
        self.client.tasks.update(task_id, completed=True)

    def newTask(self): pass
    def deleteTask(self): pass

def handleInput(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

def showDetails(task_id): pass

def registerSignals():
    urwid.register_signal(ui.TaskList, 'complete')
    urwid.register_signal(ui.TaskEdit, 'complete')

def main():
    cmdasana = CmdAsana()
    registerSignals()

    task_list = ui.TaskList(cmdasana.allMyTasks())
    urwid.connect_signal(task_list, 'complete', cmdasana.completeTask)

    loop = urwid.MainLoop(task_list, unhandled_input=handleInput)
    loop.run()


if __name__ == "__main__": main()
