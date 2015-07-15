import os
import asana

ASANA_API_KEY = os.environ['ASANA_API_KEY']

client = asana.Client.basic_auth(ASANA_API_KEY)
me = client.users.me()

def allMyTasks():
    for workspace in me['workspaces']:
        tasks = client.tasks.find_all(params={
            'assignee': me['id'],
            'workspace': workspace['id'],
            'completed_since': 'now'
        })

        for task in tasks:
            print task['name']

allMyTasks()
