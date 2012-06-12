# Standard library
import datetime
import json
import unittest

# Imports from dictshield proper
from dictshield.document import Document
from dictshield.fields import StringField, DateTimeField

# Imports from our package
from dictshield.views import WhitelistView


class Post(Document):
    name = StringField()
    body = StringField()
    username = StringField()
    password = StringField()
    created_time = DateTimeField()


class Public(WhitelistView):
    fields = ['name', 'body', 'to_json']


class DictViewTests(unittest.TestCase):

    entry = Post(name='Some clever post name',
                 body='blah blah blah',
                 username='marca',
                 password='password',
                 created_time=datetime.datetime.now())

    def setUp(self):
        self.entry_view = Public(self.entry)

    def test_has_name(self):
        self.assertEquals(self.entry_view.name, 'Some clever post name')

    def test_doesnt_have_password(self):
        try:
            self.entry_view.password
            self.fail()
        except AttributeError:
            pass

    def test_to_json(self):
        json_text = self.entry_view.to_json()
        a_dict = json.loads(json_text)
        self.assertEquals(a_dict['name'], 'Some clever post name')
        self.assertEquals(a_dict['body'], 'blah blah blah')

        try:
            a_dict['password']
            self.fail()
        except KeyError:
            pass
