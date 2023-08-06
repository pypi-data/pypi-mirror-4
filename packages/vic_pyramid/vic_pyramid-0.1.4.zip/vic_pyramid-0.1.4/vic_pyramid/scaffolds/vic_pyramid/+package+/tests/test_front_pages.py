import unittest

class TestFrontPagesView(unittest.TestCase):
    def setUp(self):
        from .helper import init_testing_env
        self.testapp = init_testing_env({
            'sqlalchemy.write.url': 'sqlite:///',
            'use_dummy_mailer': True
        })
        
    def tearDown(self):
        self.testapp.Session.remove()
        
    def test_home(self):
        self.testapp.get('/', status=200)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFrontPagesView))
    return suite
        
if __name__ == '__main__':
    unittest.main(defaultTest='suite')