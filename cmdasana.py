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

def handleInput(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

def main():
    cmdasana = CmdAsana()
    task_list = cmdasana.allMyTasks()
    
    loop = urwid.MainLoop(ui.TaskList(task_list), unhandled_input=handleInput)
    loop.run()


if __name__ == "__main__": main()
