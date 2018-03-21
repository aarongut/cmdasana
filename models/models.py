import dateutil
from html.parser import HTMLParser
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
        if 'html_notes' in self.object_dict:
            parser = HTMLTextParser()
            parser.feed(self.object_dict['html_notes'])
            parser.close()
            text = parser.get_formatted_text()
            if (len(text) > 0):
                return text
            else:
                return ""
        elif 'notes' in self.object_dict:
            return self.object_dict['notes']
        else:
            return ""

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

class Strong(object):
    def __init__(self, body):
        self.body = body

    def text_format(self):
        return ('strong', self.body.text_format())

class Italic(object):
    def __init__(self, body):
        self.body = body

    def text_format(self):
        return ('italic', self.body.text_format())

class Underline(object):
    def __init__(self, body):
        self.body = body

    def text_format(self):
        return ('underline', self.body.text_format())

class Link(object):
    def __init__(self, body):
        self.body = body

    def text_format(self):
        return ('link', self.body.text_format())

class Tag(object):
    def __init__(self, body):
        self.body = body

    def text_format(self):
        return self.body.text_format()

class List(object):
    def __init__(self, body):
        self.body = body

    def text_format(self):
        return self.body.text_format()

class ListItem(object):
    def __init__(self, body, indent):
        self.body = body
        self.indent = indent

    def text_format(self):
        return ('', [(' ' * self.indent), '• ', self.body.text_format(), '\n'])

class Text(object):
    def __init__(self, body):
        self.body = body

    def text_format(self):
        return self.body

class HTMLTextParser(HTMLParser):
    def __init__(self):
        self.text = []
        self.tag_stack = []
        self.indent = 0
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag == 'strong':
            self.tag_stack.append(Strong)
        elif tag == 'em':
            self.tag_stack.append(Italic)
        elif tag == 'u':
            self.tag_stack.append(Underline)
        elif tag == 'a':
            self.tag_stack.append(Link)
        elif tag == 'ul' or tag == 'ol':
            self.indent += 2
            self.tag_stack.append(List)
        elif tag == 'li':
            self.tag_stack.append(ListItem)
        else:
            self.tag_stack.append(Tag)

    def handle_data(self, data):
        self.text.append(Text(data))

    def handle_endtag(self, tag):
        data = self.text.pop()
        Class = self.tag_stack.pop()

        if tag == 'ul' or tag =='ol':
            self.indent -= 2

        if tag == 'li':
            self.text.append(Class(data, self.indent))
        else:
            self.text.append(Class(data))

    def get_formatted_text(self):
        formatted = [t.text_format() for t in self.text]
        return formatted


class Story(AsanaObject):
    def creator(self):
        if 'created_by' in self.object_dict:
            return  self.object_dict['created_by']['name'] + ' '
        else:
            return ''

    def text(self):
        if 'html_text' in self.object_dict:
            parser = HTMLTextParser()
            parser.feed(self.object_dict['html_text'])
            parser.close()
            return parser.get_formatted_text()
        else:
            return [self.object_dict['text']]
