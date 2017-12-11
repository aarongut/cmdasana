from models.models import *

class AsanaService(object):
    TASK_FIELDS = [
        'name',
        'notes',
        'assignee.name',
        'assignee_status',
        'completed',
        'due_on',
        'due_at',
        'projects.name',
        'parent.completed',
        'parent.name',
        'memberships.section.name',
        'memberships.project.name',
        'custom_fields.name',
        'custom_fields.type',
        'custom_fields.text_value',
        'custom_fields.number_value',
        'custom_fields.enum_value.name',
    ]

    def __init__(self, client):
        self.client = client
        self.completed_tasks = False
        self.me = User(client.users.me())
        self.workspace = self.me.workspaces()[0]

    def __wrap__(self, Klass, values):
        return map(Klass, values)

    def get_tasks(self, project_id):
        params = {
            'completed_since': '' if self.completed_tasks else 'now',
            'opt_fields': self.TASK_FIELDS,
        }

        return self.__wrap__(
            Task,
            self.client.tasks.find_by_project(project_id, params=params)
        )

    def get_my_tasks(self):
        return self.__wrap__(
            Task,
            self.client.tasks.find_all(params = {
                'completed_since': '' if self.completed_tasks else 'now',
                'opt_fields': self.TASK_FIELDS,
                'assignee': self.me.id(),
                'workspace': self.workspace.id()
            })
        )

    def get_task(self, task_id):
        return Task(self.client.tasks.find_by_id(
            task_id,
            params={
                'opt_fields': self.TASK_FIELDS
            }
        ))
    
    def get_stories(self, task_id):
        return self.__wrap__(Story,
                             self.client.stories.find_by_task(task_id)
                            )
