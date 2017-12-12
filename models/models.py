import dateutil
import sys

class AsanaObject(object):
    def __init__(self, object_dict):
        self.object_dict = object_dict

    def id(self):
        return self.object_dict['id']

    def name(self):
        if 'name' in self.object_dict:
            return self.object_dict['name']
        else:
            return ''

class User(AsanaObject):
    def workspaces(self):
        return [AsanaObject(w) for w in self.object_dict['workspaces']]

class Task(AsanaObject):
    def name(self):
        if self.object_dict['completed']:
            return '✓ %s' % super(Task, self).name()
        return super(Task, self).name()

    def assignee(self):
        if 'assignee' in self.object_dict:
            return User(self.object_dict['assignee'])
        else:
            return None

    def atm_section(self):
        return self.object_dict['assignee_status']

    def description(self):
        if 'notes' in self.object_dict:
            return self.object_dict['notes']
        else:
            return None

    def due_date(self):
        if 'due_at' in self.object_dict:
            return dateutil.parser.parse(self.object_dict['due_at'])
        elif 'due_one' in self.object_dict:
            return dateutil.parser.parse(self.object_dict['due_on'])
        else:
            return None

    def parent(self):
        if 'parent' in self.object_dict and self.object_dict['parent']:
            return Task(self.object_dict['parent'])
        else:
            return None

    def projects(self):
        if 'projects' in self.object_dict:
            return [Project(p) for p in self.object_dict['projects']]
        else:
            return []

    def subtasks(self):
        if 'subtasks' in self.object_dict:
            return [Task(t) for t in self.object_dict['subtasks']]
        else:
            return []

    def custom_fields(self):
        if 'custom_fields' in self.object_dict:
            return [CustomField(c) for c in self.object_dict['custom_fields']]
        else:
            return []
class Project(AsanaObject):
    def description(self):
        if 'notes' in self.object_dict:
            return self.object_dict['notes']
        else:
            return ''

class CustomField(AsanaObject):
    def string_value(self):
        if 'text_value' in self.object_dict:
            return str(self.object_dict['text_value'])
        elif 'number_value' in self.object_dict:
            return str(self.object_dict['number_value'])
        elif 'enum_value' in self.object_dict and self.object_dict['enum_value']:
            enum_value = AsanaObject(self.object_dict['enum_value'])
            return str(enum_value.name())

        return ''

class Story(AsanaObject):
    def creator(self):
        if 'created_by' in self.object_dict:
            return  self.object_dict['created_by']['name'] + ' '
        else:
            return ''

    def text(self):
        return self.object_dict['text']
