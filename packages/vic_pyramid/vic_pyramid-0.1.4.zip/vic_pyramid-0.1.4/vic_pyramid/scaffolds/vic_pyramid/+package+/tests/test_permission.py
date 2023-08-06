import unittest

class TestPermissionModel(unittest.TestCase):
    
    def setUp(self):
        import datetime
        from .helper import create_session
        from ..models import tables
        tables.set_now_func(datetime.datetime.utcnow)
        self.session = create_session(zope_transaction=True)
        
    def tearDown(self):
        self.session.remove()
        
    def make_one(self):
        from ..models.permission import PermissionModel
        return PermissionModel(self.session)
    
    def test_create_permission(self):
        import transaction
        model = self.make_one()
        
        permission_name = 'test'
        description = permission_name
        
        with transaction.manager:
            permission_id = model.create_permission(
                permission_name=permission_name,
                description=description,
            )
        permission = model.get_permission_by_id(permission_id)
        
        self.assertEqual(permission.permission_name, permission_name)
        self.assertEqual(permission.description, description)
    
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPermissionModel))
    return suite
        
if __name__ == '__main__':
    unittest.main(defaultTest='suite')