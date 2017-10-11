import asana

# id of the personal projects domain
PERSONAL = 498346170860

class Data:
    def __init__(self, client):
        self.client = client
        self.me = self.client.users.me()

    def me(self):
        return self.me

    def myWorkspaces(self):
        return self.me['workspaces']

    def myTasks(self, workspace_id):
        return self.client.tasks.find_all(params={
            'assignee': self.me['id'],
            'workspace': workspace_id,
            'completed_since': 'now'
        })

    def allMyProjects(self):
        if self.workspace_id != PERSONAL:
            return self.client.projects.find_by_workspace(self.workspace_id)
        else:
            return self.client.projects.find_by_workspace(self.workspace_id,
                                                         page_size=None)

    def tasksInProject(self, project_id):
        return self.client.tasks.find_by_project(project_id, params={
            'completed_since': 'now'
        })

    def getTask(self, task_id):
        task = self.client.tasks.find_by_id(task_id, params={
            'opt_fields': ['name',
                           'assignee.name',
                           'due_date',
                           'notes',
                           'parent',
                           'projects.name',
                           'subtasks.name'
                          ]
        })

        stories = self.client.stories.find_by_task(task_id)
        return (task, stories, task['subtasks'])

    def completeTask(self, task_id):
        self.client.tasks.update(task_id, completed=True)

    def createTask(self, workspace, opt_projects=[], opt_after=None,
                   opt_assignee=None, opt_name=None):
        task = self.client.tasks.create_in_workspace(workspace,
                                                     projects=opt_projects,
                                                     assignee=opt_assignee,
                                                     name=opt_name)
        if opt_after and len(opt_projects) > 0:
            self.client.tasks.add_project(task['id'],
                                          project=opt_projects[0],
                                          insert_after=opt_after)

        return task

    def updateTask(self, task_id, opt_name=None, opt_projects=None,
                   opt_assignee=None, opt_notes=None):
        return self.client.tasks.update(task_id,
                                        name=opt_name,
                                        projects=opt_projects,
                                        assignee=opt_assignee,
                                        notes=opt_notes)

    def addComment(self, task_id, comment):
        return self.client.stories.create_on_task(task_id, {"text": comment})

    def _typeahead(self, workspace, asana_type, query, count=5):
        return self.client.workspaces.typeahead(workspace, {
            'type': asana_type,
            'query': query,
            'count': count
        })

    def userTypeahead(self, workspace, query, count):
        return self._typeahead(workspace, 'user', query, count)

    def projectTypeahead(self, workspace, query, opt_count):
        return self._typeahead(workspace, 'project', query, count=opt_count)
