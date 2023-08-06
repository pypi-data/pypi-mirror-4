try:
    import unittest2 as unittest
except ImportError:
    import unittest

import mock

from flask import Flask
from flask.ext.simon import Simon, get_or_404
from pymongo.errors import InvalidURI
from simon.exceptions import MultipleDocumentsFound, NoDocumentFound
from werkzeug.exceptions import NotFound


class TestSimon(unittest.TestCase):
    def setUp(self):
        self.app = Flask('test')
        self.context = self.app.test_request_context('/')
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def test_init(self):
        """Test the `__init__()` method."""

        with mock.patch.object(Simon, 'init_app') as init_app:
            # Simon.init_app() should not be called
            Simon()

            self.assertFalse(init_app.called)

        with mock.patch.object(Simon, 'init_app') as init_app:
            # Simon.init_app() should be called with self.app
            Simon(self.app)

            init_app.assert_called_with(self.app)

    def test_init_app(self):
        """Test the `init_app()` method."""

        simon = Simon()
        with mock.patch('simon.connection.connect') as connect:
            simon.init_app(self.app)

            connect.assert_called_with(host='localhost', name='test')

    def test_init_app_invaliduri(self):
        """Test that `init_app()` raises `InvalidURI`."""

        url = 'http://example.com'
        self.app.config['MONGO_URI'] = url

        simon = Simon()
        with self.assertRaises(InvalidURI):
            simon.init_app(self.app)

    def test_init_app_uri(self):
        """Test the `init_app()` method with `MONGO_URI`."""

        url = 'mongodb://simonu:simonp@localhost:27017/test-simon'
        self.app.config['MONGO_URI'] = url

        simon = Simon()
        with mock.patch('simon.connection.connect') as connect:
            simon.init_app(self.app)

            connect.assert_called_with(host_or_uri=url, name='test-simon',
                                       username='simonu', password='simonp',
                                       replica_set=None)

    def test_init_app_valueerror(self):
        """Test that `init_app()` raises `ValueError`."""

        url = 'mongodb://simonu:simonp@localhost:27017/'
        self.app.config['MONGO_URI'] = url

        simon = Simon()
        with self.assertRaises(ValueError):
            simon.init_app(self.app)


class TestMiscellaneous(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.context = self.app.test_request_context('/')
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def test_get_or_404(self):
        """Test the `get_or_404()` method."""

        expected = {'a': 1}

        Model = mock.Mock()
        Model.get.return_value = expected

        actual = get_or_404(Model, a=1)
        self.assertEqual(actual, expected)

    def test_get_or_404_abort_multiple(self):
        ("Test that `get_or_404()` calls `abort()` with "
         "`MultipleDocumentsFound`.")

        Model = mock.Mock()
        Model.MultipleDocumentsFound = MultipleDocumentsFound
        Model.get.side_effect = Model.MultipleDocumentsFound

        with self.assertRaises(NotFound):
            get_or_404(Model, a=1)

    def test_get_or_404_abort_none(self):
        ("Test that `get_or_404()` calls `abort()` with "
         "`NoDocumentFound`.")

        Model = mock.Mock()
        Model.NoDocumentFound = NoDocumentFound
        Model.get.side_effect = Model.NoDocumentFound

        with self.assertRaises(NotFound):
            get_or_404(Model, a=1)
