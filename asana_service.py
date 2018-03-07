from models.models import *

class AsanaService(object):
    TASK_FIELDS = [
        'name',
        'html_notes',
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
        'subtasks.completed',
        'subtasks.name',
    ]

    STORY_FIELDS = [
        'created_by.name',
        'html_text',
        'text',
        'type'
    ]

    def __init__(self, client):
        self.client = client
        self.completed_tasks = False
        self.me = User(client.users.me())
        self.workspace = self.me.workspaces()[0]

    def __wrap__(self, Klass, values):
        return map(Klass, values)

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

    def get_project(self, project_id):
        return Project(
            self.client.projects.find_by_id(project_id)
        )

    def get_task(self, task_id):
        return Task(self.client.tasks.find_by_id(
            task_id,
            params={
                'opt_fields': self.TASK_FIELDS
            }
        ))

    def get_tasks(self, project_id):
        params = {
            'completed_since': '' if self.completed_tasks else 'now',
            'opt_fields': self.TASK_FIELDS,
        }

        return self.__wrap__(
            Task,
            self.client.tasks.find_by_project(project_id, params=params)
        )
    
    def get_stories(self, task_id):
        stories = self.client.stories.find_by_task(task_id, params = {
            'opt_fields': self.STORY_FIELDS
        })
        filtered_stories = filter(lambda s: s['type'] == 'comment', stories)
        return self.__wrap__(Story, filtered_stories)
