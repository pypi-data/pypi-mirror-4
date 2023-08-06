# -*- coding: utf8 -*-
import unittest

class TestAccountView(unittest.TestCase):
    def setUp(self):
        from .helper import init_testing_env
        self.testapp = init_testing_env({
            'sqlalchemy.write.url': 'sqlite:///',
            'use_dummy_mailer': True
        })
        self.create_testuser()
        
    def tearDown(self):
        self.testapp.Session.remove()
        
    def create_testuser(self):
        import transaction
        from ..models.user import UserModel
        model = UserModel(self.testapp.session)
        with transaction.manager:
            model.create_user(
                user_name='tester', 
                display_name='tester', 
                password='testerpass', 
                email='tester@example.com'
            )
        
    def login_user(self, username_or_email='tester', password='testerpass'):
        """Login as user and return cookie
        
        """
        params = dict(
            username_or_email=username_or_email, 
            password=password
        )
        self.testapp.post('/login', params)
        
    def assert_login_success(self, name, password):
        """Assert login success
        
        """
        params = dict(
            username_or_email=name, 
            password=password
        )
        self.testapp.post('/login', params, status='3*')
        
    def assert_login_failed(self, name, password):
        """Assert login failed
        
        """
        params = dict(
            username_or_email=name, 
            password=password
        )
        self.testapp.post('/login', params, status=200)
        
    def test_login(self):
        self.testapp.get('/login', status=200)
        # test valid login
        self.assert_login_success('tester', 'testerpass')
        self.assert_login_success('TESTER', 'testerpass')
        self.assert_login_success('TeStEr', 'testerpass')
        self.assert_login_success('tester@example.com', 'testerpass')
        self.assert_login_success('TESTER@example.com', 'testerpass')
        self.assert_login_success('TESTER@Example.Com', 'testerpass')
        
    def test_login_fail(self):
        self.testapp.get('/login', status=200)
        
        with self.assertRaises(Exception):
            self.assert_login_failed('tester', 'testerpass')
        
        # test invalid login
        self.assert_login_failed('', '')
        self.assert_login_failed('tester', 'tester')
        self.assert_login_failed('tester', 'TESTERPASS')
        self.assert_login_failed('tester', 'TeStErPaSs')
        self.assert_login_failed('tester@example.com', 'tester')
        self.assert_login_failed('tester@example.com', 'TESTERPASS')
        self.assert_login_failed('tester@example.com', 'TeStErPaSs')
        self.assert_login_failed('tester', '')
        self.assert_login_failed('tester@example.com', '')
        self.assert_login_failed('abc', '123')
        self.assert_login_failed('not_exist@example.com', '123')
        self.assert_login_failed('not_exist@example.com', '')
        
    def test_logout(self):
        # try to logout when not logged in
        self.testapp.get('/logout', status=400)
        self.login_user('tester', 'testerpass')
        self.testapp.get('/logout', status='3*')
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAccountView))
    return suite
        
if __name__ == '__main__':
    unittest.main(defaultTest='suite')