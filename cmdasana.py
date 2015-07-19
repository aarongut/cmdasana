import os
import asana
import json

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
        for workspace in self.me['workspaces']:
            if not self.shouldShowWorkspace(workspace['id']):
                continue

            print "*" * 80
            print workspace['id'], ': ', workspace['name'], " Tasks"
            print "*" * 80, "\n"

            tasks = self.client.tasks.find_all(params={
                'assignee': self.me['id'],
                'workspace': workspace['id'],
                'completed_since': 'now'
            })

            for task in tasks:
                print task['name']

def main():
    cmdasana = CmdAsana()

    cmdasana.allMyTasks()

if __name__ == "__main__": main()
