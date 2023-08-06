from flask import Flask, url_for
from unittest import TestCase
from flask.ext.router import Router

app = Flask(__name__)

class RouterTest(TestCase):
    """Test case class
    """

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        self.app = app.test_client()

    def tearDown(self):
        try:
            self.ctx.pop()
        except AssertionError:
            pass
        del self.ctx

    def test_router(self):
        router = Router(app, 'some_view')
        @router('/some_view/')
        def default():
            return 'default'

        @router('/some_view/', methods=['POST'])
        def post():
            return 'post'

        @router('/some_view/', methods=['PUT', 'DELETE'])
        def other():
            return 'other'

        @router('/some_view/<value>', methods=['GET'])
        def other_with_value(value):
            return value

        
        router = Router(app, 'other_view')
        @router('/other_view/', defaults={'value':'default_value'})
        @router('/other_view/<value>')
        def value(value):
            return value


        # Tests some_view
        self.assertEquals('default', self.app.get(url_for('some_view')).data)
        self.assertEquals('post', self.app.post(url_for('some_view')).data)
        self.assertEquals('other', self.app.put(url_for('some_view')).data)
        self.assertEquals('other', self.app.delete(url_for('some_view')).data)
        self.assertEquals('value', self.app.get(url_for('some_view',
            value='value')).data)

        # Tests other_view
        self.assertEquals('default_value',
            self.app.get(url_for('other_view')).data)
        self.assertEquals('value', self.app.get(url_for('other_view',
            value='value')).data)
