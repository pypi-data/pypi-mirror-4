import flask_heroku_runner

import unittest

import os
import random

import mock


def make_debug_envvar_testcase(debug_value, expected):
    """I create a test case for testing os.environ['DEBUG'] values."""
    @mock.patch('flask.Flask.run')
    def test_case(self, run_method):
        os.environ['DEBUG'] = debug_value.lower()
        app = flask_heroku_runner.HerokuApp(__name__)
        app.run(host='127.0.0.1', port=6543)
        run_method.assert_called_with(host='127.0.0.1', port=6543,
                debug=expected)
        
        os.environ['DEBUG'] = debug_value.upper()
        app = flask_heroku_runner.HerokuApp(__name__)
        app.run(host='127.0.0.1', port=6543)
        run_method.assert_called_with(host='127.0.0.1', port=6543,
                debug=expected)
        
        os.environ['DEBUG'] = debug_value.capitalize()
        app = flask_heroku_runner.HerokuApp(__name__)
        app.run(host='127.0.0.1', port=6543)
        run_method.assert_called_with(host='127.0.0.1', port=6543,
                debug=expected)
    return test_case
make_debug_envvar_testcase.__test__ = False


class HerokuEnvironmentTests(unittest.TestCase):
    initial_environ = dict()

    @classmethod
    def setUpClass(cls):
        """I stash off the starting value of ``os.environ`` in a class
        property so that we have a clean view of it for each test."""
        for k, v in os.environ.iteritems():
            cls.initial_environ[k] = v

    def setUp(self):
        """Replace ``os.environ`` with the view that was preserved when
        we started the test."""
        names = os.environ.keys()
        for n in names:
            del os.environ[n]
        for k, v in self.initial_environ.iteritems():
            os.environ[k] = v

    @mock.patch('flask.Flask.run')
    def test_that_app_uses_port_envvar(self, run_method):
        some_number = int(random.uniform(2048, 10000))
        os.environ['PORT'] = str(some_number)
        app = flask_heroku_runner.HerokuApp(__name__)
        app.run(host='127.0.0.1')
        run_method.assert_called_with(host='127.0.0.1', port=some_number)

    @mock.patch('flask.Flask.run')
    def test_that_app_uses_host_envvar(self, run_method):
        random_ip = '%d.%d.%d.%d' % (
            int(random.uniform(1, 254)),
            int(random.uniform(1, 254)),
            int(random.uniform(1, 254)),
            int(random.uniform(1, 254)))
        os.environ['HOST'] = random_ip
        app = flask_heroku_runner.HerokuApp(__name__)
        app.run(port=6543)
        run_method.assert_called_with(host=random_ip, port=6543)

    test_debug_envvar_yes = make_debug_envvar_testcase('yes', True)
    test_debug_envvar_true = make_debug_envvar_testcase('true', True)
    test_debug_envvar_1 = make_debug_envvar_testcase('1', True)
    test_debug_envvar_no = make_debug_envvar_testcase('no', False)
    test_debug_envvar_false = make_debug_envvar_testcase('false', False)
    test_debug_envvar_0 = make_debug_envvar_testcase('0', False)


def all_tests():
    return [HerokuEnvironmentTests()]

all_tests.__test__ = False

if __name__ == '__main__':
    unittest.main()


